# Credit Weekly

**v0.1 beta** — a free, local-first toolkit and shareable Grok Bot for weekly 3-bureau credit monitoring.

Clone: `https://github.com/Stacking-Capital/credit-weekly`

This is educational self-monitoring software. It is **not credit repair**, not a credit-repair service, and not legal or financial advice. A number on the dashboard is **not a FICO score unless it is explicitly labeled** as one (for example "FICO Score 8"). The computed Credit-Health Index is a 0–100 index derived from report data and is **not a FICO score**.

## Three stages

1. **Stage 1 — Weekly full reports (no scores).** Pull Equifax, Experian, and TransUnion disclosures from [AnnualCreditReport.com](https://www.annualcreditreport.com/index.action) (and, after setup, from free bureau report downloads). Parse, diff, encrypt, coach pay-by timing, and update a private Grok Page. ACR reports have no scores; the Page trends a labeled Credit-Health Index until later stages are on. Stage 1 also emits a versioned `credit-weekly-export` 1.0.0 pack (`schema/EXPORT_FOR_700_CREDIT.md`) that can be imported into Stacking's separate [700.credit](https://app.700.credit) platform. This repo is not a 700.credit front door.
2. **Stage 2 — Bureau-direct scores.** Learned logins, via in-chat Secure Forms, for Experian free (FICO Score 8, daily), myEquifax + Core Credit (VantageScore 3.0, daily), and TransUnion Credit Essentials (VantageScore 3.0, daily). Every score is labeled with its model.
3. **Stage 3 — FICO 8 trio.** Optional. Adds myFICO Free (Equifax FICO Score 8, monthly) and Capital One CreditWise (TransUnion FICO Score 8, daily) so the dashboard can show a FICO Score 8 from all three bureaus. Experian's FICO 8 already comes from Stage 2.

The person should never be sent to bureau sites to self-serve. Grok Bot drives the browser on their computer; identity, passwords, and OTP/KBA go through a write-only Secure Form (values never enter chat). After setup, reuse Vault logins, cookies, and "remember this device." Residual OTP is still possible.

## Skills

| Stage | Skill file | Skill name |
|---|---|---|
| Onboarding | `bot-template/getting-started-SKILL.md` | `getting-started` |
| 1 | `skill/SKILL.md` | `weekly-3-bureau-credit-pull` |
| 2 | `skill/score-signin-SKILL.md` | `score-signin` |
| 3 | `skill/fico-trio-SKILL.md` | `fico-trio` |

Install those skills in your own Grok Bot (the template author cannot save them into your account). Then:

```bash
git clone https://github.com/Stacking-Capital/credit-weekly.git /workspace/credit-weekly
```

## Project layout

```
credit-weekly/
├── README.md
├── LICENSE                          # MIT
├── bot-template/                    # Shareable Grok Bot template notes
├── skill/                           # Stage 1–3 skills
├── schema/                          # CreditSnapshot v1 + 700.credit export contract
├── src/credit_weekly/               # Model-agnostic parser, diff, vault, optimizer, CLI
├── fixtures/                        # SYNTHETIC "Jordan Example" data only
├── dashboard/                       # Example Grok Page template + offline HTML viewer
├── adapters/                        # Grok, ChatGPT, Claude, Gemini, Meta Muse notes
└── tests/
```

## Quickstart (local CLI + demo)

Requires Python 3.10+, `cryptography`, and `pypdf` or `pdftotext`.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v

PYTHONPATH=src python3 -m credit_weekly.cli demo --root .
```

`demo` writes `dashboard/data.js` and `dashboard/ExampleDashboard.canvas.tsx` from the synthetic fixtures. Parse real PDFs only on the owner's machine; never commit PDFs, vault files, or `canvas_id.txt`.

## Disclaimer

Credit Weekly is for educational, personal self-monitoring. It does not promise score increases, credit repair, credit restoration, or any particular lending outcome. Checking your own reports at AnnualCreditReport.com is a consumer disclosure under the FCRA and does not include a credit score. If you use this as part of a business that offers credit repair, comply separately with the Credit Repair Organizations Act and any applicable state law — this software is not a substitute for those disclosures or for legal counsel.

## License

[MIT](LICENSE) © 2026 Stacking Capital
