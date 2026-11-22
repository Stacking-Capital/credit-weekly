# Shareable Grok Bot Template Blueprint: "Free 3-Bureau Credit Monitor"

A standalone, free-forever Grok Bot template (**v0.1 beta**) in three stages: Stage 1 weekly ACR reports (no scores, plus a versioned 700.credit export), Stage 2 bureau-direct scores, and Stage 3 an optional FICO Score 8 trio. It aims at the core monitoring, alert, and dashboard workflow of $25–$35/month subscriptions with zero subscription cost.

## 1. Bot Metadata
- **Bot Name:** `Credit Weekly (Free 3-Bureau Monitor)`
- **Short Description:**
  > Free weekly 3-bureau credit monitoring. The bot drives Equifax, Experian, and TransUnion in your browser; you stay in chat and only fill a Secure Form when a code is needed. Tracks trends and utilization pay-by dates in a summary-first Grok Page, and delivers alerts via chat, email, Slack, or text.

## 2. Preset Toggleable Routines & Alerts Layer
Users toggle each preset on/off and choose delivery channels (`in-chat`, `email`, `Slack`, `SMS/iMessage`):
1. **Weekly Pull Reminder** (`0 9 * * 1`, flexible) — Checks 7-day eligibility and runs the bot-driven pull (Vault logins after setup; Secure Form only if a bureau asks for a code).
2. **Per-Card Pay-By-Date Reminders** (`0 9 * * *` conditional) — Fires 3 days before each card's statement close/reporting date (to lower reported balance) and before the payment due date (to avoid lates).
3. **Utilization Band Crossing Alerts** (post-diff hook) — Fires when overall or per-card utilization crosses 9% (AZEO prime), 20% (benchmark), or 30% (high-utilization blocker).
4. **New Inquiry & New Account Alerts** (post-diff hook) — Fires on new hard pulls (noting 2-in-6-months per-bureau cap) or new tradelines.
5. **Score / Health Index & Negative Item Alerts** (post-diff hook) — Fires on FICO/Health Index shifts or added/removed late marks, collections, and public records.

## 3. Summary-First Grok Page Dashboard
- **Top fold:** Historical trend graph — Credit-Health Index (NOT a FICO) on Stage 1; model-labeled bureau-direct scores on Stage 2; labeled FICO Score 8 trio on Stage 3 — plus Utilization %, plain-English key factors, and this week's Alerts.
- **Details on demand:** Filterable bureau pills and drill-down tabs for Pay-By Timing & AZEO Plan, Tradelines, Inquiries, Collections/Public Records, Personal Info, and Alert Preferences.

## 4. Per-User Data Privacy & Isolation
- **Across Users:** Copying a shareable bot template creates an independent bot inside **that user's own Grok Bot account**, with their own box, browser session, private persistent store (`/cursor/stores/store-<uuid>`), and private Grok Page Library. Neither the template creator nor any other user can access another user's data.
- **Within One Account:** Snapshots are stored inside this bot's own private store encrypted at rest with AES-256-GCM (`credit_weekly.vault`); full SSN, full DOB, passwords, and OTP codes are never typed in chat or stored in bot memory (Secure Forms are write-only); Grok Pages contain zero network calls and only masked identifiers (`****1234`).

---

## 5. Packaging as a Grok Bot Template

