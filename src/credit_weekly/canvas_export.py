"""Export PII-minimized weekly credit snapshot + diff into Grok Page (.canvas.tsx) and dashboard data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BUREAUS, BUREAU_LABELS


def _fmt_usd(cents: int | None) -> str:
    if cents is None:
        return "—"
    return f"${cents / 100:,.0f}" if cents % 100 == 0 else f"${cents / 100:,.2f}"


def build_dashboard_bundle(
    snapshots: list[dict[str, Any]],
    latest_diff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a strictly PII-scrubbed bundle safe for Grok Page (Canvas) or local UI."""
    ordered = sorted(snapshots, key=lambda s: s.get("captured_at", ""))
    latest = ordered[-1]
    history_points = [
        {
            "week": s.get("week_label", ""),
            "utilization_pct": s.get("health_summary", {}).get("utilization_pct", 0.0),
            "revolving_balance_usd": round(
                (s.get("health_summary", {}).get("revolving_balance_cents", 0) or 0) / 100.0, 2
            ),
            "adverse_accounts": s.get("health_summary", {}).get("adverse_accounts", 0),
        }
        for s in ordered
    ]

    bureau_cards = []
    accounts_flat = []
    inquiries_flat = []
    collections_flat = []
    public_records_flat = []
    personal_rows = []

    for b_key in BUREAUS:
        rep = latest.get("bureaus", {}).get(b_key)
        if not rep:
            continue
        label = BUREAU_LABELS[b_key]
        accts = rep.get("accounts", [])
        cols = rep.get("collections", [])
        inqs = rep.get("inquiries", [])
        prs = rep.get("public_records", [])
        rev_bal = sum((a.get("balance_cents") or 0) for a in accts if a.get("kind") == "revolving" and a.get("is_open"))
        rev_lim = sum((a.get("credit_limit_cents") or 0) for a in accts if a.get("kind") == "revolving" and a.get("is_open"))
        util = round((rev_bal / rev_lim) * 100, 1) if rev_lim > 0 else 0.0

        bureau_cards.append(
            {
                "bureau": b_key,
                "label": label,
                "report_date": rep.get("source", {}).get("report_date", ""),
                "confidence": rep.get("source", {}).get("confidence", 0),
                "open_accounts": sum(1 for a in accts if a.get("is_open")),
                "total_accounts": len(accts),
                "utilization_pct": util,
                "revolving_balance_usd": _fmt_usd(rev_bal),
                "revolving_limit_usd": _fmt_usd(rev_lim),
                "adverse_count": sum(1 for a in accts if a.get("is_adverse")) + len(cols),
                "hard_inquiries": sum(1 for q in inqs if q.get("kind") == "hard"),
            }
        )

        for a in accts:
            bal = a.get("balance_cents")
            lim = a.get("credit_limit_cents")
            acct_util = f"{round((bal / lim) * 100)}%" if (bal is not None and lim and lim > 0) else "—"
            accounts_flat.append(
                {
                    "bureau": b_key,
                    "bureau_label": label,
                    "creditor": a.get("creditor", ""),
                    "masked": a.get("account_number_masked", "****"),
                    "kind": a.get("kind", "other"),
                    "status": a.get("status", ""),
                    "is_open": bool(a.get("is_open")),
                    "is_adverse": bool(a.get("is_adverse")),
                    "balance": _fmt_usd(bal),
                    "balance_cents": bal or 0,
                    "limit": _fmt_usd(lim),
                    "limit_cents": lim or 0,
                    "util": acct_util,
                    "opened": a.get("opened", ""),
                    "updated": a.get("updated", ""),
                }
            )

        for c in cols:
            collections_flat.append(
                {
                    "bureau": b_key,
                    "bureau_label": label,
                    "creditor": c.get("creditor", ""),
                    "masked": c.get("account_number_masked", "****"),
                    "original_creditor": c.get("original_creditor", "—"),
                    "balance": _fmt_usd(c.get("balance_cents")),
                    "status": c.get("status", ""),
                    "dofd": c.get("dofd", "—"),
                }
            )

        for q in inqs:
            inquiries_flat.append(
                {
                    "bureau": b_key,
                    "bureau_label": label,
                    "creditor": q.get("creditor", ""),
                    "date": q.get("date", ""),
                    "kind": q.get("kind", "hard"),
                    "purpose": q.get("permissible_purpose", ""),
                }
            )

        for pr in prs:
            public_records_flat.append(
                {
                    "bureau": b_key,
                    "bureau_label": label,
                    "kind": pr.get("kind", ""),
                    "filed_date": pr.get("filed_date", ""),
                    "status": pr.get("status", ""),
                }
            )

        pi = rep.get("personal_info", {})
        personal_rows.append(
            {
                "bureau": b_key,
                "bureau_label": label,
                "names": ", ".join(pi.get("names", [])) or "—",
                "ssn_last4": f"***-**-{pi['ssn_last4']}" if pi.get("ssn_last4") else "—",
                "dob_year": pi.get("dob_year") or "—",
                "addresses": "; ".join(a.get("text", "") for a in pi.get("addresses", [])) or "—",
                "employers": ", ".join(pi.get("employers", [])) or "—",
            }
        )

    hs = latest.get("health_summary", {})
    return {
        "week_label": latest.get("week_label", ""),
        "captured_at": latest.get("captured_at", ""),
        "is_example_data": bool(latest.get("is_example_data", False)),
        "health_summary": {
            "utilization_pct": hs.get("utilization_pct", 0.0),
            "on_time_history_pct": hs.get("on_time_history_pct", 100.0),
            "open_accounts": hs.get("open_accounts", 0),
            "total_accounts": hs.get("total_accounts", 0),
            "revolving_balance_usd": _fmt_usd(hs.get("revolving_balance_cents")),
            "revolving_limit_usd": _fmt_usd(hs.get("revolving_limit_cents")),
            "adverse_accounts": hs.get("adverse_accounts", 0),
            "collections_count": hs.get("collections_count", 0),
            "hard_inquiries_24m": hs.get("hard_inquiries_24m", 0),
            "public_records_count": hs.get("public_records_count", 0),
        },
        "history": history_points,
        "bureaus": bureau_cards,
        "alerts": (latest_diff or {}).get("alerts", []),
        "metric_deltas": (latest_diff or {}).get("metric_deltas", {}),
        "accounts": accounts_flat,
        "collections": collections_flat,
        "inquiries": inquiries_flat,
        "public_records": public_records_flat,
        "personal_info": personal_rows,
    }


