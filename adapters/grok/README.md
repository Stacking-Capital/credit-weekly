# Grok Bot adapter (primary)

This is the native runtime. Package and share as a Grok Bot template per [Templates for Grok Bot](https://x.ai/bot/guides/templates-for-grok-bot) (Matt Palmer, Sep 8, 2026): a recipe of instructions, skills, non-personal memories, routine triggers, and first-party plugins — not custom code, MCP servers, or secrets.

## What to install
- Skills: `getting-started` (`bot-template/getting-started-SKILL.md`), `weekly-3-bureau-credit-pull` (Stage 1, `skill/SKILL.md`), `score-signin` (Stage 2, `skill/score-signin-SKILL.md`), and `fico-trio` (Stage 3, `skill/fico-trio-SKILL.md`).
- First-run: `git clone https://github.com/Stacking-Capital/credit-weekly.git /workspace/credit-weekly` (or write modules from skill fences). Keep `src/` unchanged.
- First-party plugins (reconnect after install): optional Gmail, Slack, iMessage/SMS for alert channels.

## Pull (user never visits bureau sites)
Prefer computer-use on the **user's registered computer** (persistent cookies / remembered device). The shared agent box is fallback only. Start a first-time user at `https://www.annualcreditreport.com/index.action` and follow the first-time branch map in `skill/SKILL.md`. Collect identity and OTP/KBA with in-chat Secure Forms (values never enter chat). After setup, weekly pulls use Vault-saved Experian / myEquifax+Core Credit / TransUnion Service Center logins. Save each report as PDF before leaving that tab. Parse locally:

```bash
PYTHONPATH=/workspace/credit-weekly/src python3 -m credit_weekly.cli parse \
  --equifax inbox/equifax.pdf --experian inbox/experian.pdf --transunion inbox/transunion.pdf \
  --week YYYY-Www --out /tmp/curr_snapshot.json
```

Then `diff`, `optimize_snapshot`, and `encrypt` into the bot's private store (`credit_weekly.vault`).

## Weekly schedule
Template includes a routine trigger: `0 9 * * 1` (Mondays 9:00 AM local, flexible). After onboarding, create optional daily pay-by reminders and post-diff alert routines. A scheduled run that needs an OTP or KBA **pauses and opens a Secure Form in chat** — routines cannot fill secrets unattended. Vault logins and a remembered device should make most weekly runs hands-free.

## Notify
Alerts appear on the Grok Page and go out on the channels the user enabled: in-chat (always), plus email, Slack, or SMS/iMessage after they reconnect those first-party plugins.

## Dashboard
Primary UI is a persistent **Grok Page** (`WriteCanvas`, `canvas_id` saved only in this bot's store): Stage 1 trends the Credit-Health Index (NOT a FICO); Stage 2 adds model-labeled bureau-direct scores; Stage 3 can show a labeled FICO Score 8 trio. Secondary: open `dashboard/index.html` locally after `python3 -m credit_weekly.cli export-dashboard` or `demo`.
