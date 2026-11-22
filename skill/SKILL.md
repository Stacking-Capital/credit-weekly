---
name: weekly-3-bureau-credit-pull
description: >-
  Guide and automate a weekly 3-bureau credit report pull. The user never
  visits bureau sites: computer-use on their registered computer drives
  AnnualCreditReport.com and free bureau accounts; RequestUserForm (Secure
  Form) collects identity and OTP/KBA (values never enter chat). After
  one-time setup, reuse Vault logins, persistent cookies, and remembered
  devices. Includes first-time branch map, parse/diff/optimize, multi-channel
  alerts, and a summary-first Grok Page dashboard. Use when the user asks to
  pull weekly credit reports, refresh 3-bureau monitoring, or run the weekly
  credit check routine.
---

# Weekly 3-Bureau Credit Pull & Credit Monitor

This skill is **Stage 1**: free weekly full 3-bureau reports from AnnualCreditReport.com (and, after setup, from free bureau report downloads). ACR reports have **no scores**. That is already valuable on its own — a complete FACTA file, weekly diffs, pay-by coaching, and alerts — and it is the import source for a versioned `CreditSnapshot` (`schema_version` `1.0.0`) plus the three PDFs that can be imported into Stacking's separate [700.credit](https://app.700.credit) platform. This bot is not a 700.credit front door.

**Stage 2** (`score-signin`) captures bureau-direct scores: Experian free (FICO Score 8), myEquifax + Core Credit (VantageScore 3.0), TransUnion Credit Essentials (VantageScore 3.0). **Stage 3** (`fico-trio`) adds myFICO Free and CreditWise so the dashboard can show a FICO Score 8 from all three bureaus. Until Stage 2 has at least one captured score, the dashboard trends the labeled Credit-Health Index (NOT a FICO).

## Core Safety & Privacy Rules
1. **The user never visits bureau sites themselves.** Drive AnnualCreditReport.com and bureau portals with computer-use on the **user's registered computer** (preferred: their persistent browser profile and cookies). The shared agent box is only a fallback.
2. **Never collect full SSN, DOB, passwords, or OTP codes in chat.** When a page needs those values, open `RequestUserForm` (Secure Form). The host fills the live browser fields; values are write-only and never come back to you. Only `ssn_last4` and `dob_year` are kept in parsed JSON.
3. **Sign-in order:** Vault saved logins first, then a connected password manager, then a Secure Form (`kind: "login"` so it can be saved). For email OTPs, read the code from a connected Gmail/Outlook inbox when possible. For SMS/authenticator OTPs or KBA answers, send a one-field (or KBA multi-field) Secure Form (`submitAfterFill: true` for a single OTP field). Hand the screen over only for captchas the subagent already failed, passkeys, or QR/device approvals. Never screenshot secret fields.
4. **FCRA authorization:** Only pull the user's own reports (or reports with explicit written authorization).
5. **Encrypted stores:** Bureau passwords live in the user's Settings › Vault (you never see them). Weekly snapshots live in this bot's private store encrypted with AES-256-GCM (`credit_weekly.vault`). Delete temporary plaintext files after updating the Grok Page.
6. **Never embed full account numbers, SSN, or full DOB in a Grok Page.** Only pass PII-scrubbed summaries (`****1234`) to `WriteCanvas`.

