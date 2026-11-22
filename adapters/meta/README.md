# Meta Muse adapter

## What "Muse" is (and is not)
**Muse** is Meta's **personal AI agent**, launched **September 8, 2026**, powered by the **Muse Spark** model. Meta describes it as an agent that does work (forms, bookings, email) rather than only answering questions. People use it in the Muse app, on the web (muse.ai in third-party reports), and via WhatsApp. Sensitive steps (sending mail, paying) require user approval. Login credentials are stored in a vault the model is not supposed to read; browser work is described as running in a **Secure VM** with a dedicated browser.

This is **not**:
- **Microsoft Muse** (2025 game-world model from Microsoft Research)
- **Meta AI Studio** creator characters — Meta froze **new character creation and edits on August 10, 2026**, and has been shifting focus to Muse Spark / the Muse agent
- **Meta AI** the in-app chatbot (WhatsApp / Instagram / Facebook / meta.ai), which is a general assistant, not this agent's packaging surface

Treat Muse-for-Small-Business, Muse Charm, and Muse Realtime Avatar as adjacent Meta products, not the packaging path for Credit Weekly.

Public, official documentation on **recurring weekly schedules**, **shareable custom skills/templates**, and **persistent dashboards** was **not confirmed** as of this research pass (Nov 21, 2026). Build this port as experimental and re-verify on muse.ai / Meta's help pages before promising a one-click install.

## Instructions text (give Muse as standing instructions)
"You are helping me monitor my own Equifax, Experian, and TransUnion reports for free using AnnualCreditReport.com. Once a week, remind me and, with my approval, open the site in your browser VM. I will type my SSN, date of birth, and one-time codes myself — never ask me to paste those in chat. After I save the three PDFs, tell me to run the Credit Weekly parser on my computer (or walk me through uploading the PDFs). Summarize utilization, new inquiries, and adverse items only. Do not promise score changes or credit-repair results."

## ACR pull
Ask Muse to open AnnualCreditReport.com in its Secure VM browser and pause for your OTP/KBA and Print/Save as PDF on each bureau. Download or AirDrop/email the PDFs to your computer and run the **same** `src` CLI (`parse`, `diff`, `vault`). Do not leave full reports sitting in a WhatsApp thread.

## Weekly schedule
If Muse adds a native recurring-task control, set a Monday morning reminder. Until that is documented, use a calendar reminder, WhatsApp ping, or a Grok/Claude/Gemini scheduled task that simply tells you "open Muse and run this week's pull." Do not assume unattended weekly pulls.

## Notify
In-Muse chat and, if you use it, WhatsApp. Require approval before Muse sends any email that could include report details. Prefer a PII-minimized summary (utilization %, new inquiry names, no account numbers).

## Dashboard
No Grok Page equivalent is documented. Use the local `dashboard/index.html` after `export-dashboard`, or a short weekly summary message. Do not build this as an AI Studio character.

## Feasibility
**Experimental / partial.** The Secure VM browser is the right shape for a user-in-the-loop ACR pull. Recurring schedules, a portable skill format, local encrypted storage, and a persistent dashboard are unconfirmed, so Muse is a companion front-end — not a full replacement for the Grok Bot or the Python core.

Core repo: https://github.com/Stacking-Capital/credit-weekly (v0.1 beta). Stage 1 reports, Stage 2 bureau-direct scores, Stage 3 optional FICO 8 trio.
