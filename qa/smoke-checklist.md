# Credit Weekly smoke checklist

Run these flows against a change like a real person would. A walkthrough-dependent step is a **GAP**, not a pass. Do not invent AnnualCreditReport or bureau click-paths.

## 1. Onboarding
- Start from `bot-template/getting-started-SKILL.md`.
- Pass: the opening explains Stage 1, the private Page that updates in place, and that identity never goes through chat. Questions are asked one at a time. No SSN, DOB, passwords, or OTP in chat.
- GAP: official template publishing and the first live "Add to Grok Bot" path still need Patrick.

## 2. Secure-form identity entry
- Pass: the skill tells the bot to open a Secure Form (`RequestUserForm`) for identity, login, or OTP, and never to read those values back into chat.
- GAP: a live form fill against AnnualCreditReport.com or a bureau waits on Patrick's recorded walkthrough. Leave every `TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH` line as-is.

## 3. Weekly pull
- Pass: parse, diff, optimize, and encrypt run locally on the Jordan Example fixtures with no network calls.
- GAP: live site steps for ACR and bureau accounts wait on the walkthrough.

## 4. Dashboard render
- Pass: `credit_weekly.cli export-dashboard` (or the example Pages) shows a Credit-Health Index labeled "Not a FICO score", a "What to do this week" focus, 12-week history with paydown and new-inquiry marks on the example Page, bureau tiles, and a collapsed full report. Example Pages carry a visible example-data label. Dream-state scores are labeled with model and bureau. No promised point gains. No SSN or full account numbers.
- Desktop 1440 and mobile 375: the hero, chart, and next-move copy stay readable; rows wrap; no horizontal clip of controls.
- GAP: rendering a real owner's first private Page waits on template publishing.

## 5. Same-Page weekly update
- Pass: the skill says to `WriteCanvas` the `canvas_id` in `<store>/canvas_id.txt` so the url does not change; it never overwrites the Blueprint or public example Pages; `page_state` is `ready` on a finished write and may be `updating` only as a brief in-place revision.
- GAP: a live second-week update on a published owner bot waits on template publishing.

## 6. Alerts
- Pass: the five alert types and the `templates/alert-preferences.md` defaults (in-chat on, other channels off until confirmed) are documented. Dashboard "This week" has a quiet-week empty state.
- GAP: a live send to email, Slack, or SMS is not run in this checklist. Do not send test messages.

## 7. Weekly digest (template only)
- Pass: `templates/weekly-digest-prompt.md` exists, names the same-Page link, forbids promised point gains, and says not to create the routine until the owner asks.
- GAP: do not create a live routine in this check.

## 8. Export
- Pass: a Stage 1 bundle and `CreditSnapshot` 1.0.0 export validate, use example data only, and stay PII-scrubbed (`****` masks, no full SSN).
