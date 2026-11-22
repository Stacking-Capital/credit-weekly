"""Pluggable template parsers for Experian and Equifax AnnualCreditReport.com reports.

NOTE / TODO:
Like open-source projects (e.g., wjwhitmire/errata), real Experian and Equifax
AnnualCreditReport.com PDF layouts vary slightly by browser print rendering and
change periodically. These parsers handle common labeled-field text blocks and
emit explicit confidence warnings so the assistant/user verifies extracted fields
against the saved PDF until real sample PDFs are calibrated in fixtures/.
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


def _parse_template_report(text: str, bureau: str, parser_name: str) -> dict[str, Any]:
    report = new_bureau_report(bureau, origin="annualcreditreport.com", parser=parser_name)
    report["warnings"].append(
        f"{bureau.title()} parser uses generic labeled-field template matching; "
        "TODO: calibrate coordinates against a real saved AnnualCreditReport.com PDF."
    )

    lines = [norm_space(ln) for ln in text.splitlines() if norm_space(ln)]
    section = "header"
    current_acct: dict[str, Any] | None = None

    def flush_acct() -> None:
        nonlocal current_acct
        if not current_acct:
            return
        creditor = current_acct.get("creditor", "UNKNOWN CREDITOR")
        masked = mask_account_number(current_acct.get("account_number", ""))
        opened = current_acct.get("opened", "")
        kind = current_acct.get("kind") or "other"
        if "collection" in f"{current_acct.get('account_type', '')} {current_acct.get('status', '')}".lower():
            kind = "collection"
        elif "revolving" in current_acct.get("account_type", "").lower() or "credit card" in current_acct.get("loan_type", "").lower():
            kind = "revolving"
        elif "mortgage" in current_acct.get("account_type", "").lower():
            kind = "mortgage"
        elif "installment" in current_acct.get("account_type", "").lower():
            kind = "installment"

        status = current_acct.get("status", "Open")
        is_open = not bool(current_acct.get("closed")) and "closed" not in status.lower()
        history = current_acct.get("payment_history", [])
        is_adverse = (
            kind == "collection"
            or (current_acct.get("past_due_cents") or 0) > 0
            or any(h.get("rating", "").upper() in ADVERSE_RATINGS for h in history)
            or any(w in status.lower() for w in ("late", "past due", "charge", "collection"))
        )

        record = {
            "id": tradeline_id(creditor, masked, opened),
            "creditor": creditor,
            "account_number_masked": masked,
            "kind": kind,
            "account_type": current_acct.get("account_type", ""),
            "loan_type": current_acct.get("loan_type", ""),
            "responsibility": current_acct.get("responsibility", ""),
            "status": status,
            "is_open": is_open,
            "is_adverse": is_adverse,
            "balance_cents": current_acct.get("balance_cents"),
            "credit_limit_cents": current_acct.get("credit_limit_cents"),
            "high_balance_cents": current_acct.get("high_balance_cents"),
            "past_due_cents": current_acct.get("past_due_cents"),
            "monthly_payment_cents": current_acct.get("monthly_payment_cents"),
            "opened": opened,
            "closed": current_acct.get("closed", ""),
            "updated": current_acct.get("updated", ""),
            "last_payment": current_acct.get("last_payment", ""),
            "dofd": current_acct.get("dofd", ""),
            "original_creditor": current_acct.get("original_creditor", ""),
            "remarks": current_acct.get("remarks", []),
            "payment_history": history,
            "confidence": 65,
        }
        if kind == "collection":
            report["collections"].append(record)
        else:
            report["accounts"].append(record)
        current_acct = None

    for line in lines:
        low = line.lower().rstrip(":")
        if low in {"personal information", "personal profile"}:
            flush_acct()
            section = "personal"
            continue
        if low in {"accounts", "credit accounts", "revolving accounts", "installment accounts", "mortgage accounts"}:
            flush_acct()
            section = "accounts"
            continue
        if low in {"collections"}:
            flush_acct()
            section = "collections"
            continue
        if low in {"hard inquiries", "inquiries", "regular inquiries"}:
            flush_acct()
            section = "inquiries"
            continue
        if low in {"public records"}:
            flush_acct()
            section = "public_records"
            continue

        m_kv = re.match(r"^([A-Za-z0-9 /&().#-]{2,40}?)\s*:\s*(.*)$", line)
        if section in {"header", "personal"} and m_kv:
            k, v = m_kv.group(1).lower(), norm_space(m_kv.group(2))
            if "date" in k and ("report" in k or "generated" in k):
                report["source"]["report_date"] = v
            elif "name" in k and v:
                report["personal_info"]["names"].append(v)
            elif "ssn" in k or "social security" in k:
                report["personal_info"]["ssn_last4"] = mask_ssn(v)
            elif "birth" in k or k == "dob":
                report["personal_info"]["dob_year"] = mask_dob_year(v)
            elif "address" in k and v:
                report["personal_info"]["addresses"].append({"text": v, "kind": "current", "reported": ""})
            continue

        if section in {"accounts", "collections"}:
            if m_kv and m_kv.group(1).lower() in {"account", "account name", "creditor", "creditor name"}:
                flush_acct()
                current_acct = {
                    "creditor": norm_space(m_kv.group(2)),
                    "kind": "collection" if section == "collections" else "",
                    "remarks": [],
                    "payment_history": [],
                }
                continue
            if current_acct is not None and m_kv:
                k, v = m_kv.group(1).lower(), norm_space(m_kv.group(2))
                if k in {"account number", "account #"}:
                    current_acct["account_number"] = v
                elif k in {"account type"}:
                    current_acct["account_type"] = v
                elif k in {"loan type"}:
                    current_acct["loan_type"] = v
                elif k in {"status", "account status", "payment status"}:
                    current_acct["status"] = v
                elif k in {"balance", "current balance"}:
                    current_acct["balance_cents"] = parse_money_cents(v)
                elif k in {"credit limit"}:
                    current_acct["credit_limit_cents"] = parse_money_cents(v)
                elif k in {"high balance", "high credit"}:
                    current_acct["high_balance_cents"] = parse_money_cents(v)
                elif k in {"past due", "amount past due"}:
                    current_acct["past_due_cents"] = parse_money_cents(v)
                elif k in {"monthly payment"}:
                    current_acct["monthly_payment_cents"] = parse_money_cents(v)
                elif k in {"date opened", "opened"}:
                    current_acct["opened"] = v
                elif k in {"date closed", "closed"}:
                    current_acct["closed"] = v
                elif k in {"date reported", "date updated", "status updated"}:
                    current_acct["updated"] = v
            continue

        if section == "inquiries":
            m_iq = re.match(r"^(.+?)\s*\|\s*(?:Date|Requested On)\s*:\s*([0-9/-]+)(?:\s*\|\s*Type\s*:\s*(\w+))?", line, re.I)
            if m_iq:
                cred = norm_space(m_iq.group(1))
                dt = norm_space(m_iq.group(2))
                iq_kind = (m_iq.group(3) or "hard").lower()
                if iq_kind not in {"hard", "soft", "promotional", "account_review"}:
                    iq_kind = "hard"
                report["inquiries"].append(
                    {
                        "id": inquiry_id(cred, dt, bureau, iq_kind),
                        "creditor": cred,
                        "date": dt,
                        "kind": iq_kind,
                        "permissible_purpose": "",
                    }
                )
            continue

        if section == "public_records":
            if "none" in line.lower() or "no public" in line.lower():
                continue
            m_pr = re.match(r"^(.+?)\s*\|\s*Filed\s*:\s*([0-9/-]+)\s*\|\s*Status\s*:\s*(.+)$", line, re.I)
            if m_pr:
                kind_pr = norm_space(m_pr.group(1))
                filed = norm_space(m_pr.group(2))
                report["public_records"].append(
                    {
                        "id": public_record_id(kind_pr, filed, bureau),
                        "kind": kind_pr,
                        "filed_date": filed,
                        "status": norm_space(m_pr.group(3)),
                        "reference_masked": "****",
                        "amount_cents": None,
                    }
                )

    flush_acct()
    total_items = len(report["accounts"]) + len(report["collections"])
    report["source"]["confidence"] = 65 if total_items > 0 else 25
    return report


def parse_experian_text(text: str) -> dict[str, Any]:
    # TODO: Add Experian PDF coordinate/table parser once real 2026 ACR Experian PDF fixture is added.
    return _parse_template_report(text, "experian", "experian-template-v1")


def parse_equifax_text(text: str) -> dict[str, Any]:
    # TODO: Add Equifax PDF coordinate/table parser once real 2026 ACR Equifax PDF fixture is added.
    return _parse_template_report(text, "equifax", "equifax-template-v1")
