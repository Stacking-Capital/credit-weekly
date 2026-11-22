"""Toggleable preset routines for weekly credit pulls, pay-by-date reminders, and alerts."""

from __future__ import annotations

from typing import Any


DEFAULT_ROUTINE_PRESETS: list[dict[str, Any]] = [
    {
        "id": "weekly_pull_reminder",
        "name": "Weekly 3-Bureau Pull Reminder",
        "enabled": True,
        "schedule": "0 9 * * 1",
        "schedule_human": "Mondays at 9:00 AM local",
        "channels": ["in_chat", "email"],
        "trigger_kind": "cron",
        "prompt_template": (
            "Check the encrypted snapshot store to verify at least 7 days have passed since the last "
            "Equifax, Experian, and TransUnion pull. If a pull is due, run the weekly 3-bureau credit pull: "
            "prefer Vault-saved bureau logins and the remembered browser profile on the user's computer; "
            "never ask them to open bureau sites; never ask for SSN, DOB, passwords, or OTP codes in chat — "
            "use a Secure Form only when a bureau requires identity or a code. Parse, diff, optimize, update "
            "their existing Grok Page, and send alerts on the channels they already chose. If a Secure Form "
            "or captcha is needed, pause and ping the user in this chat. Deliver the result to the user in "
            "this chat and on any enabled channel. If a pull is not due, do not message them."
        ),
    },
    {
        "id": "per_card_pay_by_reminders",
        "name": "Per-Card Pay-By-Date Reminders (Before Statement Close)",
        "enabled": True,
        "schedule": "0 9 * * *",
        "schedule_human": "Daily 9:00 AM check (fires 3 days before each card's reporting date & due date)",
        "channels": ["in_chat", "email"],
        "trigger_kind": "cron_conditional",
        "prompt_template": (
            "Read the latest encrypted snapshot's optimization pay-by dates. If today is within 3 days of any "
            "open revolving card's statement close/reporting date (pay_by_date) or payment due date, send a "
            "concise reminder naming the card, masked last 4, current balance, pay-down amount to hit <=20% "
            "or AZEO 1-9%, and remind them: pay by the due date to avoid late marks, pay by the statement-close "
            "window to lower the balance reported to the bureaus. Stay silent if no card is within the 3-day window."
        ),
    },
    {
        "id": "utilization_threshold_alerts",
        "name": "Utilization Band Crossing Alerts (>9% / >20% / >30%)",
        "enabled": True,
        "schedule": "on_snapshot_diff",
        "schedule_human": "Runs automatically after every weekly parse/diff",
        "channels": ["in_chat", "email"],
        "trigger_kind": "post_parse_hook",
        "thresholds_pct": [9, 20, 30],
        "prompt_template": (
            "Alert immediately if overall or any individual card utilization crosses above 9% (leaving AZEO prime), "
            "20% (Stacking Capital benchmark), or 30% (funding blocker), and list the exact dollar paydown needed "
            "before the next statement close date."
        ),
    },
    {
        "id": "new_inquiry_account_alerts",
        "name": "New Inquiry, New Account & Derogatory Alerts",
        "enabled": True,
        "schedule": "on_snapshot_diff",
        "schedule_human": "Runs automatically after every weekly parse/diff",
        "channels": ["in_chat", "email"],
        "trigger_kind": "post_parse_hook",
        "prompt_template": (
            "Alert immediately via in-chat and email if the weekly diff detects any new hard inquiry "
            "(flagging bureaus nearing the 2-inquiries-in-6-months cap), new account, collection, public record, "
            "new address, or adverse status downgrade."
        ),
    },
]


def build_routine_configs(
    enabled_ids: list[str] | None = None,
    delivery_channels: list[str] | None = None,
    user_email: str = "",
    per_card_pay_by: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build concrete routine toggle states and per-card pay-by reminder schedules."""
    enabled_set = set(enabled_ids) if enabled_ids is not None else {r["id"] for r in DEFAULT_ROUTINE_PRESETS}
    channels = delivery_channels or ["in_chat", "email"]

    configured = []
    for preset in DEFAULT_ROUTINE_PRESETS:
        item = dict(preset)
        item["enabled"] = preset["id"] in enabled_set
        item["channels"] = channels
        if "email" in channels and user_email:
            item["email_recipient"] = user_email
        if preset["id"] == "per_card_pay_by_reminders" and per_card_pay_by:
            item["card_schedules"] = [
                {
                    "creditor": c["creditor"],
                    "masked": c["account_masked"],
                    "pay_by_date": c["recommended_pay_by_date"],
                    "due_date_note": c["due_date_note"],
                    "target_note": c["recommendation"],
                }
                for c in per_card_pay_by
            ]
        configured.append(item)
    return configured
