"""TransUnion AnnualCreditReport.com text/PDF parser.

Designed around the 2026 TransUnion consumer disclosure layout:
- Header ("Your TransUnion Credit Report", "File Number:", "Date Created:")
- Personal Information (Name, SSN, DOB, Current/Other Address, Employers)
- Satisfactory Accounts & Accounts with Adverse Information (incl. Collections)
- Payment History lines ("2026: Jan=OK Feb=OK ..." or grid rows)
- Regular Inquiries (hard), Promotional Inquiries, Account Review Inquiries
- Public Records
"""

from __future__ import annotations

import re
from typing import Any

from ..models import (
    ADVERSE_RATINGS,
    inquiry_id,
    mask_account_number,
    mask_dob_year,
    mask_ssn,
    new_bureau_report,
    norm_space,
    parse_money_cents,
    public_record_id,
    tradeline_id,
)

PARSER_NAME = "transunion-acr-v1"

SECTION_HEADERS = {
    "personal information": "personal",
    "employers": "employers",
    "satisfactory accounts": "accounts_sat",
    "accounts with adverse information": "accounts_adv",
    "collections": "collections",
    "regular inquiries": "inq_hard",
    "promotional inquiries": "inq_promo",
    "account review inquiries": "inq_review",
    "public records": "public_records",
}


def _classify_kind(account_type: str, loan_type: str, section: str) -> str:
    if section == "collections":
        return "collection"
    combined = f"{account_type} {loan_type}".upper()
    if "COLLECTION" in combined or "FACTORING" in combined:
        return "collection"
    if "MORTGAGE" in combined or "REAL ESTATE" in combined:
        return "mortgage"
    if "REVOLVING" in combined or "CREDIT CARD" in combined or "LINE OF CREDIT" in combined:
        return "revolving"
    if "INSTALLMENT" in combined or "AUTO" in combined or "STUDENT" in combined:
        return "installment"
    if "OPEN" in combined:
        return "open"
    return "other"


def _parse_kv(line: str) -> tuple[str, str] | None:
    m = re.match(r"^\s*([A-Za-z0-9 /&().#-]{2,42}?)\s*:\s*(.*)$", line)
    if not m:
        return None
    return norm_space(m.group(1)), norm_space(m.group(2))


def _finalize_account(raw: dict[str, Any], section: str) -> dict[str, Any]:
    creditor = raw.get("creditor", "UNKNOWN CREDITOR")
    acct_masked = mask_account_number(raw.get("account_number", ""))
    opened = raw.get("opened", "")
    kind = _classify_kind(raw.get("account_type", ""), raw.get("loan_type", ""), section)
    status = raw.get("status", "Unknown")
    closed = raw.get("closed", "")
    is_open = not bool(closed) and "CLOSED" not in status.upper() and "PAID" not in status.upper()
    if kind == "collection":
        is_open = "PAID" not in status.upper() and not bool(closed)

    history = raw.get("payment_history", [])
    has_adverse_hist = any(str(h.get("rating", "")).upper() in ADVERSE_RATINGS for h in history)
    status_upper = status.upper()
    is_adverse = (
        section == "accounts_adv"
        or kind == "collection"
        or has_adverse_hist
        or any(tok in status_upper for tok in ("PAST DUE", "LATE", "CHARGE", "COLLECTION", "DELINQ"))
        or (raw.get("past_due_cents") or 0) > 0
    )

    populated = sum(
        1
        for k in ("creditor", "account_number", "status", "opened", "balance_cents")
        if raw.get(k) not in (None, "", [])
    )
    confidence = min(100, 45 + populated * 11)

    return {
        "id": tradeline_id(creditor, acct_masked, opened),
        "creditor": creditor,
        "account_number_masked": acct_masked,
        "kind": kind,
        "account_type": raw.get("account_type", ""),
        "loan_type": raw.get("loan_type", ""),
        "responsibility": raw.get("responsibility", ""),
        "status": status,
        "is_open": is_open,
        "is_adverse": is_adverse,
        "balance_cents": raw.get("balance_cents"),
        "credit_limit_cents": raw.get("credit_limit_cents"),
        "high_balance_cents": raw.get("high_balance_cents"),
        "past_due_cents": raw.get("past_due_cents"),
        "monthly_payment_cents": raw.get("monthly_payment_cents"),
        "opened": opened,
        "closed": closed,
        "updated": raw.get("updated", ""),
        "last_payment": raw.get("last_payment", ""),
        "dofd": raw.get("dofd", ""),
        "original_creditor": raw.get("original_creditor", ""),
        "remarks": raw.get("remarks", []),
        "payment_history": history,
        "confidence": confidence,
    }


