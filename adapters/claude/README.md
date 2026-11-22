# Claude adapter

## Closest equivalent (as of Nov 2026)
A **Claude Skill** (same `SKILL.md` format as this repo) plus a **Project** for standing instructions, **Desktop or cloud scheduled tasks** (formerly "routines") for the Monday reminder, and **Claude in Chrome** or **computer use** for the ACR browser handoff.

Sources:
- [Skills vs Projects vs MCP](https://claude.com/resources/articles/skills-explained)
- [Cloud scheduled tasks / routines](https://code.claude.com/docs/en/routines)
- [Scheduling options (Cloud vs Desktop vs /loop)](https://code.claude.com/docs/en/scheduled-tasks)
- [Computer use (CLI, macOS research preview)](https://code.claude.com/docs/en/computer-use)

## Instructions text
Install `skill/SKILL.md` and `bot-template/getting-started-SKILL.md` as Claude Skills (they already use YAML frontmatter). Add a short Project instruction: "You are a free 3-bureau credit monitor. Follow @weekly-3-bureau-credit-pull. Never ask for SSN or DOB in chat. Run parsers only from the local credit-weekly/src core." Clone this repo onto the user's machine so Desktop tasks can see `src/`.

## ACR pull
Prefer **Claude in Chrome** or Desktop **computer use** (macOS research preview; Pro/Max/Ultra; interactive session; not Team/Enterprise; not `-p` headless). Navigate AnnualCreditReport.com, pause for OTP/KBA, save the three PDFs, then run:

```bash
PYTHONPATH=/path/to/credit-weekly/src python3 -m credit_weekly.cli parse \
  --equifax equifax.pdf --experian experian.pdf --transunion transunion.pdf \
  --week YYYY-Www --out /tmp/curr_snapshot.json
```

Diff, optimize, and encrypt with `credit_weekly.vault` on the user's disk. Cloud scheduled tasks do **not** have the user's local files (they get a fresh clone), so the **parse/vault step belongs on Desktop scheduled tasks**, not a pure cloud routine.

## Weekly schedule
- **Desktop scheduled task**: Monday morning reminder + (if the user is present) assist the pull and run the local CLI. Machine must be on.
- **Cloud scheduled task**: Monday reminder / "it's time to pull" ping that works with the laptop closed; minimum interval is 1 hour; cron is supported. Do not expect unattended ACR sign-in in the cloud.

## Notify
Claude chat on each run. Connectors / MCP can reach email or Slack if the user enables them. Keep report bodies off shared channels unless the user asks.

## Dashboard
No Grok Page. After `export-dashboard`, open `dashboard/index.html` locally, or paste the scrubbed bundle into a Claude **Artifact** (interactive summary-first view). Optionally regenerate the Artifact each week from the JSON bundle.

## Feasibility
**Strongest non-Grok port.** Skills map 1:1, Desktop scheduled tasks can run the Python core against local PDFs, and Chrome/computer use covers the ACR handoff. Gaps: computer use is macOS preview and plan-gated; there is no native persistent Canvas equivalent.

Core repo: https://github.com/Stacking-Capital/credit-weekly (v0.1 beta). Stage 1 reports, Stage 2 bureau-direct scores, Stage 3 optional FICO 8 trio.
