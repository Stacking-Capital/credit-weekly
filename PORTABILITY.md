# Running Credit Weekly on other AI platforms

Credit Weekly is a skill pack plus a local Python toolkit, not a hosted service. The interchange format is **CreditSnapshot 1.0.0** (`schema/credit_snapshot.schema.json`). Grok Bot is the primary host. The same skills can be copied onto other assistants.

## What to copy

| Piece | Path |
|---|---|
| Onboarding | `bot-template/getting-started-SKILL.md` |
| Stage 1 weekly pull | `skill/SKILL.md` |
| Stage 2 bureau-direct scores | `skill/score-signin-SKILL.md` |
| Stage 3 FICO 8 trio | `skill/fico-trio-SKILL.md` |
| Host notes | `adapters/README.md` and `adapters/{grok,chatgpt,claude,gemini,meta}/` |
| Snapshot schema | `schema/credit_snapshot.schema.json` |
| Example snapshots | `fixtures/stage1_snapshot.json`, `stage2_snapshot.json`, `stage3_snapshot.json` (synthetic Jordan Example only) |

## Validate a snapshot

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m credit_weekly.validator fixtures/stage1_snapshot.json
```

A valid file prints `VALID ...` and exits 0. Errors name JSON paths only. They never print document values, so a last-4 or a score cannot leak into logs.

Stage 1 snapshots have report facts and a Credit-Health Index. Stages 2 and 3 add a `scores` array. Each score must name its `model` (for example `FICO Score 8` or `VantageScore 3.0`), `source`, `as_of` date, and `is_fico`. The Credit-Health Index is not a FICO score and does not belong in `scores`.

## Host rules that do not change

- The person should not be sent to bureau sites to self-serve. Prefer a write-only secret form on that host. If the host has no such form, they type identity or OTP only in the bureau browser the assistant is driving, never in chat.
- Snapshots stay on the user's machine or that platform's private store, encrypted when possible (AES-256-GCM via `credit_weekly.vault`).
- Do not invent AnnualCreditReport.com or bureau click-paths. Site steps marked `TO CONFIRM IN PATRICK'S RECORDED WALKTHROUGH` stay unmarked until a recorded walkthrough exists.
- Public artifacts use synthetic example data only. Never put a full SSN, a full account number, a password, or an OTP in a repo, a log, or a Page.

This repo is not a front door to 700.credit. The versioned export contract in `schema/EXPORT_FOR_700_CREDIT.md` is for later import into that separate platform.