def parse_transunion_text(text: str) -> dict[str, Any]:
    report = new_bureau_report("transunion", origin="annualcreditreport.com", parser=PARSER_NAME)
    lines = text.splitlines()
    section = "header"
    current_acct: dict[str, Any] | None = None

    def flush_account() -> None:
        nonlocal current_acct
        if current_acct is None:
            return
        acct_obj = _finalize_account(current_acct, section)
        if acct_obj["kind"] == "collection" or section == "collections":
            report["collections"].append(acct_obj)
        else:
            report["accounts"].append(acct_obj)
        current_acct = None

    for raw_line in lines:
        line = norm_space(raw_line)
        if not line:
            continue

        low = line.lower().rstrip(":")
        if low in SECTION_HEADERS:
            flush_account()
            section = SECTION_HEADERS[low]
            continue

        if section == "header":
            kv = _parse_kv(line)
            if kv:
                k, v = kv
                kl = k.lower()
                if "file number" in kl:
                    report["source"]["file_number_masked"] = "****" + re.sub(r"\D", "", v)[-4:]
                elif "date created" in kl or "report date" in kl:
                    report["source"]["report_date"] = v
            continue

        if section == "personal":
            kv = _parse_kv(line)
            if kv:
                k, v = kv
                kl = k.lower()
                if kl in {"name", "also known as", "aka"} and v:
                    report["personal_info"]["names"].append(v)
                elif "social security" in kl or kl == "ssn":
                    report["personal_info"]["ssn_last4"] = mask_ssn(v)
                elif "date of birth" in kl or kl == "dob":
                    report["personal_info"]["dob_year"] = mask_dob_year(v)
                elif "address" in kl and v:
                    kind = "current" if "current" in kl else "other"
                    report["personal_info"]["addresses"].append({"text": v, "kind": kind, "reported": ""})
            continue

        if section == "employers":
            if not line.lower().startswith(("employer", "date verified")):
                report["personal_info"]["employers"].append(line)
            continue

        if section in {"accounts_sat", "accounts_adv", "collections"}:
            # Start of an account card: either "Account: NAME (#1234)" or ALL CAPS creditor header
            m_acct = re.match(r"^(?:Account Name|Account)\s*:\s*(.+?)(?:\s*\(([^)]+)\))?$", line, re.I)
            if m_acct:
                flush_account()
                current_acct = {
                    "creditor": norm_space(m_acct.group(1)),
                    "account_number": norm_space(m_acct.group(2) or ""),
                    "remarks": [],
                    "payment_history": [],
                }
                continue

            if (
                current_acct is None
                and re.match(r"^[A-Z0-9][A-Z0-9 &'.,/\-]{2,}$", line)
                and ":" not in line
            ):
                current_acct = {
                    "creditor": line,
                    "account_number": "",
                    "remarks": [],
                    "payment_history": [],
                }
                continue

            if current_acct is not None:
                # Payment history row: e.g. "Payment History 2026: Jan=OK Feb=OK Mar=30"
                m_hist = re.match(r"^(?:Payment History\s+)?(20\d{2})\s*:\s*(.+)$", line, re.I)
                if m_hist:
                    yr = m_hist.group(1)
                    pairs = re.findall(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*[=:]\s*([A-Z0-9/]+)", m_hist.group(2), re.I)
                    month_map = {
                        "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
                        "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
                        "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
                    }
                    for mon, rating in pairs:
                        mm = month_map.get(mon.upper(), "01")
                        current_acct["payment_history"].append(
                            {"month": f"{yr}-{mm}", "rating": rating.upper()}
                        )
                    continue

                kv = _parse_kv(line)
                if kv:
                    k, v = kv
                    kl = k.lower()
                    if kl in {"account number", "account #"}:
                        current_acct["account_number"] = v
                    elif kl in {"account type"}:
                        current_acct["account_type"] = v
                    elif kl in {"loan type"}:
                        current_acct["loan_type"] = v
                    elif kl in {"responsibility"}:
                        current_acct["responsibility"] = v
                    elif kl in {"pay status", "account status", "status"}:
                        current_acct["status"] = v
                    elif kl in {"balance", "current balance"}:
                        current_acct["balance_cents"] = parse_money_cents(v)
                    elif kl in {"credit limit"}:
                        current_acct["credit_limit_cents"] = parse_money_cents(v)
                    elif kl in {"high balance", "high credit", "original amount"}:
                        current_acct["high_balance_cents"] = parse_money_cents(v)
                    elif kl in {"past due", "amount past due"}:
                        current_acct["past_due_cents"] = parse_money_cents(v)
                    elif kl in {"monthly payment", "scheduled payment"}:
                        current_acct["monthly_payment_cents"] = parse_money_cents(v)
                    elif kl in {"date opened", "opened"}:
                        current_acct["opened"] = v
                    elif kl in {"date closed", "closed"}:
                        current_acct["closed"] = v
                    elif kl in {"date updated", "updated", "date reported"}:
                        current_acct["updated"] = v
                    elif kl in {"last payment made", "last payment", "date of last payment"}:
                        current_acct["last_payment"] = v
                    elif kl in {"date of first delinquency", "dofd"}:
                        current_acct["dofd"] = v
                    elif kl in {"original creditor"}:
                        current_acct["original_creditor"] = v
                    elif kl in {"remarks", "comments"} and v:
                        current_acct["remarks"].append(v)
                continue

        if section in {"inq_hard", "inq_promo", "inq_review"}:
            kind = {
                "inq_hard": "hard",
                "inq_promo": "promotional",
                "inq_review": "account_review",
            }[section]
            # Example: "SUMMIT BANK NA | Requested On: 2026-10-14 | Permissible Purpose: Credit Application"
            m_iq = re.match(
                r"^(.+?)\s*\|\s*(?:Requested On|Date)\s*:\s*([0-9/-]+)(?:\s*\|\s*(?:Permissible Purpose|Purpose)\s*:\s*(.+))?$",
                line,
                re.I,
            )
            if m_iq:
                cred = norm_space(m_iq.group(1))
                dt = norm_space(m_iq.group(2))
                purpose = norm_space(m_iq.group(3) or "")
                report["inquiries"].append(
                    {
                        "id": inquiry_id(cred, dt, "transunion", kind),
                        "creditor": cred,
                        "date": dt,
                        "kind": kind,
                        "permissible_purpose": purpose,
                    }
                )
            continue

        if section == "public_records":
            if "no public records" in line.lower() or "none reported" in line.lower():
                continue
            m_pr = re.match(r"^(.+?)\s*\|\s*Filed\s*:\s*([0-9/-]+)\s*\|\s*Status\s*:\s*(.+)$", line, re.I)
            if m_pr:
                kind_pr = norm_space(m_pr.group(1))
                filed = norm_space(m_pr.group(2))
                status_pr = norm_space(m_pr.group(3))
                report["public_records"].append(
                    {
                        "id": public_record_id(kind_pr, filed, "transunion"),
                        "kind": kind_pr,
                        "filed_date": filed,
                        "status": status_pr,
                        "reference_masked": "****",
                        "amount_cents": None,
                    }
                )

    flush_account()

    acct_confs = [a["confidence"] for a in report["accounts"] + report["collections"]]
    if acct_confs:
        report["source"]["confidence"] = round(sum(acct_confs) / len(acct_confs))
    elif report["personal_info"]["names"]:
        report["source"]["confidence"] = 65
    else:
        report["source"]["confidence"] = 20
        report["warnings"].append("Low parse confidence: verify extracted TransUnion text against PDF.")

    return report
