"""Stacking Capital credit optimization engine.

Computes:
1. Statement close / reporting date vs due date pay-by recommendations per revolving tradeline.
2. Overall and per-card utilization bands (0%, 1-9%, 10-20% benchmark, 21-29% watch, 30%+ blocker)
   with FICO treatment & AZEO (All Zero Except One) paydown plan.
3. 6-month inquiry & new-account readiness (<= 2 hard inquiries per bureau in 6 months),
   plus inquiry-to-account dispute safety (never dispute an inquiry tied to an open account).
4. Optional DTI check (40% cap from reported monthly payments) and score-band context
   (780+ BEST / 750+ BETTER / 700+ MIN) when user provides income/FICO score locally.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from .models import BUREAUS, BUREAU_LABELS, norm_creditor


UTIL_BANDS = [
    {
        "id": "zero",
        "range": "0%",
        "label": "All Zero (0%)",
        "tone": "info",
        "fico_note": (
            "Reporting 0% across every revolving card can trigger a minor FICO 'all-zero' "
            "penalty (~10-20 pts). Keep exactly ONE non-HELOC personal card reporting 1-9% (AZEO)."
        ),
    },
    {
        "id": "azeo_prime",
        "range": "1-9%",
        "label": "AZEO / Prime (1-9%)",
        "tone": "success",
        "fico_note": (
            "Optimal FICO scoring band. Under AZEO (All Zero Except One), one unsecured personal "
            "card reports 1-9% (ideally 1-3% / small balance) while all other personal cards report $0."
        ),
    },
    {
        "id": "benchmark",
        "range": "10-20%",
        "label": "Stacking Benchmark (10-20%)",
        "tone": "success",
        "fico_note": (
            "Meets Stacking Capital's <=20% overall and <=20% per-card readiness benchmark. "
            "Paying down to 1-9% (AZEO) before applications unlocks extra score upside."
        ),
    },
    {
        "id": "ceiling_watch",
        "range": "21-29%",
        "label": "Above Benchmark (21-29%)",
        "tone": "warning",
        "fico_note": (
            "Below the 30% bare ceiling but ABOVE Stacking Capital's <=20% benchmark. "
            "Requires an explicit paydown before funding applications."
        ),
    },
    {
        "id": "blocker",
        "range": "30%+",
        "label": "High Utilization Blocker (30%+)",
        "tone": "danger",
        "fico_note": (
            "High FICO utilization penalty and Round 1 funding blocker. Prioritize paying down "
            "below 20% per card (and <=20% overall) before applying, and keep balances down."
        ),
    },
]


def classify_utilization_band(pct: float, balance_cents: int = 0) -> dict[str, Any]:
    if balance_cents <= 0 or pct <= 0.0:
        return UTIL_BANDS[0]
    if pct <= 9.4:
        return UTIL_BANDS[1]
    if pct <= 20.0:
        return UTIL_BANDS[2]
    if pct <= 29.9:
        return UTIL_BANDS[3]
    return UTIL_BANDS[4]


def _parse_iso_date(raw: str | None) -> date | None:
    if not raw:
        return None
    s = raw.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m"):
        try:
            dt = datetime.strptime(s, fmt).date()
            return dt
        except ValueError:
            continue
    return None


def _next_occurrence_of_day(day: int, ref: date) -> date:
    """Return the next calendar date matching day-of-month (clamped to month length)."""
    import calendar

    year, month = ref.year, ref.month
    last_day = calendar.monthrange(year, month)[1]
    candidate = date(year, month, min(day, last_day))
    if candidate < ref:
        month += 1
        if month > 12:
            month = 1
            year += 1
        last_day = calendar.monthrange(year, month)[1]
        candidate = date(year, month, min(day, last_day))
    return candidate


def _is_au_or_heloc_or_charge(acct: dict[str, Any]) -> tuple[bool, bool, bool]:
    resp = (acct.get("responsibility") or "").lower()
    is_au = "authorized" in resp or resp == "au"
    text = f"{acct.get('creditor', '')} {acct.get('account_type', '')} {acct.get('loan_type', '')}".lower()
    is_heloc = bool(re.search(r"\bheloc\b|home equity line", text))
    is_charge = acct.get("kind") == "revolving" and not (acct.get("credit_limit_cents") or 0)
    return is_au, is_heloc, is_charge


def build_pay_by_recommendations(
    snapshot: dict[str, Any],
    card_due_days: dict[str, int] | None = None,
    as_of_date: date | None = None,
) -> list[dict[str, Any]]:
    """Detect statement-close/reporting date per revolving card and build pay-by guidance."""
    ref = as_of_date or date.today()
    due_map = {k.lower(): v for k, v in (card_due_days or {}).items()}
    seen: dict[str, dict[str, Any]] = {}

    for b_key in BUREAUS:
        rep = snapshot.get("bureaus", {}).get(b_key)
        if not rep:
            continue
        for acct in rep.get("accounts", []):
            if acct.get("kind") != "revolving" or not acct.get("is_open"):
                continue
            is_au, is_heloc, is_charge = _is_au_or_heloc_or_charge(acct)
            if is_au or is_charge:
                continue

            key = f"{norm_creditor(acct.get('creditor'))}:{acct.get('account_number_masked', '****')[-4:]}"
            updated_dt = _parse_iso_date(acct.get("updated"))
            bal = acct.get("balance_cents") or 0
            lim = acct.get("credit_limit_cents") or 0
            util_pct = round((bal / lim) * 100, 1) if lim > 0 else 0.0

            existing = seen.get(key)
            # Keep record with most recent updated date or higher balance
            if existing is not None and existing.get("_updated_dt") and updated_dt:
                if updated_dt < existing["_updated_dt"]:
                    continue

            report_day = updated_dt.day if updated_dt else None
            # Optional user-supplied due day by creditor or masked last4; otherwise note typical ~25-day lag
            cred_low = acct.get("creditor", "").lower()
            last4 = acct.get("account_number_masked", "")[-4:]
            due_day = due_map.get(last4) or due_map.get(cred_low)

            if report_day:
                next_report = _next_occurrence_of_day(report_day, ref)
                pay_by = next_report - timedelta(days=3)
                if pay_by < ref:
                    # Roll to following cycle if within 3-day window already passed
                    next_cycle = _next_occurrence_of_day(report_day, next_report + timedelta(days=1))
                    next_report = next_cycle
                    pay_by = next_report - timedelta(days=3)
                pay_by_str = pay_by.isoformat()
                report_date_str = next_report.isoformat()
                timing_basis = f"Observed bureau report/statement close on day {report_day}"
            else:
                pay_by_str = "3 days before statement close"
                report_date_str = "Unknown (no Date Updated)"
                timing_basis = "Check issuer statement closing date"

            if due_day:
                next_due = _next_occurrence_of_day(due_day, ref)
                due_str = next_due.isoformat()
            elif report_day:
                # Typical US CARD Act rule: due date is >=21 days after close (~25 days), ~3-6 days before next close
                est_due = _next_occurrence_of_day(max(1, (report_day - 4) % 28 or 28), ref)
                due_str = f"~{est_due.isoformat()} (est.; confirm issuer due date)"
            else:
                due_str = "Check issuer statement"

            band = classify_utilization_band(util_pct, bal)
            target_9_cents = int(lim * 0.09)
            target_20_cents = int(lim * 0.20)
            paydown_to_9 = max(0, bal - target_9_cents)
            paydown_to_20 = max(0, bal - target_20_cents)

            if bal > target_20_cents:
                action = (
                    f"Pay at least ${paydown_to_20/100:,.0f} by {pay_by_str} to reach <=20% benchmark "
                    f"(or ${paydown_to_9/100:,.0f} to hit 1-9% prime); always pay minimum by due date ({due_str}) to avoid lates."
                )
            elif bal > target_9_cents:
                action = (
                    f"Within <=20% benchmark. For AZEO prime (<9%), pay ${paydown_to_9/100:,.0f} by {pay_by_str}; "
                    f"pay at least minimum by due date ({due_str})."
                )
            elif bal > 0:
                action = (
                    f"In 1-9% prime band. Pay by due date ({due_str}) to avoid late marks; "
                    f"for AZEO, keep this as your 1 small reporting balance or zero by {pay_by_str}."
                )
            else:
                action = f"Reporting $0 (AZEO-ready). Pay any new charges by {pay_by_str} before statement close."

            seen[key] = {
                "creditor": acct.get("creditor", ""),
                "account_masked": acct.get("account_number_masked", "****"),
                "is_heloc": is_heloc,
                "balance_cents": bal,
                "credit_limit_cents": lim,
                "utilization_pct": util_pct,
                "band": band,
                "observed_report_day": report_day,
                "next_report_date": report_date_str,
                "recommended_pay_by_date": pay_by_str,
                "due_date_note": due_str,
                "timing_basis": timing_basis,
                "paydown_to_20_cents": paydown_to_20,
                "paydown_to_9_cents": paydown_to_9,
                "recommendation": action,
                "_updated_dt": updated_dt,
            }

    results = list(seen.values())
    for item in results:
        item.pop("_updated_dt", None)
    results.sort(key=lambda r: r["utilization_pct"], reverse=True)
    return results


def build_azeo_plan(cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Build an All Zero Except One (AZEO) paydown plan on unsecured personal cards."""
    personal_unsecured = [c for c in cards if not c["is_heloc"]]
    helocs = [c for c in cards if c["is_heloc"] and c["balance_cents"] > 0]

    if not personal_unsecured:
        return {
            "strategy": "AZEO (All Zero Except One)",
            "eligible_cards": 0,
            "keep_balance_card": None,
            "zero_cards": [],
            "explanation": "No open unsecured personal revolving cards detected.",
        }

    # If a HELOC already carries a balance, AZEO says zero all unsecured cards
    if helocs:
        return {
            "strategy": "AZEO (HELOC carries balance -> zero all unsecured cards)",
            "eligible_cards": len(personal_unsecured),
            "keep_balance_card": None,
            "zero_cards": [f"{c['creditor']} ({c['account_masked']})" for c in personal_unsecured],
            "explanation": (
                "An open HELOC carries a balance. Per Stacking Capital AZEO rules, leave the HELOC "
                "separate and pay ALL unsecured personal credit cards to $0 before their statement close dates."
            ),
        }

    # Choose the largest-limit open card (lowest utilization impact for small balance) as the 1 card to leave 1-9%
    anchor = max(personal_unsecured, key=lambda c: c["credit_limit_cents"])
    others = [c for c in personal_unsecured if c is not anchor]
    suggested_small_bal_cents = min(max(1000, int(anchor["credit_limit_cents"] * 0.02)), int(anchor["credit_limit_cents"] * 0.09))

    return {
        "strategy": "AZEO (All Zero Except One)",
        "eligible_cards": len(personal_unsecured),
        "keep_balance_card": {
            "creditor": anchor["creditor"],
            "account_masked": anchor["account_masked"],
            "target_balance_cents": suggested_small_bal_cents,
            "pay_by_date": anchor["recommended_pay_by_date"],
        },
        "zero_cards": [
            {
                "creditor": c["creditor"],
                "account_masked": c["account_masked"],
                "current_balance_cents": c["balance_cents"],
                "pay_by_date": c["recommended_pay_by_date"],
            }
            for c in others
        ],
        "explanation": (
            f"Keep {anchor['creditor']} ({anchor['account_masked']}) reporting a small 1-3% balance "
            f"(~${suggested_small_bal_cents/100:,.0f}) by {anchor['recommended_pay_by_date']}, and pay all "
            f"other {len(others)} card(s) to $0 before their statement close/reporting dates. "
            "Always pay by each card's due date to avoid late fees or 30-day lates."
        ),
    }