## Packaging note (Grok Bot templates)
This skill is meant to travel inside a Grok Bot template ([Templates for Grok Bot](https://x.ai/bot/guides/templates-for-grok-bot)). Templates include skills, non-personal memories, routine triggers, and first-party plugins — not custom code, MCP servers, or secrets. If `/workspace/credit-weekly` is missing on first use, run the `getting-started` skill first: clone `https://github.com/Stacking-Capital/credit-weekly` (or write the compact modules from skill code fences) onto this owner's private box. Never reuse another user's vault, PDFs, or `canvas_id`.

## Walkthrough lock-in and self-learning (new users)
Patrick will record a live ACR walkthrough as the **baseline** for click order and current labels. After that recording is ingested, this bot must still **self-learn the NEW USER first-time flow**, starting at `https://www.annualcreditreport.com/index.action`. Patrick's own session may already have bureau accounts, cookies, or a remembered device — do not treat that path as a first-time user's path.

**How to self-learn (every first-time or unknown screen):**
1. Drive the browser yourself. Read visible page title, headings, and non-secret field labels only. Never screenshot SSN, password, or OTP fields.
2. Match the screen to a branch in the map below and open the mapped Secure Form.
3. Append an entry to `<store>/runbooks/acr-first-time-branches.md` with: date, bureau or `acr-central`, branch id, outcome (`success` / `fail` / `fallback`), and exact button or heading text observed. **No PII, no OTP values, no SSN, no answers.**
4. If the screen is not in the map, pause, describe only the visible non-secret UI, use the closest Secure Form, and log it as **TO CONFIRM LIVE**.
5. Do not overwrite the baseline runbook from a single surprise screen. Promote a new branch only after it is confirmed in Patrick's walkthrough, confirmed live twice, or the user confirms the label.

Marker key:
- **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** — lock exact labels and click order from his baseline recording.
- **TO CONFIRM LIVE** — first-time or failure branches that may not appear in his recording (new accounts, KBA fail, freeze, fraud alert, "can't verify online").

## Secure Form catalog (in-chat, values never returned)
Use these prompts. Do not invent a chat question that asks for the same secret.

| Form id | When to open | Fields (write-only) | Submit behavior |
|---|---|---|---|
| `acr-identity` | ACR central request form | Legal first / middle / last / suffix, SSN, DOB, current street / city / state / ZIP, previous address if the page asks | Fill all visible fields, then continue |
| `otp-sms` | SMS or authenticator code | Single code field | `submitAfterFill: true` |
| `otp-email` | Email code when a mail connector cannot read it | Single code field | `submitAfterFill: true` |
| `otp-phone-link` | Bureau sends a tap-link (common on Experian ACR) | No secret; short confirmation: user taps the link on their phone, then confirms in chat that they tapped it | Not a secret form |
| `kba` | Multiple-choice or short-answer credit-file questions | One field per visible question (answers never logged) | Fill, then continue |
| `bureau-login` | myEquifax, Experian, TransUnion, myFICO, CreditWise sign-in | Username/email + password (`kind: "login"`) | Fill, then sign in; save to Vault |
| `bureau-signup` | Bureau offers a free account during or after the report | Email, password, any required non-SSN profile fields (`kind: "login"` if it creates a reusable login) | Fill, save to Vault, check "remember this device" if shown |
| `freeze-pin` | Online verification is blocked by a security freeze and a PIN is required to lift it temporarily | Freeze PIN only | Fill the bureau freeze-lift field; do not ask the user to visit the site |
| `mail-request-confirm` | Online verify fails and the only path is mail or phone | No secrets; confirm mailing address already on file and whether to file the mail/phone request | User confirms in chat; bot can drive the on-screen mail request |

Email OTP shortcut: if Gmail/Outlook is connected, read the newest matching code and fill it yourself — skip `otp-email`.

---

## Step-by-Step Workflow

### Step 1: Pre-Flight Check
1. Prefer the **user's registered computer** (persistent browser profile) so cookies and "remember this device" survive. Confirm the credit-weekly toolkit is available (clone the public PII-free repo on first run).
2. If weekly bureau-account logins are already saved in Vault and a pull is due (≥7 days since last report per bureau), skip to **Step 2B**. If this is a first-time user or Vault is empty, run **Step 2A**.
3. Do not ask the user to open Equifax, Experian, TransUnion, or AnnualCreditReport.com themselves.

### Step 2A: One-time setup + new-user first-time flow
Drive the browser yourself. Use the Secure Form catalog. Check **Remember this device** / **trusted device** whenever a bureau offers it.

Recommended path:
1. Run the official ACR first-time flow below for a full FACTA baseline (all 3 bureaus). Save each PDF before leaving that bureau's tab.
2. If a bureau offers a free account during or after the report, create or link it via `bureau-signup` / `bureau-login` and save it to Vault. If no offer appears, after the PDFs are saved, create the free accounts in this order: Experian free membership, myEquifax + **Core Credit**, TransUnion Service Center (full inquiries) and optionally Credit Essentials (score only; it omits soft inquiries).
3. Confirm PDFs parse, encrypt the snapshot, and create the persistent Grok Page.

**Honesty cap:** ACR itself has no durable login. The first ACR visit will almost always need `acr-identity` plus per-bureau OTP and sometimes KBA. Weekly hands-free relies on the bureau accounts, not on repeating ACR every week.

#### First-time branch map (start here)
Start at **`https://www.annualcreditreport.com/index.action`**.

##### A. ACR landing — branch `acr-landing`
- Expected: a control such as **Request your free credit reports** or **Start Here**. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** exact button copy, any interstitial (security tip, freeze reminder, Spanish toggle).
- Bot clicks through. No Secure Form.
- **TO CONFIRM LIVE:** Akamai / captcha interstitial on a new device. If a captcha appears, the computer-use subagent tries first; if it fails, hand the screen over (`request_box_help`) without asking the user to open the URL themselves.

##### B. Central request form — branch `acr-request-form`
Expected fields (map to `acr-identity`):

| Field | Notes |
|---|---|
| First name, middle, last, suffix | Suffix may be optional |
| SSN | Full SSN; never in chat; never stored past fill |
| Date of birth | Month / day / year |
| Current mailing address | Street, city, state, ZIP |
| Previous address | Only if the form asks something like "less than 2 years at this address" — **TO CONFIRM LIVE** |
| Phone or email on the central form | May appear here or only on the bureau handoff — **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** |

- **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** required vs optional fields, exact labels, and the continue-button copy.
- After fill, do not re-read the form values.

##### C. Bureau selection — branch `acr-bureau-select`
- Choose Equifax, Experian, and TransUnion (first run: all three unless a known freeze will block one).
- **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** checkbox vs toggle UI, whether selection is on the same page as identity, and the continue-button copy.
- Then follow the selected bureaus **sequentially**. Finish and save one PDF before advancing. If the session warns that leaving will end access, believe it.

##### D. Equifax handoff — branches `eq-*`
Work through the first matching branch:

| Branch | What you see (expected, not yet locked) | Secure Form | Next |
|---|---|---|---|
| `eq-otp` | Email and/or SMS one-time code | `otp-email` or `otp-sms` (mail connector first) | Report view |
| `eq-kba` | Multiple security questions | `kba` | Report view, or `eq-kba-fail` |
| `eq-kba-fail` | Questions failed or attempts exceeded; mail or phone offer | `mail-request-confirm` | Mail/phone fallback; do not retry until the lockout clears. **TO CONFIRM LIVE** |
| `eq-freeze` | Security freeze blocks online disclosure | `freeze-pin` if a temporary lift is offered; otherwise explain and skip Equifax this week | **TO CONFIRM LIVE** |
| `eq-fraud-alert` | Fraud alert requires extra steps or blocks online access | Closest form (`otp-*`, `kba`, or `mail-request-confirm`) | **TO CONFIRM LIVE** |
| `eq-cant-verify` | "Can't verify online" / unable to verify identity | `mail-request-confirm` | Official mail/phone path (see fallbacks). **TO CONFIRM LIVE** |
| `eq-already-pulled` | Already requested within 7 days | None | Skip; use last PDF or myEquifax if Vault login exists |
| `eq-report` | Report is on screen | None | **Print Credit Report** → system **Save as PDF** as `equifax.pdf`. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** exact print/save labels and whether a printable-view second click is required. |
| `eq-account-offer` | myEquifax or Core Credit signup/sign-in is offered | `bureau-signup` or `bureau-login`; check remember-this-device | Enroll **Core Credit** for daily reports (without it, myEquifax is about **six reports/year**). Score shown is VantageScore 3.0, not FICO. **TO CONFIRM LIVE** whether this offer appears in the ACR handoff or only later. |
| `eq-next` | Continue back to ACR | None | **Get your next report or finish** — **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** wording. |

##### E. Experian handoff — branches `ex-*`

| Branch | What you see (expected, not yet locked) | Secure Form | Next |
|---|---|---|---|
| `ex-contact` | Email and/or phone collection | Extend `acr-identity` only for empty contact fields, or a tiny contact Secure Form | Verification |
| `ex-otp-link` | SMS/email **link** to tap (not a numeric code) | `otp-phone-link` | Report view. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** link vs numeric OTP in 2026. |
| `ex-otp` | Numeric email/SMS code | `otp-sms` / `otp-email` | Report view |
| `ex-kba` | Security questions | `kba` | Report view, or `ex-kba-fail` |
| `ex-kba-fail` | KBA failed | `mail-request-confirm` | **TO CONFIRM LIVE** |
| `ex-freeze` / `ex-fraud-alert` / `ex-cant-verify` | Freeze, fraud alert, or cannot verify online | `freeze-pin` or `mail-request-confirm` | **TO CONFIRM LIVE** |
| `ex-already-pulled` | 7-day lockout | None | Skip or use Experian free account |
| `ex-report` | Report is on screen | None | **Print or Save Report**, then again on the printable view if it appears, as `experian.pdf`. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** still two saves? |
| `ex-account-offer` | Free Experian membership | `bureau-signup` or `bureau-login`; prefer password + Vault over an optional passkey | Daily Experian report + FICO 8 on sign-in. 2-step verification is optional in Account Information. **TO CONFIRM LIVE** if the offer is in-handoff. |
| `ex-next` | Return to ACR | None | Wording **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**. |

##### F. TransUnion handoff — branches `tu-*`

| Branch | What you see (expected, not yet locked) | Secure Form | Next |
|---|---|---|---|
| `tu-terms` | Review info, accept terms | None (click accept) | Expected copy like **I Accept & Continue** — **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** |
| `tu-otp` | 5-digit SMS or call passcode (about 15 minutes, about 3 tries) | `otp-sms` | Report view. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH:** still 5 digits? |
| `tu-kba` | Security questions in addition to or instead of the passcode | `kba` | **TO CONFIRM LIVE** |
| `tu-kba-fail` | Failed KBA or passcode attempts | `mail-request-confirm` | **TO CONFIRM LIVE** |
| `tu-freeze` / `tu-fraud-alert` / `tu-cant-verify` | Freeze, fraud alert, or cannot verify | `freeze-pin` or `mail-request-confirm` | **TO CONFIRM LIVE** |
| `tu-already-pulled` | 7-day lockout | None | Skip or use Service Center |
| `tu-report` | Report is on screen | None | **Print or Save My Report** as `transunion.pdf`. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** |
| `tu-account-offer` | Service Center and/or Credit Essentials | `bureau-signup` or `bureau-login` | Prefer **Service Center** for hard **and** soft inquiries. Credit Essentials has a free daily score but **omits soft inquiries** — never the only TU source. Optional $0.99 score upsell can be skipped. **TO CONFIRM LIVE** |
| `tu-next` | Done or back to ACR | None | Wording **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** |

##### G. Shared fallbacks (all bureaus)
- **Mail/phone official disclosure:** phone `1-877-322-8228`, or mail Annual Credit Report Request Service, P.O. Box 105281, Atlanta, GA 30348-5281 (typically mailed within ~15 days). The user should not have to hunt this down on a bureau site; tell them the path and offer to start the on-screen mail request if present.
- **Session timeout / PDF not saved:** do not advance. If the report is gone, that bureau may be locked for 7 days — say so clearly.
- **Retry lockouts** (wrong ZIP/state, too many OTP/KBA tries): stop that bureau, log the branch, continue with the others.

### Step 2B: Weekly hands-free path (recommended after setup)
Do **not** start at AnnualCreditReport.com every week. On the remembered browser profile, Vault-fill each free bureau login, open the report, and Save as PDF:

- Experian free membership → credit report → Print/Save as PDF (`experian.pdf`)
- myEquifax + Core Credit → credit report → Print/Save as PDF (`equifax.pdf`)
- TransUnion Service Center → credit report → Print/Save as PDF (`transunion.pdf`)

If a bureau forces an OTP: mail connector first, else `otp-sms` / `otp-email`. The user stays in chat. If login fails or the file looks incomplete versus last week's ACR parse, fall back to ACR **for that bureau only** (Step 2A branches D–F). Still use ACR occasionally (for example quarterly, or before a dispute) because it is the official FACTA weekly disclosure and can include fields a membership view trims.

**Lowest-friction recommendation (research, Nov 2026):** first run via ACR + create/link free bureau accounts; weekly via those accounts with Vault + cookies + remember-this-device. ACR has no account, so a weekly ACR repeat almost always re-asks identity and per-bureau OTP/KBA.

Sources: [Experian free report](https://www.experian.com/credit/credit-report/), [Experian login / 2-step / passkeys](https://www.experian.com/help/login/), [Equifax products with a free report](https://www.equifax.com/personal/help/article-list/-/h/a/equifax-products-free-credit-report/), [Equifax Core Credit](https://www.equifax.com/personal/products/credit/free-credit-score/), [TransUnion free report](https://www.transunion.com/free-credit-report/), [TU Service Center vs Credit Essentials](https://www.transunion.com/blog/credit-advice/how-do-i-get-my-credit-report-and-score-from-transunion).

**TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH and TO CONFIRM LIVE:** how often each bureau re-forces OTP on a remembered device; whether membership PDFs parse with the same templates as ACR PDFs; exact Print/Save paths on each member site.

Honesty cap: this is as hands-free as the bureau allows. Cookie expiry, a new IP, a freeze, or a risk check can still trigger OTP. It should not require the user to browse bureau sites or re-enter SSN most weeks.

### Step 3: Leave scores to Stage 2 and Stage 3
Stage 1 does not capture scores. After PDFs are parsed, compute the **Credit-Health Index (0–100, NOT a FICO score)** from the ACR data and use it on the Page until Stage 2 is on. Then offer `score-signin` (bureau-direct Experian / myEquifax+Core Credit / TransUnion Credit Essentials). Offer `fico-trio` only if they want a three-bureau FICO Score 8 (myFICO Free + CreditWise). Do not mix score logins into the ACR handoff.

### Step 4: Parse, Diff, Optimize & Encrypt
Save PDFs to `<store>/inbox/YYYY-MM-DD/` then run locally (zero network calls):

```bash
PYTHONPATH=/workspace/credit-weekly/src python3 -m credit_weekly.cli parse \
  --equifax <store>/inbox/YYYY-MM-DD/equifax.pdf \
  --experian <store>/inbox/YYYY-MM-DD/experian.pdf \
  --transunion <store>/inbox/YYYY-MM-DD/transunion.pdf \
  --week YYYY-Www --out /tmp/curr_snapshot.json
```

Decrypt the prior week's snapshot from `<store>/vault/` and run `credit_weekly.cli diff` plus `credit_weekly.optimizer.optimize_snapshot`:
- **Pay-by vs Due Date:** Flag each open revolving card's observed `Date Updated` (statement close proxy) and recommend paying down **2–3 business days before reporting** to lower reported utilization, while paying at least the minimum by the **due date** to avoid 30-day lates.
- **Utilization Bands & AZEO:** Evaluate `0%` vs `1–9%` (AZEO prime) vs `10–20%` (benchmark) vs `21–29%` (paydown needed) vs `30%+` (blocker). Exclude no-preset-limit charge cards and AU accounts from AZEO paydown; treat HELOC separately.
- **Inquiries & Readiness:** Track 6-month hard inquiries per bureau (≤2 cap) and mark inquiries linked to open accounts as **DO NOT DISPUTE**.

Re-encrypt the new snapshot with AES-256-GCM into `<store>/vault/` and delete temporary plaintext files.

### Step 5: Alerts Layer (in-dashboard + multi-channel)
Evaluate the user's per-alert preferences (`in_chat`, `email`, `slack`, `sms`/`imessage`) across 5 types:
1. **New Hard Inquiry Alert** (plus bureau 6-month cap warning if ≥2)
2. **Score / Credit-Health Index Change Alert**
3. **New Account Opened Alert**
4. **Balance / Utilization Band Crossing Alert** (crossing >9%, >20%, or >30%)
5. **Negative Item Added or Removed Alert** (lates, collections, public records)

Dispatch only to opted-in channels. Get explicit confirmation before any external Slack/SMS/email send if a saved routine preference does not already authorize it.

### Step 6: Update the summary-first Grok Page
Use the dashboard Page template at `/workspace/credit-weekly/dashboard/ExampleDashboard.canvas.tsx` (layout and controls). Replace the embedded `DATA` object with this week's PII-scrubbed bundle (`credit_weekly.cli export-dashboard` or the example bundle shape in `dashboard/example_bundle.json`).

- If `<store>/canvas_id.txt` exists, `WriteCanvas` that `canvas_id` (same persistent Page).
- If not (first run), `WriteCanvas` a **new** private Page titled for this owner (not the public Blueprint), then save the new `canvas_id` only in their store.

Layout contract:
- **Top fold:** Historical trend graph — Credit-Health Index (NOT a FICO) + Utilization % on Stage 1 only; model-labeled bureau-direct scores once Stage 2 is on; labeled FICO Score 8 trio once Stage 3 is on. Plain-English key factors and the active Weekly Alerts feed.
- **On-demand drill-down:** Bureau switcher (`All 3`, `Experian`, `Equifax`, `TransUnion`) and tabs (`Pay-By & Optimization`, `Tradelines`, `Inquiries`, `Collections & Public`, `Personal Info`, `Alert & Routine Toggles`).
- Never put SSN, full DOB, passwords, or full account numbers on the Page. Never imitate a bureau's official UI. No `<form>` and no secret collection on the Page.

### Step 7: Create routines (if not already created)
Use the ready-to-create prompts in the section below. Ask once for day/time and channels if getting-started has not already done so. Do not start routines until the user agrees.

---

## Ready-to-create routine prompts
Write each routine as intent, not a frozen tool list. End with who receives the result (the user in this chat, plus any channel they opted in) and what to do when there is nothing new. Name no tools in the saved prompt. Deliver in the user's America/New_York local time unless they chose another zone.

### Weekly 3-Bureau Pull Reminder
- **Schedule:** `0 9 * * 1` (Mondays 9:00 AM local; change if they picked another slot). At least 5 minutes from any other routine.
- **Prompt:** Check the encrypted snapshot store to see whether at least 7 days have passed since the last Equifax, Experian, and TransUnion pull. If a pull is due, run the weekly 3-bureau credit pull skill: prefer Vault-saved bureau logins and the remembered browser profile on the user's computer; never ask them to open bureau sites; never ask for SSN, DOB, passwords, or OTP codes in chat — use a Secure Form only when a bureau requires identity or a code. Parse, diff, optimize, update their existing Grok Page, and send alerts on the channels they already chose. If a Secure Form or captcha is needed, pause and ping the user in this chat. If a pull is not due yet, stay silent or send a one-line "not yet eligible" only if they asked to be told either way. Deliver the result to the user in this chat, and on any email, Slack, or text channel they enabled. If nothing is due and they did not ask for an all-clear, do not message them.

### Per-Card Pay-By-Date Reminders
- **Schedule:** `0 9 * * *` (daily 9:00 AM local).
- **Prompt:** Read the latest encrypted snapshot's pay-by dates. If today is within 3 days of any open revolving card's statement close/reporting date or payment due date, send a concise reminder naming the card, masked last 4, current balance, and the pay-down amount to hit ≤20% or AZEO 1–9%. Remind them: pay by the due date to avoid late marks; pay 2–3 business days before statement close to lower the balance reported to the bureaus. Deliver to the user in this chat and on any channel they enabled for pay-by reminders. If no card is within the 3-day window, do not message them.

### Utilization Band Crossing Alerts
- **When:** After every weekly parse/diff (not a separate cron). Include this intent in the weekly pull routine, or as a post-diff hook the weekly run performs.
- **Prompt:** If overall or any card utilization newly crosses above 9% (leaving AZEO prime), 20% (benchmark), or 30% (blocker), alert with the exact dollar paydown needed before the next statement close. Deliver to the user in this chat and on opted-in channels. If no band was crossed, do not send a utilization alert.

### New Inquiry & New Account Alerts
- **When:** After every weekly parse/diff.
- **Prompt:** If the weekly diff shows a new hard inquiry (flag bureaus at or over 2 inquiries in 6 months), a new account, or an adverse opening, alert immediately. Deliver to the user in this chat and on opted-in channels. If there is no new inquiry or account, do not send this alert.

### Score / Health Index & Negative Item Alerts
- **When:** After every weekly parse/diff.
- **Prompt:** If a connected FICO 8 or the Credit-Health Index (labeled not a FICO) changed, or if a late, collection, or public record was added or removed, alert with a plain-language summary. Deliver to the user in this chat and on opted-in channels. If nothing changed, do not send this alert.

---

## Dashboard Page template
Canonical layout (synthetic "Jordan Example" data, safe to ship in the public repo):

- `/workspace/credit-weekly/dashboard/ExampleDashboard.canvas.tsx`
- Data shape: `/workspace/credit-weekly/dashboard/example_bundle.json`
- Local fallback viewer: `/workspace/credit-weekly/dashboard/index.html`

On each weekly run, copy the template's structure, swap in the scrubbed bundle, and write or update the owner's private Grok Page. Do not overwrite the public Blueprint Page (`canvas_id` `1efc1c3f-a5c5-4ed8-9edc-1e45c4ea07e4`).
