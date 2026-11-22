# ChatGPT adapter

## Closest equivalent (as of Nov 2026)
Do **not** build this as a Custom GPT. OpenAI is retiring custom GPTs (standard date **December 11, 2026**) and migrating workflows to **Plugins** (reusable instructions, reference files, and connected apps). The older "ChatGPT agent" product is also retired; use **ChatGPT Work** for multi-step tasks and the **cloud browser** for signed-in site flows.

Sources:
- [GPTs in ChatGPT](https://help.openai.com/en/articles/8554407-gpts-in-chatgpt)
- [ChatGPT agent](https://help.openai.com/en/articles/11752874-chatgpt-agent)
- [Scheduled tasks](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)
- [Cloud browser](https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt)
- [Apps SDK (preview, MCP-based)](https://help.openai.com/en/articles/12515353-building-with-the-apps-sdk)

## Instructions text (paste into a Plugin / Work project)
Copy `skill/SKILL.md` (Stage 1), `skill/score-signin-SKILL.md` (Stage 2), `skill/fico-trio-SKILL.md` (Stage 3), and `bot-template/getting-started-SKILL.md` as Plugin instructions / reference files. Attach `https://github.com/Stacking-Capital/credit-weekly` or a zip of `src/` as knowledge — do not upload real credit PDFs or vault files. Keep the same safety rules: never collect SSN/DOB in chat; ACR OTP/KBA stays user-in-the-loop.

## ACR pull
On a paid plan with ChatGPT Work, start a Work task that uses **cloud browser**: go to AnnualCreditReport.com, pause for the user to sign in / enter SSN and OTPs, then Print → Save as PDF for Equifax, Experian, and TransUnion. Download the three PDFs to the user's machine (or a connected folder) and run the **same** `src` CLI locally, or have the user upload the PDFs into the chat for a local-side parse. Headless scraping will fail the same way it does on ACR (Akamai/WAF). Cloud browser is **not** on Free/Go.

## Weekly schedule
Create a **Scheduled task** (weekly, Monday morning) whose prompt is: "Remind me to complete this week's 3-bureau AnnualCreditReport.com pull, then parse and diff with last week." Scheduled tasks do **not** support GPTs or locked chats. Free/Go plans are limited (about 3 active tasks; at most daily, flexible windows). Event triggers (Gmail/Slack) can ingest forwarded FICO 8 alert emails.

## Notify
In-chat when the scheduled task finishes. Connect Gmail or Slack in Settings → Apps if the user wants email/Slack delivery. Do not send credit-report bodies to extra parties.

## Dashboard
There is no Grok Page. Render the summary-first view as: (1) a ChatGPT Canvas / document updated each week from `export-dashboard` JSON, (2) the local `dashboard/index.html`, or (3) later, a custom ChatGPT App via the Apps SDK if you want an in-chat UI (preview; Business/Enterprise for custom MCP apps). Scores and the Credit-Health Index must stay clearly labeled.

## Feasibility
**Strong on paid ChatGPT Work**, weaker on Free. The weekly reminder and assisted browser path exist; the Python core still runs on the user's computer; persistent encrypted vault and a first-class in-chat dashboard are thinner than Grok Bot.
