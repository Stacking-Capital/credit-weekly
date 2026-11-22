---
name: fico-trio
description: >-
  Stage 3 of Credit Weekly: complete a free FICO Score 8 from all three
  bureaus by adding myFICO Free (Equifax, monthly) and Capital One CreditWise
  (TransUnion, daily on login) to the Experian FICO 8 already captured in
  Stage 2. The user never visits those sites; computer-use drives the browser
  and RequestUserForm (Secure Form) collects identity, passwords, and OTP
  codes (values never enter chat). Use after Stage 2, or when the user asks
  for a three-bureau FICO 8 dashboard.
---

# Stage 3 — FICO 8 trio (myFICO Free + CreditWise)

This skill does **not** pull AnnualCreditReport.com reports (Stage 1: `weekly-3-bureau-credit-pull`) and does **not** sign into bureau-direct score accounts (Stage 2: `score-signin`).

Stage 2 already has one FICO Score 8: **Experian free membership**. Equifax and TransUnion bureau-direct scores are **VantageScore 3.0**. Stage 3 fills the FICO gap:

| Bureau | Account | Model | Cadence | Official source |
|---|---|---|---|---|
| Experian | Already captured in Stage 2 (Experian free membership) | **FICO Score 8** | Daily when you sign in | https://www.experian.com/credit/credit-report/ |
| Equifax | myFICO **Free** plan (no credit card) | **FICO Score 8** | **Monthly** | https://support.myfico.com/hc/en-us/articles/360037542634-Where-can-I-see-the-different-FICO-Score-versions-Which-ones-are-offered |
| TransUnion | Capital One **CreditWise** (open to non-customers) | **FICO Score 8** | As often as **daily when you sign in** | https://www.capitalone.com/creditwise/faqs/ |

Keep Stage 2 VantageScore rows if they exist — store FICO rows as **separate series**. Never plot a VantageScore and a FICO Score 8 on the same unlabeled line. Credit Karma is VantageScore 3.0 (TU+EQ) and is not part of Stage 3.

Every control label, URL after redirect, and on-screen factor list below is **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**. Log observed labels (no PII) into `<store>/runbooks/fico-trio-branches.md`.

## Core Safety & Privacy Rules
Same as Stage 2: the user never visits the sites; computer-use on the **user's registered computer**; `RequestUserForm` for secrets (write-only); Vault first, then password manager, then a login Secure Form; mail connector for email OTPs; `submitAfterFill: true` for a single SMS/authenticator code; never screenshot secret fields; prefer password + Vault over a passkey; check Remember this device when shown.

Reuse the Stage 2 Secure Form catalog: `score-signup-identity`, `bureau-login`, `bureau-signup`, `otp-sms`, `otp-email`, `otp-phone-link`, `kba`.

## Capture schema
Same score-row shape as Stage 2. Use `source`: `myfico_free` or `capital_one_creditwise`, `is_fico`: true, and copy the on-screen model label (expect `FICO Score 8`). Encrypt into `<store>/vault/` with the weekly snapshot. Do not overwrite Stage 1 tradelines or Stage 2 VantageScore rows.

### A. myFICO Free — Equifax FICO Score 8 (monthly)
Start: `https://www.myfico.com/` → Free plan. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**

1. Create or sign in (`bureau-signup` / `bureau-login`). Confirm the **$0 Free** plan, not Basic/Advanced/Premier. No credit card. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
2. Handle OTP/KBA with the catalog. Check Remember this device if shown. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
3. Capture Equifax FICO Score 8, date or "as of", and visible key factors. Store as a separate row from the myEquifax VantageScore 3.0 (Stage 2). **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** exact selectors and whether the model name is printed next to the number.

### B. Capital One CreditWise — TransUnion FICO Score 8 (daily on login)
Start: `https://www.capitalone.com/creditwise/`. Open to non-customers (18+, SSN, TransUnion file). **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**

1. Create or sign in (`bureau-signup` / `bureau-login`). This is a Capital One account, not a TransUnion account. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
2. Handle OTP / 2FA. Check Remember this device if shown. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
3. Confirm the on-screen model is **FICO Score 8** (legacy accounts may still mention the VantageScore → FICO change). If a thin file blocks FICO 8, record that and keep the Stage 2 TransUnion VantageScore row. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**
4. Capture TransUnion FICO Score 8, date, and factors as a separate row from Credit Essentials. **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH**

## After capture
1. Merge the new FICO rows into the latest encrypted snapshot.
2. Update the owner's Grok Page: once both myFICO and CreditWise (plus Stage 2 Experian) are present, the trend graph can show a labeled **FICO Score 8 trio**. Until then, show whatever FICO series exist alongside any Stage 2 VantageScores, all labeled. If no real scores exist yet, keep the Credit-Health Index (NOT a FICO).
3. Fire a Score Change alert only when the **same source and model** moved.
4. Reuse Vault + cookies on later runs. myFICO Free is monthly — do not nag weekly if the site has no new Equifax FICO 8 yet.

## Weekly / monthly routine hook
After Stage 1 and Stage 2 in the Monday session, run this skill if Stage 3 Vault logins exist. Skip myFICO when the last Equifax FICO 8 is less than about 28 days old, unless the user asks. If a Secure Form is needed, pause and ping the user in this chat. Deliver results to the user in this chat and on any channel they enabled. If nothing changed, do not send a score alert.