Source: [Templates for Grok Bot](https://x.ai/bot/guides/templates-for-grok-bot) (Matt Palmer, Sep 8, 2026).

**A template is a recipe, not a clone.** It packages instructions, skills, non-personal memories, routines (triggers), and first-party plugins, then shares via a Team or Public link with one-click **Add to Grok Bot**. It does **not** include custom code/scripts, custom MCP servers, or secrets. The installer's bot rebuilds its own version.

### Recommended approach (do not use a public MCP server)
Ship the parser, diff, optimizer, vault, and Grok Page exporter in a **public GitHub repo**. Encode first-run setup in the `getting-started` skill so the new owner's bot clones (or writes) that toolkit onto **their** private box. A shared MCP would send credit-report PII through a third-party endpoint, add hosting cost, and is not packaged by templates anyway.

### What goes in each template slot

| Slot | Include | Exclude |
|------|---------|---------|
| **Bot instructions** | Short generalized description + privacy rule (never type SSN/DOB/passwords/OTP in chat; use Secure Forms; user never visits bureau sites) | Vault passphrases, emails, personal notes |
| **Skills** | `getting-started`, `weekly-3-bureau-credit-pull` (Stage 1 reports), `score-signin` (Stage 2 bureau-direct scores), and `fico-trio` (Stage 3 FICO 8 trio). Skills may include compact code fences the bot writes to disk if `git clone` is unavailable. | Secrets in skill text |
| **Memories (non-personal only)** | Conventions: 7-day ACR cadence; AZEO and 20%/30% utilization bands; 2 hard inquiries / 6 months per bureau; Credit-Health Index is not a FICO score; default Monday 9:00 AM reminder | Names, files, scores, SSN last-4, any user's vault path |
| **Routines (triggers)** | Weekly pull reminder (`0 9 * * 1`, flexible). Pay-by, utilization, inquiry, and score/derog alerts are created after the new owner chooses channels. | Pre-bound email addresses or Slack channel IDs |
| **First-party plugins** | Optional Gmail, Slack, or iMessage/SMS so those alert channels can be offered. The installer reconnects each plugin in their own account. | Custom MCP servers and API keys |

### First-run setup (getting-started skill)
1. Clone `https://github.com/Stacking-Capital/credit-weekly.git` into `/workspace/credit-weekly` (or write modules from skill code fences). Never copy another user's vault, PDFs, or `canvas_id`.
2. Ask setup questions one at a time: reminder day/time, Stage 1 bot-driven Secure Form capture vs PDF-drop backup, optional Stage 2 bureau-direct scores, optional Stage 3 FICO 8 trio, alert channels. Never ask for SSN, DOB, passwords, or OTP in chat. First pull follows the new-user branch map starting at AnnualCreditReport.com. Clone `https://github.com/Stacking-Capital/credit-weekly`.
3. If email/Slack/SMS was chosen, prompt the owner to reconnect those first-party plugins. Then create the weekly routine and any opted-in alert routines from the packaged triggers.
4. Offer the first baseline pull. After parse, `WriteCanvas` creates a **new** private Page in the new owner's Library and stores that `canvas_id` only in their bot store.

If this workspace disallows **Public** templates, publish as a **Team** template or clear policy before creating a public link.


## 6. One-time setup, hands-free after

The person should never go to bureau sites themselves. computer-use on **their** registered computer drives the browsers; in-chat Secure Forms fill identity and OTP/KBA (values never enter chat). After first run, reuse Vault saved logins, persistent cookies, and "remember this device."

**Lowest-friction weekly path:** first run via AnnualCreditReport.com (official FACTA baseline, almost always OTP/KBA because ACR has no login) while creating or linking free bureau accounts (Experian free membership, myEquifax + Core Credit, TransUnion Service Center). Weekly: log into those accounts and download reports. Fall back to ACR per bureau if login fails, and still pull ACR occasionally (quarterly or before a dispute). Residual OTP risk remains when a bureau re-challenges a device.

Stages: **1** ACR full reports + versioned 700.credit export (`skill/SKILL.md`); **2** bureau-direct scores (`skill/score-signin-SKILL.md`); **3** FICO 8 trio via myFICO Free + CreditWise (`skill/fico-trio-SKILL.md`). New-user first-time ACR branches and their Secure Form mappings live in the Stage 1 skill. Unverified branches are marked **TO CONFIRM LIVE**. Click-order labels are marked **TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH** until his baseline recording is ingested. After that recording, the bot still self-learns a *new* user's first-time path into `<store>/runbooks/acr-first-time-branches.md` (no PII).
