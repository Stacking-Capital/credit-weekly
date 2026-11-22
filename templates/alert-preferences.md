# Alert preferences flow (template only)

Use this during getting-started, or later when the owner wants to change alerts. Save only non-sensitive preferences in bot memory. Never store SSN, date of birth, passwords, or passphrases. Do not create or start a routine until the owner agrees. Do not send a test message to email, Slack, or SMS unless they clearly ask for one.

## Defaults
- In-chat: on for all five types below.
- Email, Slack, and SMS/iMessage: off until the owner reconnects that first-party plugin and confirms they want that type there.

## The five types
1. New hard inquiry (plus a 6-month cap warning if that bureau is at or over 2).
2. Score or Credit-Health Index change (the index is labeled not a FICO; any connected FICO Score 8 is named with its model and bureau).
3. New account opened.
4. Utilization band crossing (newly above 9%, 20%, or 30%).
5. Negative item added or removed (late, collection, or public record).

## How to ask
Ask one question at a time, in plain words:

1. "I can watch for five kinds of changes: a new inquiry, a score or Credit-Health Index move, a new account, a utilization-band crossing, and a new or removed negative item. In this chat I will mention all five unless you want some turned off. Which should I leave on?"
2. If they already chose email, Slack, or text: "Which of those same alerts, if any, should also go to [channel]? I will not send anything there until you say yes."
3. Confirm the matrix back in one short list and save it.

If they skip the question, keep the defaults. If they later say "fewer texts" or "only fraud," update the saved matrix and repeat it back.

## Dispatch rules
- Exception alerts fire only after a weekly parse/diff, and only for types and channels that are on.
- Get explicit confirmation before the first send on any external channel if a saved preference does not already authorize it.
- If nothing matched, do not message them.
- Copy stays short. No promised point gains. No secrets in the alert body. Link their existing dashboard Page when a change is easier to see there.

Site sign-in and OTP still follow the weekly skill. Do not invent AnnualCreditReport or bureau click-paths; leave any walkthrough-pending step as it is.
