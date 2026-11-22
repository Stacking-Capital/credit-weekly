# Dashboard Page template

This folder is the **summary-first Grok Page template** the weekly skill writes or updates for each owner.

| File | Role |
|---|---|
| `ExampleDashboard.canvas.tsx` | Canonical consumer layout for Stage 1: a strong Credit-Health Index hero (not a FICO), an annotated history chart, a clear "What to do this week" focus, a utilization meter, three bureau tiles, and a full report one tap away. Embedded `DATA` is synthetic "Jordan Example" only. |
| `DreamStateDashboard.canvas.tsx` | Dream-state consumer layout once Stages 1-3 are on: three FICO Score 8 tiles labeled with model and bureau, annotated 3-bureau score history, key factors, alerts, the same next-move focus, utilization meter, bureau tiles, a quiet VantageScore 3.0 row, and a collapsed full report. Synthetic "Jordan Example" only. Do not use this as the Stage 1 template. |
| `example_bundle.json` | PII-scrubbed bundle shape produced by `credit_weekly.cli export-dashboard`. |
| `index.html` + `data.js` | Offline local viewer (secondary UX). |

## How the weekly skill uses it
1. Parse / diff / optimize, then export a scrubbed bundle.
2. Copy the structure of `ExampleDashboard.canvas.tsx`.
3. Replace `DATA` with that week's bundle. Keep `is_example_data: false` on real owner pages. Set `page_state` to `ready` on the finished write. Use `updating` only as a brief in-place revision if a pull will take a while; otherwise leave last week's ready Page in place until the new bundle is ready, then write once.
4. If `<store>/canvas_id.txt` exists, `WriteCanvas` **that same id** so the owner's Page URL does not change. Never create a second dashboard for the same owner. If the file is missing (first run), create a **new** private Page in the owner's Library and save the new id only in their store.
5. Never overwrite the public Blueprint Page (`1efc1c3f-a5c5-4ed8-9edc-1e45c4ea07e4`), the Stage 1 example Page (`a669f6e0-1cb8-4435-a852-d8388d8d0880`), or the dream-state example Page (`15e9c3b4-0c70-4bdc-9ad0-ff712e3e4585`).
6. Never put SSN, full DOB, passwords, or full account numbers on the Page. Never imitate a bureau's official UI. No `<form>`.

The Blueprint Page is the product/architecture write-up, not a user's monitor dashboard.

## Consumer layout
The Page is a simple, wide consumer dashboard, not a data dump:

1. Hero with one large Credit-Health Index number (tabular figures), a one-word band, week-over-week change, an "As of" date, and a small "Not a FICO score" note, then a history LineChart with a 4-week / 12-week / All range when at least four weeks exist. The chart scale starts near the data (never a flat 0-100 view that hides the move). The Jordan Example chart uses 12 synthetic weeks, with annotations on the paydown and the new-inquiry week. If this is the first week, show the hero and the calm empty line "Your history will build here after the next weekly pull."
2. "What to do this week" is the action focus: one lead Callout from the optimizer, any other moves as rows, and a utilization band meter (0 / 1-9 / 10-20 / 21-29 / 30+). If there is nothing to do, use the good-shape empty copy. Do not promise a point gain.
3. "This week" - up to three plain-English changes as rows with Status labels; the rest behind "See all changes". A quiet week uses the quiet-week empty copy.
4. Three bureau tiles (Equifax, Experian, TransUnion) with utilization, on-time %, inquiries, negatives, and last updated.
5. "See full report" at the bottom, collapsed by default (one tap opens it): a bureau Segmented switch and a clean account list.

Copy stays short, warm, and plain. No em dashes. Example Pages always carry a visible example-data label.
