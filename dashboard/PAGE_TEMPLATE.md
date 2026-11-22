# Dashboard Page template

This folder is the **summary-first Grok Page template** the weekly skill writes or updates for each owner.

| File | Role |
|---|---|
| `ExampleDashboard.canvas.tsx` | Canonical consumer layout: Credit-Health Index hero (not a FICO), annotated history chart, 3 alert cards, next-move cards and utilization meter, three bureau tiles, collapsed full report. Embedded `DATA` is synthetic "Jordan Example" only. |
| `example_bundle.json` | PII-scrubbed bundle shape produced by `credit_weekly.cli export-dashboard`. |
| `index.html` + `data.js` | Offline local viewer (secondary UX). |

## How the weekly skill uses it
1. Parse / diff / optimize, then export a scrubbed bundle.
2. Copy the structure of `ExampleDashboard.canvas.tsx`.
3. Replace `DATA` with that week's bundle. Keep `is_example_data: false` on real pages.
4. If `<store>/canvas_id.txt` exists, `WriteCanvas` that id. Otherwise create a **new** private Page in the owner's Library and save the new id.
5. Never overwrite the public Blueprint Page (`1efc1c3f-a5c5-4ed8-9edc-1e45c4ea07e4`).
6. Never put SSN, full DOB, passwords, or full account numbers on the Page. Never imitate a bureau's official UI. No `<form>`.

The Blueprint Page is the product/architecture write-up, not a user's monitor dashboard.

## Consumer layout
The Page is a simple, wide consumer dashboard, not a data dump:

1. Hero with one Credit-Health Index number, a one-word band, week-over-week change, and a small "Not a FICO score" note, then a history LineChart with a 4-week / 12-week / All range and an annotation on a new-inquiry week.
2. "This week" — at most three plain-English alert cards with Status pills; the rest behind "See all changes".
3. "Your next move" — one to three optimizer action cards (pay-by dates and amounts) and a utilization band meter (0 / 1–9 / 10–20 / 21–29 / 30+).
4. Three bureau tiles (Equifax, Experian, TransUnion) with utilization, on-time %, inquiries, negatives, and last updated.
5. "See full report" at the bottom, collapsed by default: a bureau Segmented switch and a clean account list.

Copy stays short, warm, and plain. Do not add accordion tabs or raw multi-table drill-downs.