def render_canvas_tsx(bundle: dict[str, Any]) -> str:
    """Emit a self-contained grok/canvas .tsx page from the PII-scrubbed bundle."""
    data_json = json.dumps(bundle, indent=2, ensure_ascii=False)
    return f'''import {{
  Bars,
  Callout,
  Input,
  LineChart,
  Metrics,
  Page,
  Rows,
  Section,
  Segmented,
  Select,
  Table,
  Text,
  useMemo,
  useState,
}} from "grok/canvas";

type BureauKey = "all" | "experian" | "equifax" | "transunion";
type ViewTab = "overview" | "accounts" | "inquiries" | "derogatory" | "personal";

const DATA = {data_json} as const;

export default function App() {{
  const [bureau, setBureau] = useState<BureauKey>("all");
  const [tab, setTab] = useState<ViewTab>("overview");
  const [query, setQuery] = useState<string>("");
  const [kindFilter, setKindFilter] = useState<string>("all");

  const hs = DATA.health_summary;
  const utilTone =
    hs.utilization_pct <= 10 ? "success" : hs.utilization_pct <= 30 ? "warning" : "danger";
  const advTone =
    hs.adverse_accounts + hs.collections_count === 0 ? "success" : "danger";

  const filteredAccounts = useMemo(() => {{
    const q = query.trim().toLowerCase();
    return DATA.accounts.filter((a) => {{
      if (bureau !== "all" && a.bureau !== bureau) return false;
      if (kindFilter !== "all" && a.kind !== kindFilter) return false;
      if (q && !a.creditor.toLowerCase().includes(q) && !a.status.toLowerCase().includes(q)) {{
        return false;
      }}
      return true;
    }});
  }}, [bureau, kindFilter, query]);

  const filteredInquiries = useMemo(() => {{
    const q = query.trim().toLowerCase();
    return DATA.inquiries.filter((iq) => {{
      if (bureau !== "all" && iq.bureau !== bureau) return false;
      if (q && !iq.creditor.toLowerCase().includes(q)) return false;
      return true;
    }});
  }}, [bureau, query]);

  const filteredCollections = useMemo(() => {{
    return DATA.collections.filter((c) => bureau === "all" || c.bureau === bureau);
  }}, [bureau]);

  const filteredPublic = useMemo(() => {{
    return DATA.public_records.filter((p) => bureau === "all" || p.bureau === bureau);
  }}, [bureau]);

  const filteredPersonal = useMemo(() => {{
    return DATA.personal_info.filter((p) => bureau === "all" || p.bureau === bureau);
  }}, [bureau]);

  const utilPoints = DATA.history.map((h) => ({{
    label: h.week,
    value: h.utilization_pct,
  }}));

  const bureauBars = DATA.bureaus.map((b) => ({{
    label: b.label,
    value: b.utilization_pct,
    display: `${{b.utilization_pct}}%`,
    meta: `${{b.revolving_balance_usd}} / ${{b.revolving_limit_usd}}`,
  }}));

  return (
    <Page
      title={{`3-Bureau Credit Monitor — ${{DATA.week_label}}`}}
      summary="Weekly AnnualCreditReport.com snapshot across Equifax, Experian, and TransUnion. Score-free report health, utilization, and week-over-week change alerts."
      width="wide"
    >
      <Metrics
        metrics={{[
          {{
            value: `${{hs.utilization_pct}}%`,
            label: "Revolving Utilization",
            detail: `${{hs.revolving_balance_usd}} of ${{hs.revolving_limit_usd}}`,
            tone: utilTone,
          }},
          {{
            value: `${{hs.on_time_history_pct}}%`,
            label: "On-Time Payments",
            detail: `${{hs.open_accounts}} open / ${{hs.total_accounts}} total`,
            tone: hs.on_time_history_pct >= 99 ? "success" : "warning",
          }},
          {{
            value: `${{hs.hard_inquiries_24m}}`,
            label: "Hard Inquiries",
            detail: "Across loaded bureaus",
          }},
          {{
            value: `${{hs.adverse_accounts + hs.collections_count}}`,
            label: "Adverse & Collections",
            detail: `${{hs.collections_count}} collections · ${{hs.public_records_count}} public`,
            tone: advTone,
          }},
        ]}}
      />

      <Section heading="Scope & View">
        <Segmented<BureauKey>
          options={{[
            {{ value: "all", label: "All 3 Bureaus" }},
            {{ value: "experian", label: "Experian" }},
            {{ value: "equifax", label: "Equifax" }},
            {{ value: "transunion", label: "TransUnion" }},
          ]}}
          value={{bureau}}
          onChange={{(v: BureauKey) => setBureau(v)}}
        />
        <Segmented<ViewTab>
          options={{[
            {{ value: "overview", label: "Overview & Alerts", count: DATA.alerts.length }},
            {{ value: "accounts", label: "Accounts", count: filteredAccounts.length }},
            {{ value: "inquiries", label: "Inquiries", count: filteredInquiries.length }},
            {{ value: "derogatory", label: "Collections & Public", count: filteredCollections.length + filteredPublic.length }},
            {{ value: "personal", label: "Personal Info", count: filteredPersonal.length }},
          ]}}
          value={{tab}}
          onChange={{(v: ViewTab) => setTab(v)}}
        />
      </Section>

      {{tab === "overview" && (
        <>
          {{DATA.alerts.length > 0 && (
            <Section heading="What Changed This Week" caption="Week-over-week structural diff across bureaus">
              <Rows
                rows={{DATA.alerts.map((al) => ({{
                  title: al.title,
                  detail: al.detail,
                  status: {{
                    label: al.severity.toUpperCase(),
                    tone: al.severity === "critical" ? "danger" : al.severity === "warning" ? "warning" : "success",
                  }},
                }}))}}
              />
            </Section>
          )}}

          {{bureauBars.length > 0 && (
            <Section heading="Utilization by Bureau" caption="Revolving balance divided by total revolving limit per bureau">
              <Bars bars={{bureauBars}} />
            </Section>
          )}}

          {{utilPoints.length > 1 && (
            <Section heading="Weekly Utilization Trend">
              <LineChart
                points={{utilPoints}}
                ceiling={{Math.max(40, ...utilPoints.map((p) => p.value + 5))}}
                floor={{0}}
                unit="%"
                labels={{["Utilization %"]}}
              />
            </Section>
          )}}

          <Section heading="Bureau Snapshot Status">
            <Table
              columns={{["Bureau", "Report Date", "Open / Total", "Utilization", "Adverse", "Hard Inq", "Parse Confidence"]}}
              align={{["start", "start", "end", "end", "end", "end", "end"]}}
              rows={{DATA.bureaus.map((b) => [
                b.label,
                b.report_date || "—",
                `${{b.open_accounts}} / ${{b.total_accounts}}`,
                `${{b.utilization_pct}}%`,
                {{ text: `${{b.adverse_count}}`, tone: b.adverse_count > 0 ? "danger" : "success" }},
                `${{b.hard_inquiries}}`,
                `${{b.confidence}}%`,
              ])}}
            />
          </Section>
        </>
      )}}

      {{tab === "accounts" && (
        <Section heading="Tradelines & Balances">
          <Input
            label="Filter creditor or status"
            value={{query}}
            onChange={{(val: string) => setQuery(val)}}
            placeholder="Search bank, card, status..."
          />
          <Select<string>
            label="Account Type"
            value={{kindFilter}}
            onChange={{(val: string) => setKindFilter(val)}}
            options={{[
              {{ value: "all", label: "All Types" }},
              {{ value: "revolving", label: "Revolving" }},
              {{ value: "installment", label: "Installment" }},
              {{ value: "mortgage", label: "Mortgage" }},
            ]}}
          />
          {{filteredAccounts.length > 0 && (
            <Table
              columns={{["Bureau", "Creditor", "Acct", "Type", "Status", "Balance", "Limit", "Util"]}}
              align={{["start", "start", "start", "start", "start", "end", "end", "end"]}}
              rows={{filteredAccounts.map((a) => [
                a.bureau_label,
                a.creditor,
                a.masked,
                a.kind,
                {{ text: a.status, tone: a.is_adverse ? "danger" : "success" }},
                a.balance,
                a.limit,
                a.util,
              ])}}
            />
          )}}
        </Section>
      )}}

      {{tab === "inquiries" && filteredInquiries.length > 0 && (
        <Section heading="Credit Inquiries" caption="Hard inquiries affect credit decisions; promotional/account review are soft">
          <Input
            label="Filter inquiry"
            value={{query}}
            onChange={{(val: string) => setQuery(val)}}
            placeholder="Search creditor..."
          />
          <Table
            columns={{["Bureau", "Creditor", "Date", "Type", "Permissible Purpose"]}}
            rows={{filteredInquiries.map((q) => [
              q.bureau_label,
              q.creditor,
              q.date,
              {{ text: q.kind, tone: q.kind === "hard" ? "warning" : "success" }},
              q.purpose || "—",
            ])}}
          />
        </Section>
      )}}

      {{tab === "derogatory" && (
        <>
          {{filteredCollections.length > 0 && (
            <Section heading="Collections">
              <Table
                columns={{["Bureau", "Agency", "Acct", "Original Creditor", "Balance", "Status", "DOFD"]}}
                align={{["start", "start", "start", "start", "end", "start", "start"]}}
                rows={{filteredCollections.map((c) => [
                  c.bureau_label,
                  c.creditor,
                  c.masked,
                  c.original_creditor,
                  c.balance,
                  {{ text: c.status, tone: "danger" }},
                  c.dofd,
                ])}}
              />
            </Section>
          )}}
          {{filteredPublic.length > 0 && (
            <Section heading="Public Records">
              <Table
                columns={{["Bureau", "Type", "Filed", "Status"]}}
                rows={{filteredPublic.map((p) => [
                  p.bureau_label,
                  p.kind,
                  p.filed_date,
                  {{ text: p.status, tone: "danger" }},
                ])}}
              />
            </Section>
          )}}
          {{filteredCollections.length === 0 && filteredPublic.length === 0 && (
            <Callout tone="success" lead="Clean derogatory check">
              Zero collections or public records appear in the selected bureau scope for ${{DATA.week_label}}.
            </Callout>
          )}}
        </>
      )}}

      {{tab === "personal" && filteredPersonal.length > 0 && (
        <Section heading="Personal Information (PII-Minimized)">
          <Table
            columns={{["Bureau", "Names", "SSN (Masked)", "Birth Year", "Addresses", "Employers"]}}
            rows={{filteredPersonal.map((p) => [
              p.bureau_label,
              p.names,
              p.ssn_last4,
              p.dob_year,
              p.addresses,
              p.employers,
            ])}}
          />
        </Section>
      )}}
    </Page>
  );
}}
'''
