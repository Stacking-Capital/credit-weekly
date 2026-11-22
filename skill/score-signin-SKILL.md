---
name: score-signin
description: >-
  Stage 2 of Credit Weekly: capture bureau-direct scores by signing into
  Experian free (FICO Score 8, daily), myEquifax + Core Credit (VantageScore
  3.0, daily), and TransUnion Credit Essentials (VantageScore 3.0, daily).
  The user never visits those sites; computer-use drives the browser and
  RequestUserForm (Secure Form) collects identity, passwords, and OTP codes
  (values never enter chat). Use after a Stage 1 ACR report pull, or when
  the user asks to add bureau-direct scores to their Grok Page. For a
  three-bureau FICO 8 trio, use the separate Stage 3 skill `fico-trio`.
---

# Stage 2 — Score Sign-In (bureau-direct learned login)

This skill does **not** pull AnnualCreditReport.com reports. That is Stage 1 (`weekly-3-bureau-credit-pull`). ACR disclosures have **no scores**. Stage 2 is a separate learned login flow for the three **bureau-direct** score accounts so the dashboard can plot real, model-labeled scores. Until at least one Stage 2 score is captured, the Page trends the labeled **Credit-Health Index (0–100, NOT a FICO)**. Completing a FICO Score 8 from all three bureaus is **Stage 3** (`fico-trio`) and is not part of this skill.

There is no Experian, Equifax, or TransUnion connector in the Grok plugin catalog (verified Nov 2026 against the Connect Apps list; the Finance/Plaid-style plugin lists bank, card, and investment accounts only — it does not return bureau scores). So this skill uses computer-use + Secure Forms, then reuses Vault logins and a remembered device.

## Core Safety & Privacy Rules
1. **The user never visits score sites themselves.** Drive the portals on the **user's registered computer** (persistent browser profile). The shared agent box is only a fallback.
2. **Never collect SSN, DOB, passwords, or OTP codes in chat.** Use `RequestUserForm` (write-only; values never return to the model). Never screenshot secret fields.
3. **Sign-in order:** Vault saved login → connected password manager → Secure Form (`kind: "login"`). Email OTP: try a connected Gmail/Outlook inbox first. SMS/authenticator OTP: one-field Secure Form (`submitAfterFill: true`). Hand the screen over only for a captcha the subagent already failed, a passkey, or a QR/device approval.
4. **Prefer password + Vault over a passkey** (passkeys often require a phone handoff).
5. Check **Remember this device** / **trusted device** whenever it is offered.
6. Store only scrubbed score rows in the bot vault (AES-256-GCM). Never put full SSN, full DOB, or passwords on the Grok Page.
7. **Label every score with its model and bureau.** Do not plot a VantageScore on the same unlabeled line as a FICO Score 8.

## Recommended sources (Nov 2026) — bureau-direct first

Stage 2 default (bureau-direct, the three logins Patrick asked for):

| Bureau | Account | Model | Cadence | Official source |
|---|---|---|---|---|
| Experian | Free Experian membership (no credit card) | **FICO Score 8** based on Experian | Updated **daily when you sign in** | https://www.experian.com/credit/credit-report/ |
| Equifax | myEquifax + enroll **Core Credit** | **VantageScore 3.0** based on Equifax (not FICO) | **Daily** on login | https://www.equifax.com/personal/products/credit/free-credit-score/ |
| TransUnion | TransUnion **Credit Essentials** (free) | **VantageScore 3.0** based on TransUnion (not FICO) | **Daily** refreshes on login | https://www.transunion.com/free-credit-score |

Notes that must stay on the dashboard:
- Experian free is **FICO Score 8**. myEquifax / Core Credit and TransUnion Credit Essentials are **VantageScore 3.0**, not FICO.
- Credit Karma is VantageScore 3.0 from TransUnion and Equifax and is not a Stage 2 source.
- Do not pay $0.99 for a TransUnion Service Center score when Credit Essentials is free.
- After these three logins are saved, offer **Stage 3** (`fico-trio`) if the user wants Equifax and TransUnion **FICO Score 8** as well (myFICO Free + CreditWise).

## Capture schema (store one row per source per pull)
```json
{
  "source": "experian_free | myequifax_core_credit | tu_credit_essentials",
  "bureau": "experian | equifax | transunion",
  "score": 0,
  "model": "FICO Score 8 | VantageScore 3.0 | other (copy the on-screen label)",
  "score_date": "YYYY-MM-DD",
  "captured_at": "ISO-8601",
  "factors": ["plain-language factor as shown", "..."],
  "product_name": "",
  "is_fico": false
}
```
No account numbers, SSN, or full DOB in this object. Encrypt into `<store>/vault/` with the weekly snapshot.

