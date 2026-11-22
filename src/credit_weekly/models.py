"""Normalized data structures, PII masking, deterministic IDs, and score-free health metrics."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0.0"
BUREAUS = ("equifax", "experian", "transunion")
BUREAU_LABELS = {
    "equifax": "Equifax",
    "experian": "Experian",
    "transunion": "TransUnion",
}

ADVERSE_RATINGS = {"30", "60", "90", "120", "150", "180", "C/O", "CO", "COL", "RPO", "FC", "BK"}


def norm_space(text: str | None) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def norm_creditor(name: str | None) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", " ", str(name or "").upper()).strip()
    return re.sub(r"\s+", " ", cleaned)


def mask_ssn(raw: str | None) -> str:
    """Extract at most the last 4 digits of an SSN; never store full SSN."""
    digits = re.sub(r"\D", "", str(raw or ""))
    if len(digits) >= 4:
        return digits[-4:]
    return ""


def mask_account_number(raw: str | None) -> str:
    """Mask account number so at most the trailing 4 alphanumeric chars remain visible."""
    s = norm_space(raw)
    if not s:
        return "****"
    alnum = re.sub(r"[^A-Z0-9]", "", s.upper())
    # If already masked at the end (e.g. '492900****') keep prefix/last4 safe
    digits_only = re.sub(r"\D", "", s)
    if digits_only and not s.endswith("*"):
        return "****" + digits_only[-4:]
    if len(alnum) <= 4:
        return "****" + alnum
    return "****" + alnum[-4:]


def mask_dob_year(raw: str | None) -> str:
    """Return only birth year (YYYY) for PII minimization."""
    m = re.search(r"(19\d{2}|20\d{2})", str(raw or ""))
    return m.group(1) if m else ""


def parse_money_cents(raw: str | int | float | None) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(round(raw * 100))
    s = str(raw).strip()
    if not s or s in {"-", "--", "N/A", "NA", "Not Reported"}:
        return None
    neg = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    cleaned = re.sub(r"[^0-9.]", "", s)
    if not cleaned:
        return None
    try:
        cents = int(round(float(cleaned) * 100))
        return -cents if neg else cents
    except ValueError:
        return None


def stable_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def tradeline_id(creditor: str, account_masked: str, opened: str = "") -> str:
    last4 = re.sub(r"[^A-Z0-9]", "", account_masked.upper())[-4:]
    return "tl_" + stable_hash(f"{norm_creditor(creditor)}:{last4}:{opened}")


def inquiry_id(creditor: str, date: str, bureau: str, kind: str) -> str:
    return "iq_" + stable_hash(f"{norm_creditor(creditor)}:{date}:{bureau}:{kind}")


def public_record_id(kind: str, filed_date: str, bureau: str) -> str:
    return "pr_" + stable_hash(f"{norm_creditor(kind)}:{filed_date}:{bureau}")


def new_bureau_report(bureau: str, origin: str = "annualcreditreport.com", parser: str = "") -> dict[str, Any]:
    return {
        "bureau": bureau,
        "source": {
            "origin": origin,
            "parser": parser,
            "file_number_masked": "",
            "report_date": "",
            "confidence": 0,
        },
        "personal_info": {
            "names": [],
            "ssn_last4": "",
            "dob_year": "",
            "addresses": [],
            "employers": [],
        },
        "accounts": [],
        "collections": [],
        "inquiries": [],
        "public_records": [],
        "warnings": [],
    }


def new_snapshot(
    bureaus: dict[str, dict[str, Any]] | None = None,
    captured_at: str | None = None,
    week_label: str | None = None,
    is_example_data: bool = False,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    iso_ts = captured_at or now.isoformat()
    if not week_label:
        iso_cal = now.isocalendar()
        week_label = f"{iso_cal.year}-W{iso_cal.week:02d}"
    snap = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": f"snap_{week_label}_{stable_hash(iso_ts)[:8]}",
        "week_label": week_label,
        "captured_at": iso_ts,
        "is_example_data": is_example_data,
        "bureaus": bureaus or {},
        "health_summary": {},
    }
    snap["health_summary"] = compute_health_summary(snap["bureaus"])
    return snap


def compute_health_summary(bureaus: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Compute score-free report health metrics across available bureaus.

    Revolving balances and limits are deduplicated by normalized (creditor, last4)
    so a single credit card reported by all 3 bureaus is not triple-counted.
    """
    present = [b for b in BUREAUS if b in bureaus]
    dedup_accounts: dict[str, dict[str, Any]] = {}
    all_collections: dict[str, dict[str, Any]] = {}
    hard_inquiries = 0
    public_records = 0
    total_ratings = 0
    on_time_ratings = 0

    for b_key in present:
        report = bureaus[b_key]
        for acct in report.get("accounts", []):
            key = f"{norm_creditor(acct.get('creditor'))}:{acct.get('account_number_masked', '****')[-4:]}"
            existing = dedup_accounts.get(key)
            # Prefer open/higher-confidence record when merging across bureaus
            if existing is None or (acct.get("balance_cents") or 0) > (existing.get("balance_cents") or 0):
                dedup_accounts[key] = acct
            for ph in acct.get("payment_history", []):
                rating = str(ph.get("rating", "")).upper()
                if rating in {"OK", "C", "0"}:
                    total_ratings += 1
                    on_time_ratings += 1
                elif rating in ADVERSE_RATINGS:
                    total_ratings += 1

        for col in report.get("collections", []):
            ckey = f"{norm_creditor(col.get('creditor'))}:{col.get('account_number_masked', '****')[-4:]}"
            all_collections[ckey] = col

        hard_inquiries += sum(1 for iq in report.get("inquiries", []) if iq.get("kind") == "hard")
        public_records += len(report.get("public_records", []))

    accounts_list = list(dedup_accounts.values())
    open_accounts = sum(1 for a in accounts_list if a.get("is_open"))
    adverse_accounts = sum(1 for a in accounts_list if a.get("is_adverse"))
    rev_bal = sum(
        (a.get("balance_cents") or 0)
        for a in accounts_list
        if a.get("kind") == "revolving" and a.get("is_open")
    )
    rev_lim = sum(
        (a.get("credit_limit_cents") or 0)
        for a in accounts_list
        if a.get("kind") == "revolving" and a.get("is_open") and (a.get("credit_limit_cents") or 0) > 0
    )
    util_pct = round((rev_bal / rev_lim) * 100, 1) if rev_lim > 0 else 0.0
    on_time_pct = round((on_time_ratings / total_ratings) * 100, 1) if total_ratings > 0 else 100.0

    return {
        "bureaus_present": present,
        "total_accounts": len(accounts_list),
        "open_accounts": open_accounts,
        "revolving_balance_cents": rev_bal,
        "revolving_limit_cents": rev_lim,
        "utilization_pct": util_pct,
        "adverse_accounts": adverse_accounts,
        "collections_count": len(all_collections),
        "hard_inquiries_24m": hard_inquiries,
        "public_records_count": public_records,
        "on_time_history_pct": on_time_pct,
    }