def analyze_inquiries_and_readiness(
    snapshot: dict[str, Any],
    as_of_date: date | None = None,
    monthly_income_cents: int | None = None,
    self_reported_fico: int | None = None,
) -> dict[str, Any]:
    """Evaluate 6-month inquiry caps (max 2/bureau), inquiry-to-account dispute safety, and DTI."""
    ref = as_of_date or date.today()
    cutoff_6m = ref - timedelta(days=183)
    cutoff_24m = ref - timedelta(days=730)

    bureau_inq_status: dict[str, Any] = {}
    dispute_safety: list[dict[str, Any]] = []
    total_monthly_payments_cents = 0
    counted_payment_keys: set[str] = set()
    recent_new_accounts_6m: set[str] = set()

    for b_key in BUREAUS:
        rep = snapshot.get("bureaus", {}).get(b_key)
        if not rep:
            continue
        accounts = rep.get("accounts", [])
        for a in accounts:
            pkey = f"{norm_creditor(a.get('creditor'))}:{a.get('account_number_masked', '')[-4:]}"
            if pkey not in counted_payment_keys and a.get("is_open") and (a.get("monthly_payment_cents") or 0) > 0:
                counted_payment_keys.add(pkey)
                total_monthly_payments_cents += a["monthly_payment_cents"]
            odt = _parse_iso_date(a.get("opened"))
            if odt and odt >= cutoff_6m:
                recent_new_accounts_6m.add(pkey)

        hard_6m = 0
        hard_24m = 0
        for iq in rep.get("inquiries", []):
            if iq.get("kind") != "hard":
                continue
            iq_dt = _parse_iso_date(iq.get("date"))
            if iq_dt is None or iq_dt >= cutoff_24m:
                hard_24m += 1
            if iq_dt and iq_dt >= cutoff_6m:
                hard_6m += 1

            # Inquiry-to-account fuzzy link for dispute safety
            iq_norm = norm_creditor(iq.get("creditor"))
            linked_open = False
            linked_closed = False
            for a in accounts:
                a_norm = norm_creditor(a.get("creditor"))
                if iq_norm and a_norm and (iq_norm in a_norm or a_norm in iq_norm):
                    if a.get("is_open"):
                        linked_open = True
                    else:
                        linked_closed = True

            if iq_dt and iq_dt < cutoff_24m:
                safety = "aging_off"
                note = "24+ months old; will drop naturally."
            elif linked_open:
                safety = "do_not_dispute"
                note = "Linked to an OPEN account — do NOT dispute (can trigger account closure)."
            elif linked_closed:
                safety = "safe_closed_link"
                note = "Linked to a closed account; reviewable."
            else:
                safety = "safe_orphan"
                note = "No matching open tradeline (orphan/denied app); safe to review."

            dispute_safety.append(
                {
                    "bureau": BUREAU_LABELS[b_key],
                    "creditor": iq.get("creditor", ""),
                    "date": iq.get("date", ""),
                    "safety": safety,
                    "note": note,
                }
            )

        bureau_inq_status[b_key] = {
            "label": BUREAU_LABELS[b_key],
            "hard_6m": hard_6m,
            "hard_24m": hard_24m,
            "cap_6m": 2,
            "within_cap": hard_6m <= 2,
            "status": "Clean (0-1)" if hard_6m <= 1 else ("At Cap (2)" if hard_6m == 2 else "Over Cap (>2)"),
        }

    dti = None
    if monthly_income_cents and monthly_income_cents > 0:
        dti_pct = round((total_monthly_payments_cents / monthly_income_cents) * 100, 1)
        dti = {
            "monthly_debt_cents": total_monthly_payments_cents,
            "monthly_income_cents": monthly_income_cents,
            "dti_pct": dti_pct,
            "cap_pct": 40.0,
            "within_cap": dti_pct <= 40.0,
        }

    score_band = None
    if self_reported_fico and 300 <= self_reported_fico <= 850:
        if self_reported_fico >= 780:
            tier = "780+ BEST (0% Business Funding Tier)"
        elif self_reported_fico >= 750:
            tier = "750+ BETTER (Strong 0% Readiness)"
        elif self_reported_fico >= 720:
            tier = "720+ PERSONAL TARGET (Min 700+ Biz)"
        elif self_reported_fico >= 700:
            tier = "700+ MIN (Qualifies, below 750+ ideal)"
        else:
            tier = "BELOW 700 MIN (Focus on utilization & repair first)"
        score_band = {"fico": self_reported_fico, "tier": tier}

    return {
        "bureau_inquiry_6m": bureau_inq_status,
        "new_accounts_6m": len(recent_new_accounts_6m),
        "new_accounts_6m_target": "<= 1 new account in 6 months",
        "dispute_safety": dispute_safety,
        "total_reported_monthly_payments_cents": total_monthly_payments_cents,
        "dti": dti,
        "score_band": score_band,
    }