## Secure Form catalog
| Form id | When | Fields | Submit |
|---|---|---|---|
| `score-signup-identity` | New account requires name / DOB / SSN / address / phone / email | Only the fields visible on that screen | Fill, then continue |
| `bureau-login` | Returning sign-in | Username/email + password (`kind: "login"`) | Fill, sign in, save to Vault |
| `bureau-signup` | Create free account | Email + password and any non-secret profile fields (`kind: "login"`) | Fill, save to Vault |
| `otp-sms` / `otp-email` | One-time code | Single code | `submitAfterFill: true` (try mail connector first for email) |
| `otp-phone-link` | SMS/email tap-link instead of a code | No secret; user confirms in chat that they tapped it | Not a secret form |
| `kba` | Security questions | One field per visible question | Fill, then continue |

---

## Per-bureau learned flows
Every control label, URL after redirect, and on-screen factor list below is **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**. Log observed labels (no PII) into `<store>/runbooks/score-signin-branches.md`.

### A. Experian free membership — FICO Score 8 (daily)
Start: `https://www.experian.com/credit/credit-report/` (or the current free-membership/sign-in entry). **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**

1. If no Vault login: create the free membership (no credit card). Open `bureau-signup` / `score-signup-identity` for whatever the form actually asks (email, password, last-4 or full SSN, phone, address — **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**).
2. If a Vault login exists: `bureau-login`, then OTP if challenged (`otp-sms` / `otp-email` / `otp-phone-link`). Check Remember this device if shown. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
3. Prefer password + Vault. Experian passkeys are optional; skip unless the user already uses one (handoff). 2-step verification may live under Your Account → Account Information. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
4. Land on the score / report overview. Capture: numeric score, on-screen model (**expect "FICO Score 8"**), date or "as of", and visible key factors. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** exact selectors and whether the model name is printed next to the number.
5. Do not upgrade to a paid 3-bureau plan. Do not turn on paid add-ons.

### B. myEquifax + Core Credit — VantageScore 3.0 (daily)
Start: `https://my.equifax.com/` then enroll **Core Credit** (or `https://www.equifax.com/personal/products/credit/free-credit-score/`). **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**

1. Create or sign in to myEquifax via `bureau-signup` or `bureau-login`. OTP may appear on a new device. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
2. **Enroll Core Credit.** Without it, myEquifax is only about six free reports a year and may not include a daily score. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** the exact enroll clicks and whether a card is requested (it should not be for Core Credit).
3. Check Remember this device if shown.
4. Capture: numeric score, model (**must be recorded as VantageScore 3.0, not FICO**), date, factors. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
5. If the user also wants Equifax **FICO Score 8**, offer Stage 3 (`fico-trio`, myFICO Free) after this succeeds.

### C. TransUnion Credit Essentials — VantageScore 3.0 (daily)
Start: `https://www.transunion.com/free-credit-score` and choose the **free Credit Essentials** path, not Service Center and not the $0.99 one-time score. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**

1. TransUnion uses a centralized login. Create or sign in with `bureau-signup` / `bureau-login`. If the UI asks which product, pick Credit Essentials. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
2. OTP may arrive by text or email. Check Remember this device if shown. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
3. Confirm you are **not** on Service Center only (Service Center's score is a $0.99 VantageScore, not the free daily score). **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
4. Capture: numeric score, model (**VantageScore 3.0, not FICO**), date, factors. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
5. If the user also wants TransUnion **FICO Score 8**, offer Stage 3 (`fico-trio`, CreditWise) after this succeeds.

## After capture
1. Merge score rows into the latest encrypted snapshot (do not overwrite Stage 1 ACR tradelines).
2. Update the owner's Grok Page: the trend graph uses captured Stage 2 scores (each series labeled with model + bureau). If no Stage 2 score exists yet, keep the Credit-Health Index and the "NOT a FICO" label. Do not present this as a three-bureau FICO 8 trio until Stage 3 (`fico-trio`) has run.
3. Fire a Score Change alert only when the **same source and model** moved — never compare a VantageScore to a FICO as if they were one series.
4. Reuse Vault + cookies on later runs. If a bureau re-challenges, pause and open the matching Secure Form in chat.

## Weekly routine hook
The Monday pull routine should run Stage 1 first (ACR or bureau-account report PDFs). If Stage 2 Vault logins exist, run this skill next in the same session. If Stage 3 logins exist, run `fico-trio` after that. If a Secure Form is needed, pause and ping the user in this chat. Deliver results to the user in this chat and on any channel they enabled. If nothing changed, do not send a score alert.
