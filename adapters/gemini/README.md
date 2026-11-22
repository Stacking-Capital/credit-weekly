# Gemini adapter

## Closest equivalent (as of Nov 2026)
**Skills in Gemini** are replacing **Gems** (existing Gems are slated to migrate automatically). Recurring work runs as **Tasks** with schedules. Assisted site work uses **Computer use** in the Gemini app for Mac (rolled out Nov 19, 2026): an isolated window with a live preview, app-by-app permission, and a pause for logins.

Sources:
- [Create & manage schedules for tasks in Gemini](https://support.google.com/gemini/answer/17094710)
- [Gemini Apps release notes (Gems → Skills; Mac computer use)](https://gemini.google/release-notes/)
- [Computer use on Mac](https://blog.google/innovation-and-ai/products/gemini-app/computer-use-mac/)
- [Use Gemini with apps on your Mac](https://support.google.com/gemini/answer/18956635)

## Instructions text
Paste `skill/SKILL.md` into a Gemini Skill (do not depend on a long-lived Gem). Opening line: "You are a free weekly 3-bureau credit monitor. Follow the Credit Weekly skill. Never collect SSN or DOB in chat. Use the credit-weekly Python core on this computer when parsing PDFs."

## ACR pull
In a Gemini **Task**, mention `@Computer use` and ask Gemini to open AnnualCreditReport.com. It works in a separate virtual screen so the user can keep their cursor. Computer use is currently: **Gemini app for Mac**, English, **United States**, personal Google account (not work/school), age 18+, **Google AI Plus / Pro / Ultra**, macOS Sequoia 15+ on Apple Silicon. Gemini must pause for logins and OTP/KBA. Save the three PDFs, then run the same `src` CLI locally (`parse`, `diff`, `encrypt`).

## Weekly schedule
Create a Task schedule: "Every Monday morning, remind me to pull my weekly AnnualCreditReport.com reports and, if I am present, help with the 3-bureau save-as-PDF flow." Pro/Ultra can set weekly (and other) time-based schedules; without a Google AI subscription, or on Plus, Tasks schedule **at most once per day** in a general window (overnight / daytime / evening). Tasks are not available on work/school accounts and are limited in some regions (including, as of the help article, not in the EEA/UK for some plans).

## Notify
Gemini notifies when a Task finishes. Gmail monitors can also fire when a forwarded FICO 8 alert email arrives (Pro/Ultra). Optional: have the Task email a short, PII-minimized summary to the user.

## Dashboard
No Grok Page. Options: (1) local `dashboard/index.html`, (2) a Google Sheet or Doc that the Task updates from the scrubbed `export-dashboard` JSON (utilization trend + alerts only; no full SSN or account numbers), (3) a Gemini Canvas-style artifact if available in the account.

## Feasibility
**Good for US Mac users on a paid personal Gemini plan.** Weekly Tasks + computer use cover reminder and assisted ACR. Weaker elsewhere (no Mac computer use, work accounts, some countries). Persistent dashboard is a Doc/Sheet or local HTML, not a first-party Page.

Core repo: https://github.com/Stacking-Capital/credit-weekly (v0.1 beta). Stage 1 reports, Stage 2 bureau-direct scores, Stage 3 optional FICO 8 trio.
