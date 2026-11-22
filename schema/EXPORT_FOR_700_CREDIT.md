# Versioned export for 700.credit (Stage 1)

Credit Weekly is a standalone bot. Stage 1's weekly 3-bureau ACR (or bureau-account) parse is also a clean import source for Stacking's separate [700.credit](https://app.700.credit) platform. This is an export contract, not a front-door integration.

## Bundle (versioned)
Each pull should be able to emit a folder (or zip) named `credit-weekly-export-v1-<YYYY-MM-DD>/` containing:

| File | Contents |
|---|---|
| `manifest.json` | `export_format`: `credit-weekly-export`, `format_version`: `1.0.0`, `schema_version`: `1.0.0` (CreditSnapshot), `captured_at`, `week_label`, `sources` (acr / bureau-account), `bureaus_present`, `includes_scores` (false for a pure Stage 1 pack) |
| `snapshot.json` | PII-minimized CreditSnapshot (`schema/credit_snapshot.schema.json`, `schema_version` `1.0.0`): tradelines, inquiries, collections, public records, utilization, masked account numbers (`****1234`), `ssn_last4` only if already present, no full SSN or full DOB |
| `diff.json` | Optional week-over-week diff if a prior snapshot exists |
| `pdf/equifax.pdf`, `pdf/experian.pdf`, `pdf/transunion.pdf` | The official report PDFs from that pull, if the user chooses to include them |

700.credit's current parser is built around HTML monitoring reports (MyScoreIQ / IdentityIQ). This export is a stable, versioned JSON + PDF pack those tools can be taught to ingest later. Bump `format_version` when the manifest or snapshot shape changes; do not silently break `1.0.0`.

Never email the pack unencrypted. Leave it in the owner's private bot store unless they ask to download it.
