"""Week-over-week 3-bureau credit snapshot diff engine."""

from __future__ import annotations

from typing import Any

from .models import BUREAUS, BUREAU_LABELS


def _index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items if "id" in item}


def _fmt_usd(cents: int | None) -> str:
    if cents is None:
        return "$0"
    sign = "-" if cents < 0 else ""
    val = abs(cents) / 100.0
    return f"{sign}${val:,.0f}" if abs(cents) % 100 == 0 else f"{sign}${val:,.2f}"


def diff_snapshots(prev: dict[str, Any], curr: dict[str, Any]) -> dict[str, Any]:
    """Compare two normalized CreditSnapshot objects and return alerts + metric deltas."""
    alerts: list[dict[str, Any]] = []
    bureau_diffs: dict[str, Any] = {}

    prev_bureaus = prev.get("bureaus", {})
    curr_bureaus = curr.get("bureaus", {})

    for bureau in BUREAUS:
        if bureau not in curr_bureaus:
            continue
        c_rep = curr_bureaus[bureau]
        p_rep = prev_bureaus.get(bureau)
        label = BUREAU_LABELS[bureau]

        if p_rep is None:
            alerts.append(
                {
                    "severity": "info",
                    "bureau": bureau,
                    "category": "bureau_added",
                    "title": f"{label} baseline captured",
                    "detail": f"First snapshot recorded with {len(c_rep.get('accounts', []))} accounts.",
                }
            )
            continue

        b_changes: list[dict[str, Any]] = []

        # 1. Accounts
        p_accts = _index_by_id(p_rep.get("accounts", []))
        c_accts = _index_by_id(c_rep.get("accounts", []))

        for aid, acct in c_accts.items():
            if aid not in p_accts:
                ev = {
                    "severity": "warning",
                    "bureau": bureau,
                    "category": "new_account",
                    "title": f"New account on {label}: {acct['creditor']} ({acct['account_number_masked']})",
                    "detail": f"Opened {acct.get('opened') or 'N/A'}, balance {_fmt_usd(acct.get('balance_cents'))}.",
                }
                alerts.append(ev)
                b_changes.append(ev)
                continue

            old = p_accts[aid]
            old_bal = old.get("balance_cents") or 0
            new_bal = acct.get("balance_cents") or 0
            if old_bal != new_bal:
                delta = new_bal - old_bal
                direction = "increased" if delta > 0 else "decreased"
                ev = {
                    "severity": "info",
                    "bureau": bureau,
                    "category": "balance_change",
                    "title": f"{label}: {acct['creditor']} balance {direction} by {_fmt_usd(abs(delta))}",
                    "detail": f"{_fmt_usd(old_bal)} -> {_fmt_usd(new_bal)} ({acct['account_number_masked']}).",
                }
                alerts.append(ev)
                b_changes.append(ev)

            old_lim = old.get("credit_limit_cents")
            new_lim = acct.get("credit_limit_cents")
            if old_lim is not None and new_lim is not None and old_lim != new_lim:
                ev = {
                    "severity": "warning" if new_lim < old_lim else "info",
                    "bureau": bureau,
                    "category": "limit_change",
                    "title": f"{label}: {acct['creditor']} credit limit changed",
                    "detail": f"{_fmt_usd(old_lim)} -> {_fmt_usd(new_lim)}.",
                }
                alerts.append(ev)
                b_changes.append(ev)

            if not old.get("is_adverse") and acct.get("is_adverse"):
                ev = {
                    "severity": "critical",
                    "bureau": bureau,
                    "category": "adverse_status",
                    "title": f"Adverse status change on {label}: {acct['creditor']}",
                    "detail": f"Status changed from '{old.get('status')}' to '{acct.get('status')}'.",
                }
                alerts.append(ev)
                b_changes.append(ev)

            if old.get("is_open") and not acct.get("is_open"):
                ev = {
                    "severity": "info",
                    "bureau": bureau,
                    "category": "account_closed",
                    "title": f"{label}: {acct['creditor']} marked closed",
                    "detail": f"Status: {acct.get('status')}.",
                }
                alerts.append(ev)
                b_changes.append(ev)

        # 2. Collections
        p_cols = _index_by_id(p_rep.get("collections", []))
        c_cols = _index_by_id(c_rep.get("collections", []))
        for cid, col in c_cols.items():
            if cid not in p_cols:
                ev = {
                    "severity": "critical",
                    "bureau": bureau,
                    "category": "new_collection",
                    "title": f"New collection on {label}: {col['creditor']}",
                    "detail": f"Balance {_fmt_usd(col.get('balance_cents'))} (Original: {col.get('original_creditor') or 'N/A'}).",
                }
                alerts.append(ev)
                b_changes.append(ev)

        for cid in set(p_cols) - set(c_cols):
            ev = {
                "severity": "info",
                "bureau": bureau,
                "category": "collection_removed",
                "title": f"Collection removed on {label}: {p_cols[cid]['creditor']}",
                "detail": "No longer present on this week's report.",
            }
            alerts.append(ev)
            b_changes.append(ev)

        # 3. Hard inquiries
        p_inq = {i["id"]: i for i in p_rep.get("inquiries", []) if i.get("kind") == "hard"}
        c_inq = {i["id"]: i for i in c_rep.get("inquiries", []) if i.get("kind") == "hard"}
        for qid, iq in c_inq.items():
            if qid not in p_inq:
                ev = {
                    "severity": "warning",
                    "bureau": bureau,
                    "category": "new_hard_inquiry",
                    "title": f"New hard inquiry on {label}: {iq['creditor']}",
                    "detail": f"Date: {iq.get('date')}.",
                }
                alerts.append(ev)
                b_changes.append(ev)

        # 4. Public records
        p_pr = _index_by_id(p_rep.get("public_records", []))
        c_pr = _index_by_id(c_rep.get("public_records", []))
        for pid, pr in c_pr.items():
            if pid not in p_pr:
                ev = {
                    "severity": "critical",
                    "bureau": bureau,
                    "category": "new_public_record",
                    "title": f"New public record on {label}: {pr['kind']}",
                    "detail": f"Filed {pr.get('filed_date')} ({pr.get('status')}).",
                }
                alerts.append(ev)
                b_changes.append(ev)

        # 5. Personal info / addresses
        p_addrs = {a.get("text", "").upper() for a in p_rep.get("personal_info", {}).get("addresses", [])}
        for addr in c_rep.get("personal_info", {}).get("addresses", []):
            txt = addr.get("text", "")
            if txt and txt.upper() not in p_addrs:
                ev = {
                    "severity": "warning",
                    "bureau": bureau,
                    "category": "new_address",
                    "title": f"New address reported on {label}",
                    "detail": txt,
                }
                alerts.append(ev)
                b_changes.append(ev)

        bureau_diffs[bureau] = b_changes

    severity_rank = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: (severity_rank.get(a["severity"], 9), a["bureau"]))

    ph = prev.get("health_summary", {})
    ch = curr.get("health_summary", {})
    metric_deltas = {
        "revolving_balance_delta_cents": (ch.get("revolving_balance_cents") or 0) - (ph.get("revolving_balance_cents") or 0),
        "revolving_limit_delta_cents": (ch.get("revolving_limit_cents") or 0) - (ph.get("revolving_limit_cents") or 0),
        "utilization_delta_pct": round((ch.get("utilization_pct") or 0.0) - (ph.get("utilization_pct") or 0.0), 1),
        "adverse_delta": (ch.get("adverse_accounts") or 0) - (ph.get("adverse_accounts") or 0),
        "collections_delta": (ch.get("collections_count") or 0) - (ph.get("collections_count") or 0),
        "hard_inquiries_delta": (ch.get("hard_inquiries_24m") or 0) - (ph.get("hard_inquiries_24m") or 0),
    }

    return {
        "previous_snapshot_id": prev.get("snapshot_id"),
        "current_snapshot_id": curr.get("snapshot_id"),
        "previous_week": prev.get("week_label"),
        "current_week": curr.get("week_label"),
        "alert_counts": {
            "critical": sum(1 for a in alerts if a["severity"] == "critical"),
            "warning": sum(1 for a in alerts if a["severity"] == "warning"),
            "info": sum(1 for a in alerts if a["severity"] == "info"),
        },
        "metric_deltas": metric_deltas,
        "alerts": alerts,
        "by_bureau": bureau_diffs,
    }
