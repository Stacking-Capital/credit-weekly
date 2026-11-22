import {
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
} from "grok/canvas";

type BureauKey = "all" | "experian" | "equifax" | "transunion";
type ViewTab = "overview" | "accounts" | "inquiries" | "derogatory" | "personal";

const DATA = {
  "week_label": "2026-W47",
  "captured_at": "2026-11-22T00:46:53.890193+00:00",
  "is_example_data": true,
  "health_summary": {
    "utilization_pct": 7.9,
    "on_time_history_pct": 100.0,
    "open_accounts": 3,
    "total_accounts": 3,
    "revolving_balance_usd": "$1,350",
    "revolving_limit_usd": "$17,000",
    "adverse_accounts": 1,
    "collections_count": 0,
    "hard_inquiries_24m": 3,
    "public_records_count": 0
  },
  "history": [
    {
      "week": "2026-W46",
      "utilization_pct": 16.7,
      "revolving_balance_usd": 2500.0,
      "adverse_accounts": 1
    },
    {
      "week": "2026-W47",
      "utilization_pct": 7.9,
      "revolving_balance_usd": 1350.0,
      "adverse_accounts": 1
    }
  ],
  "bureaus": [
    {
      "bureau": "equifax",
      "label": "Equifax",
      "report_date": "2026-11-16",
      "confidence": 65,
      "open_accounts": 2,
      "total_accounts": 2,
      "utilization_pct": 7.9,
      "revolving_balance_usd": "$1,350",
      "revolving_limit_usd": "$17,000",
      "adverse_count": 0,
      "hard_inquiries": 0
    },
    {
      "bureau": "experian",
      "label": "Experian",
      "report_date": "2026-11-16",
      "confidence": 65,
      "open_accounts": 3,
      "total_accounts": 3,
      "utilization_pct": 7.9,
      "revolving_balance_usd": "$1,350",
      "revolving_limit_usd": "$17,000",
      "adverse_count": 3,
      "hard_inquiries": 1
    },
    {
      "bureau": "transunion",
      "label": "TransUnion",
      "report_date": "2026-11-16",
      "confidence": 100,
      "open_accounts": 0,
      "total_accounts": 3,
      "utilization_pct": 0.0,
      "revolving_balance_usd": "$0",
      "revolving_limit_usd": "$0",
      "adverse_count": 0,
      "hard_inquiries": 2
    }
  ],
  "alerts": [
    {
      "severity": "warning",
      "bureau": "transunion",
      "category": "new_hard_inquiry",
      "title": "New hard inquiry on TransUnion: HARBOR PREMIER BANK",
      "detail": "Date: 2026-11-14."
    },
    {
      "severity": "info",
      "bureau": "equifax",
      "category": "balance_change",
      "title": "Equifax: SUMMIT BANK NA balance decreased by $900",
      "detail": "$1,850 -> $950 (****1234)."
    },
    {
      "severity": "info",
      "bureau": "equifax",
      "category": "limit_change",
      "title": "Equifax: SUMMIT BANK NA credit limit changed",
      "detail": "$10,000 -> $12,000."
    },
    {
      "severity": "info",
      "bureau": "equifax",
      "category": "balance_change",
      "title": "Equifax: NORTHSTAR CREDIT UNION balance decreased by $250",
      "detail": "$650 -> $400 (****5678)."
    },
    {
      "severity": "info",
      "bureau": "experian",
      "category": "balance_change",
      "title": "Experian: SUMMIT BANK NA balance decreased by $900",
      "detail": "$1,850 -> $950 (****1234)."
    },
    {
      "severity": "info",
      "bureau": "experian",
      "category": "limit_change",
      "title": "Experian: SUMMIT BANK NA credit limit changed",
      "detail": "$10,000 -> $12,000."
    },
    {
      "severity": "info",
      "bureau": "experian",
      "category": "balance_change",
      "title": "Experian: NORTHSTAR CREDIT UNION balance decreased by $250",
      "detail": "$650 -> $400 (****5678)."
    },
    {
      "severity": "info",
      "bureau": "experian",
      "category": "balance_change",
      "title": "Experian: CASCADIA AUTO FINANCE balance decreased by $350",
      "detail": "$11,400 -> $11,050 (****9012)."
    },
    {
      "severity": "info",
      "bureau": "transunion",
      "category": "balance_change",
      "title": "TransUnion: SUMMIT BANK NA balance decreased by $900",
      "detail": "$1,850 -> $950 (****1234)."
    },
    {
      "severity": "info",
      "bureau": "transunion",
      "category": "balance_change",
      "title": "TransUnion: NORTHSTAR CREDIT UNION balance decreased by $250",
      "detail": "$650 -> $400 (****5678)."
    },
    {
      "severity": "info",
      "bureau": "transunion",
      "category": "balance_change",
      "title": "TransUnion: CASCADIA AUTO FINANCE balance decreased by $350",
      "detail": "$11,400 -> $11,050 (****9012)."
    }
  ],
  "metric_deltas": {
    "revolving_balance_delta_cents": -115000,
    "revolving_limit_delta_cents": 200000,
    "utilization_delta_pct": -8.8,
    "adverse_delta": 0,
    "collections_delta": 0,
    "hard_inquiries_delta": 1
  },
  "accounts": [
    {
      "bureau": "equifax",
      "bureau_label": "Equifax",
      "creditor": "SUMMIT BANK NA",
      "masked": "****1234",
      "kind": "revolving",
      "status": "Pays as Agreed",
      "is_open": true,
      "is_adverse": false,
      "balance": "$950",
      "balance_cents": 95000,
      "limit": "$12,000",
      "limit_cents": 1200000,
      "util": "8%",
      "opened": "2021-04-15",
      "updated": "2026-11-12"
    },
    {
      "bureau": "equifax",
      "bureau_label": "Equifax",
      "creditor": "NORTHSTAR CREDIT UNION",
      "masked": "****5678",
      "kind": "revolving",
      "status": "Pays as Agreed",
      "is_open": true,
      "is_adverse": false,
      "balance": "$400",
      "balance_cents": 40000,
      "limit": "$5,000",
      "limit_cents": 500000,
      "util": "8%",
      "opened": "2022-08-01",
      "updated": "2026-11-11"
    },
    {
      "bureau": "experian",
      "bureau_label": "Experian",
      "creditor": "SUMMIT BANK NA",
      "masked": "****1234",
      "kind": "revolving",
      "status": "Open / Never Late",
      "is_open": true,
      "is_adverse": true,
      "balance": "$950",
      "balance_cents": 95000,
      "limit": "$12,000",
      "limit_cents": 1200000,
      "util": "8%",
      "opened": "2021-04-15",
      "updated": "2026-11-12"
    },
    {
      "bureau": "experian",
      "bureau_label": "Experian",
      "creditor": "NORTHSTAR CREDIT UNION",
      "masked": "****5678",
      "kind": "revolving",
      "status": "Open / Never Late",
      "is_open": true,
      "is_adverse": true,
      "balance": "$400",
      "balance_cents": 40000,
      "limit": "$5,000",
      "limit_cents": 500000,
      "util": "8%",
      "opened": "2022-08-01",
      "updated": "2026-11-11"
    },
    {
      "bureau": "experian",
      "bureau_label": "Experian",
      "creditor": "CASCADIA AUTO FINANCE",
      "masked": "****9012",
      "kind": "installment",
      "status": "Open / Never Late",
      "is_open": true,
      "is_adverse": true,
      "balance": "$11,050",
      "balance_cents": 1105000,
      "limit": "—",
      "limit_cents": 0,
      "util": "—",
      "opened": "2024-02-10",
      "updated": "2026-11-10"
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "creditor": "SUMMIT BANK NA",
      "masked": "****1234",
      "kind": "revolving",
      "status": "Paid or Paying as Agreed",
      "is_open": false,
      "is_adverse": false,
      "balance": "$950",
      "balance_cents": 95000,
      "limit": "$10,000",
      "limit_cents": 1000000,
      "util": "10%",
      "opened": "2021-04-15",
      "updated": "2026-11-12"
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "creditor": "NORTHSTAR CREDIT UNION",
      "masked": "****5678",
      "kind": "revolving",
      "status": "Paid or Paying as Agreed",
      "is_open": false,
      "is_adverse": false,
      "balance": "$400",
      "balance_cents": 40000,
      "limit": "$5,000",
      "limit_cents": 500000,
      "util": "8%",
      "opened": "2022-08-01",
      "updated": "2026-11-11"
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "creditor": "CASCADIA AUTO FINANCE",
      "masked": "****9012",
      "kind": "installment",
      "status": "Paid or Paying as Agreed",
      "is_open": false,
      "is_adverse": false,
      "balance": "$11,050",
      "balance_cents": 1105000,
      "limit": "—",
      "limit_cents": 0,
      "util": "—",
      "opened": "2024-02-10",
      "updated": "2026-11-10"
    }
  ],
  "collections": [],
  "inquiries": [
    {
      "bureau": "experian",
      "bureau_label": "Experian",
      "creditor": "HARBOR MORTGAGE PREQUAL",
      "date": "2026-04-02",
      "kind": "hard",
      "purpose": ""
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "creditor": "NORTHSTAR CREDIT UNION",
      "date": "2026-06-12",
      "kind": "hard",
      "purpose": "Credit Application"
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "creditor": "HARBOR PREMIER BANK",
      "date": "2026-11-14",
      "kind": "hard",
      "purpose": "Credit Card Application"
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "creditor": "EXAMPLE CARD OFFERS LLC",
      "date": "2026-10-20",
      "kind": "promotional",
      "purpose": "Promotional"
    }
  ],
  "public_records": [],
  "personal_info": [
    {
      "bureau": "equifax",
      "bureau_label": "Equifax",
      "names": "Jordan Example",
      "ssn_last4": "***-**-0000",
      "dob_year": "1990",
      "addresses": "100 Maple Ave, Austin, TX 78701",
      "employers": "—"
    },
    {
      "bureau": "experian",
      "bureau_label": "Experian",
      "names": "Jordan Example",
      "ssn_last4": "***-**-0000",
      "dob_year": "1990",
      "addresses": "100 Maple Ave, Austin, TX 78701",
      "employers": "—"
    },
    {
      "bureau": "transunion",
      "bureau_label": "TransUnion",
      "names": "Jordan Example",
      "ssn_last4": "***-**-0000",
      "dob_year": "1990",
      "addresses": "100 Maple Ave, Austin, TX 78701",
      "employers": "ACME EXAMPLE CORP"
    }
  ]
} as const;