def optimize_snapshot(
    snapshot: dict[str, Any],
    card_due_days: dict[str, int] | None = None,
    monthly_income_cents: int | None = None,
    self_reported_fico: int | None = None,
    as_of_date: date | None = None,
) -> dict[str, Any]:
    """Run the full Stacking Capital credit optimization analysis on a snapshot."""
    hs = snapshot.get("health_summary", {})
    overall_util = float(hs.get("utilization_pct", 0.0) or 0.0)
    overall_bal = int(hs.get("revolving_balance_cents", 0) or 0)
    overall_band = classify_utilization_band(overall_util, overall_bal)

    cards = build_pay_by_recommendations(snapshot, card_due_days=card_due_days, as_of_date=as_of_date)
    azeo = build_azeo_plan(cards)
    readiness = analyze_inquiries_and_readiness(
        snapshot,
        as_of_date=as_of_date,
        monthly_income_cents=monthly_income_cents,
        self_reported_fico=self_reported_fico,
    )

    return {
        "overall_utilization_pct": overall_util,
        "overall_band": overall_band,
        "utilization_bands_guide": UTIL_BANDS,
        "per_card_pay_by": cards,
        "azeo_plan": azeo,
        "readiness": readiness,
        "score_timing_note": (
            "AnnualCreditReport.com reports do not contain FICO scores. If checking scores on "
            "Experian/Credit Karma phone apps, note those refresh daily while monthly 3-bureau "
            "monitoring (e.g. ScoreIQ) updates monthly—a higher phone score means a recent positive update posted."
        ),
    }
