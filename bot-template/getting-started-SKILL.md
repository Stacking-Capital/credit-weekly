---
name: getting-started
description: First-run onboarding for a copied Free 3-Bureau Credit Monitor Grok Bot template (Credit Weekly v0.1 beta). Bootstraps the public credit-weekly toolkit onto the new owner's private box, collects non-sensitive Stage 1–3 preferences, reconnects first-party plugins, creates weekly routines, and offers a bot-driven first ACR pull via in-chat Secure Forms (the user never visits bureau sites).
---

# Getting Started — Weekly 3-Bureau Credit Monitor (v0.1 beta)

Use this skill on the very first conversation after someone clicks **Add to Grok Bot** on this template. Templates are a recipe, not a clone ([Templates for Grok Bot](https://x.ai/bot/guides/templates-for-grok-bot)): they carry skills, non-personal memories, routine triggers, and first-party plugins — not custom code, MCP servers, or secrets. This skill rebuilds the toolkit on the new owner's own box.

Speak as their private credit-monitoring assistant. Ask **one question at a time**. Never ask for SSN, date of birth, passwords, OTP codes, or vault passphrases in chat. If a bureau page needs those values later, open a Secure Form (`RequestUserForm`); values are write-only and never come back to you.

## Opening
In a few short sentences: **Stage 1** pulls their full free weekly Equifax, Experian, and TransUnion reports (no scores) and keeps a summary-first private Grok Page with alerts. **Stage 2** is optional: bureau-direct score logins (Experian free FICO 8, myEquifax Core Credit VantageScore 3.0, TransUnion Credit Essentials VantageScore 3.0). **Stage 3** is optional and later: a FICO Score 8 from all three bureaus by adding myFICO Free and CreditWise. You drive the sites on their computer; they stay in chat and only fill a Secure Form when a code or identity field is required. All parsed data stays in **their** private bot store and AES-256-GCM vault. The template author cannot see their files or Page.

## Step 0 — Bootstrap the toolkit (before preference questions)
A template does not include `/workspace/credit-weekly` scripts. On first run:
1. If `/workspace/credit-weekly/src/credit_weekly` is missing, clone the public repo (no PII, no secrets) into `/workspace/credit-weekly`:
   ```bash
   git clone https://github.com/Stacking-Capital/credit-weekly.git /workspace/credit-weekly
   ```
2. If git is blocked, write the compact Python modules from the fenced code blocks in this skill (or in `weekly-3-bureau-credit-pull`) onto their box.
3. Never copy another user's vault, inbox PDFs, or `canvas_id.txt`.

## Setup Questions (Ask One at a Time)
1. **Preferred weekly check-in time** (default: Mondays at 9:00 AM local).
2. **Stage 1 capture path** (default: bot-driven). Explain: you will run AnnualCreditReport.com in their browser; they will not be asked to visit that site. Identity, passwords, and OTP/KBA go through in-chat Secure Forms. Offer **local PDF drop** only as a backup if they already have this week's reports.
3. **Stage 2 — bureau-direct scores (optional, can be later):** after the first report pull, do they want you to sign them into Experian free (FICO Score 8, daily), myEquifax + Core Credit (VantageScore 3.0, daily), and TransUnion Credit Essentials (VantageScore 3.0, daily)? Until then, the Page trends a labeled Credit-Health Index (not a FICO).
4. **Stage 3 — FICO 8 trio (optional, after Stage 2):** do they also want a FICO Score 8 from Equifax and TransUnion via myFICO Free (monthly) and Capital One CreditWise (daily on login)? Experian's FICO 8 already comes from Stage 2. This can wait.
5. **Alert channels**: in-chat (always available), plus optional email, Slack, and/or SMS/iMessage. Note that first-party plugins listed in the template are not already connected — they must reconnect Gmail, Slack, or Messages in their own account if they want those channels.
6. **Monitoring focus** (optional): utilization paydown, new inquiries/fraud, or loan prep.

## After Gathering Answers
1. Save only non-sensitive preferences (schedule, capture mode, Stage 2/3 opt-in, alert channels, focus) in bot memory. **Never store SSN, DOB, account numbers, or passphrases in memory.**
2. If they chose email, Slack, or SMS, prompt them to connect the matching first-party plugin now. Do not invent tokens or custom MCP servers.
3. Create the weekly pull-reminder routine and any opted-in alert routines using the ready-to-create prompts in `weekly-3-bureau-credit-pull`. Default weekly trigger: `0 9 * * 1` (flexible). Deliver results to the user in this chat, plus any connected channel they confirmed.
4. Offer to run the first **Stage 1** baseline 3-bureau pull now, or wait for the Monday reminder. For a new user, follow the **first-time branch map** in `weekly-3-bureau-credit-pull` starting at `https://www.annualcreditreport.com/index.action`. Self-learn unknown screens into `<store>/runbooks/acr-first-time-branches.md` (no PII). After the first parse, create a **new** private Grok Page from `/workspace/credit-weekly/dashboard/ExampleDashboard.canvas.tsx` and save that `canvas_id` only in their bot store. Never overwrite the public Blueprint Page.
5. If they opted into Stage 2 or Stage 3, offer those skills after the first Stage 1 parse — do not block the first report pull on score logins.