export default function App() {
  const [bureau, setBureau] = useState<BureauKey>("all");
  const [tab, setTab] = useState<ViewTab>("overview");
  const [query, setQuery] = useState<string>("");
  const [kindFilter, setKindFilter] = useState<string>("all");

  const hs = DATA.health_summary;
  const utilTone =
    hs.utilization_pct <= 10 ? "success" : hs.utilization_pct <= 30 ? "warning" : "danger";
  const advTone =
    hs.adverse_accounts + hs.collections_count === 0 ? "success" : "danger";

  const filteredAccounts = useMemo(() => {
    const q = query.trim().toLowerCase();
    return DATA.accounts.filter((a) => {
      if (bureau !== "all" && a.bureau !== bureau) return false;
      if (kindFilter !== "all" && a.kind !== kindFilter) return false;
      if (q && !a.creditor.toLowerCase().includes(q) && !a.status.toLowerCase().includes(q)) {
        return false;
      }
      return true;
    });
  }, [bureau, kindFilter, query]);

  const filteredInquiries = useMemo(() => {
    const q = query.trim().toLowerCase();
    return DATA.inquiries.filter((iq) => {
      if (bureau !== "all" && iq.bureau !== bureau) return false;
      if (q && !iq.creditor.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [bureau, query]);

  const filteredCollections = useMemo(() => {
    return DATA.collections.filter((c) => bureau === "all" || c.bureau === bureau);
  }, [bureau]);

  const filteredPublic = useMemo(() => {
    return DATA.public_records.filter((p) => bureau === "all" || p.bureau === bureau);
  }, [bureau]);

  const filteredPersonal = useMemo(() => {
    return DATA.personal_info.filter((p) => bureau === "all" || p.bureau === bureau);
  }, [bureau]);

  const utilPoints = DATA.history.map((h) => ({
    label: h.week,
    value: h.utilization_pct,
  }));

  const bureauBars = DATA.bureaus.map((b) => ({
    label: b.label,
    value: b.utilization_pct,
    display: `${b.utilization_pct}%`,
    meta: `${b.revolving_balance_usd} / ${b.revolving_limit_usd}`,
  }));

  return (
    <Page
      title={`3-Bureau Credit Monitor — ${DATA.week_label}`}
      summary="Weekly AnnualCreditReport.com snapshot across Equifax, Experian, and TransUnion. Score-free report health, utilization, and week-over-week change alerts."
      width="wide"
    >
      <Metrics
        metrics={[
          {
            value: `${hs.utilization_pct}%`,
            label: "Revolving Utilization",
            detail: `${hs.revolving_balance_usd} of ${hs.revolving_limit_usd}`,
            tone: utilTone,
          },
          {
            value: `${hs.on_time_history_pct}%`,
            label: "On-Time Payments",
            detail: `${hs.open_accounts} open / ${hs.total_accounts} total`,
            tone: hs.on_time_history_pct >= 99 ? "success" : "warning",
          },
          {
            value: `${hs.hard_inquiries_24m}`,
            label: "Hard Inquiries",
            detail: "Across loaded bureaus",
          },
          {
            value: `${hs.adverse_accounts + hs.collections_count}`,
            label: "Adverse & Collections",
            detail: `${hs.collections_count} collections · ${hs.public_records_count} public`,
            tone: advTone,
          },
        ]}
      />

      <Section heading="Scope & View">
        <Segmented<BureauKey>
          options={[
            { value: "all", label: "All 3 Bureaus" },
            { value: "experian", label: "Experian" },
            { value: "equifax", label: "Equifax" },
            { value: "transunion", label: "TransUnion" },
          ]}
          value={bureau}
          onChange={(v: BureauKey) => setBureau(v)}
        />
        <Segmented<ViewTab>
          options={[
            { value: "overview", label: "Overview & Alerts", count: DATA.alerts.length },
            { value: "accounts", label: "Accounts", count: filteredAccounts.length },
            { value: "inquiries", label: "Inquiries", count: filteredInquiries.length },
            { value: "derogatory", label: "Collections & Public", count: filteredCollections.length + filteredPublic.length },
            { value: "personal", label: "Personal Info", count: filteredPersonal.length },
          ]}
          value={tab}
          onChange={(v: ViewTab) => setTab(v)}
        />
      </Section>

      {tab === "overview" && (
        <>
          {DATA.alerts.length > 0 && (
            <Section heading="What Changed This Week" caption="Week-over-week structural diff across bureaus">
              <Rows
                rows={DATA.alerts.map((al) => ({
                  title: al.title,
                  detail: al.detail,
                  status: {
                    label: al.severity.toUpperCase(),
                    tone: al.severity === "critical" ? "danger" : al.severity === "warning" ? "warning" : "success",
                  },
                }))}
              />
            </Section>
          )}

          {bureauBars.length > 0 && (
            <Section heading="Utilization by Bureau" caption="Revolving balance divided by total revolving limit per bureau">
              <Bars bars={bureauBars} />
            </Section>
          )}

          {utilPoints.length > 1 && (
            <Section heading="Weekly Utilization Trend">
              <LineChart
                points={utilPoints}
                ceiling={Math.max(40, ...utilPoints.map((p) => p.value + 5))}
                floor={0}
                unit="%"
                labels={["Utilization %"]}
              />
            </Section>
          )}

          <Section heading="Bureau Snapshot Status">
            <Table
              columns={["Bureau", "Report Date", "Open / Total", "Utilization", "Adverse", "Hard Inq", "Parse Confidence"]}
              align={["start", "start", "end", "end", "end", "end", "end"]}
              rows={DATA.bureaus.map((b) => [
                b.label,
                b.report_date || "—",
                `${b.open_accounts} / ${b.total_accounts}`,
                `${b.utilization_pct}%`,
                { text: `${b.adverse_count}`, tone: b.adverse_count > 0 ? "danger" : "success" },
                `${b.hard_inquiries}`,
                `${b.confidence}%`,
              ])}
            />
          </Section>
        </>
      )}

      {tab === "accounts" && (
        <Section heading="Tradelines & Balances">
          <Input
            label="Filter creditor or status"
            value={query}
            onChange={(val: string) => setQuery(val)}
            placeholder="Search bank, card, status..."
          />
          <Select<string>
            label="Account Type"
            value={kindFilter}
            onChange={(val: string) => setKindFilter(val)}
            options={[
              { value: "all", label: "All Types" },
              { value: "revolving", label: "Revolving" },
              { value: "installment", label: "Installment" },
              { value: "mortgage", label: "Mortgage" },
            ]}
          />
          {filteredAccounts.length > 0 && (
            <Table
              columns={["Bureau", "Creditor", "Acct", "Type", "Status", "Balance", "Limit", "Util"]}
              align={["start", "start", "start", "start", "start", "end", "end", "end"]}
              rows={filteredAccounts.map((a) => [
                a.bureau_label,
                a.creditor,
                a.masked,
                a.kind,
                { text: a.status, tone: a.is_adverse ? "danger" : "success" },
                a.balance,
                a.limit,
                a.util,
              ])}
            />
          )}
        </Section>
      )}

      {tab === "inquiries" && filteredInquiries.length > 0 && (
        <Section heading="Credit Inquiries" caption="Hard inquiries affect credit decisions; promotional/account review are soft">
          <Input
            label="Filter inquiry"
            value={query}
            onChange={(val: string) => setQuery(val)}
            placeholder="Search creditor..."
          />
          <Table
            columns={["Bureau", "Creditor", "Date", "Type", "Permissible Purpose"]}
            rows={filteredInquiries.map((q) => [
              q.bureau_label,
              q.creditor,
              q.date,
              { text: q.kind, tone: q.kind === "hard" ? "warning" : "success" },
              q.purpose || "—",
            ])}
          />
        </Section>
      )}

      {tab === "derogatory" && (
        <>
          {filteredCollections.length > 0 && (
            <Section heading="Collections">
              <Table
                columns={["Bureau", "Agency", "Acct", "Original Creditor", "Balance", "Status", "DOFD"]}
                align={["start", "start", "start", "start", "end", "start", "start"]}
                rows={filteredCollections.map((c) => [
                  c.bureau_label,
                  c.creditor,
                  c.masked,
                  c.original_creditor,
                  c.balance,
                  { text: c.status, tone: "danger" },
                  c.dofd,
                ])}
              />
            </Section>
          )}
          {filteredPublic.length > 0 && (
            <Section heading="Public Records">
              <Table
                columns={["Bureau", "Type", "Filed", "Status"]}
                rows={filteredPublic.map((p) => [
                  p.bureau_label,
                  p.kind,
                  p.filed_date,
                  { text: p.status, tone: "danger" },
                ])}
              />
            </Section>
          )}
          {filteredCollections.length === 0 && filteredPublic.length === 0 && (
            <Callout tone="success" lead="Clean derogatory check">
              Zero collections or public records appear in the selected bureau scope for ${DATA.week_label}.
            </Callout>
          )}
        </>
      )}

      {tab === "personal" && filteredPersonal.length > 0 && (
        <Section heading="Personal Information (PII-Minimized)">
          <Table
            columns={["Bureau", "Names", "SSN (Masked)", "Birth Year", "Addresses", "Employers"]}
            rows={filteredPersonal.map((p) => [
              p.bureau_label,
              p.names,
              p.ssn_last4,
              p.dob_year,
              p.addresses,
              p.employers,
            ])}
          />
        </Section>
      )}
    </Page>
  );
}
