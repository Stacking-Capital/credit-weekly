# Weekly digest routine prompt (template only)

Do not create this routine until the owner agrees. Do not start it from this file on your own. This is intent for a saved Grok Bot routine, not a live schedule.

## When to offer it
After onboarding, if the owner wants a short weekly recap in this chat (and on any channel they already enabled) in addition to exception alerts. If they only want alerts when something changes, do not create this routine.

## Suggested schedule
`30 9 * * 1` (Mondays 9:30 AM in the owner's America/New_York zone, or the zone they chose). At least five minutes from the weekly pull reminder. If they would rather receive the digest immediately after a finished pull, skip a standing clock and run this intent as a post-pull step instead.

## Prompt to save
Write the routine as intent. Name no tools in the saved prompt.

---

Check whether this week's 3-bureau pull already finished and the owner's Grok Page was updated. If a pull is still in progress, wait; do not send a partial digest. If no new week is on file and they did not ask for an all-clear, stay silent.

If a new week is ready, write a short digest for the owner in this chat, and on any email, Slack, or text channel they already enabled for digests:

1. One line on the Credit-Health Index (labeled not a FICO) or, if Stage 2 or 3 is on, each connected score with its model and bureau.
2. What changed this week: inquiries, new accounts, paydowns, limit changes, or negative items. If nothing material changed, say it was a quiet week.
3. The one thing to do this week (pay-by date and amount), or that they are in good shape.
4. The link to their existing dashboard Page (the same url as last week).

Never promise a point gain. Never include SSN, date of birth, passwords, or full account numbers. Use only the owner's own data from their private store. If a Secure Form or captcha blocked the pull, say that in one line and ask them to continue in this chat. If nothing is due and they did not ask to be told either way, do not message them.

---
