import {
  Grid,
  LineChart,
  Page,
  Properties,
  Section,
  Segmented,
  Status,
  Table,
  Text,
  Toggle,
  useGrokTheme,
  useMemo,
  useState,
} from "grok/canvas";

type RangeKey = "4w" | "12w" | "all";
type BureauKey = "equifax" | "experian" | "transunion";
type StatusTone = "success" | "warning" | "danger" | "accent" | "neutral";

const DATA = {
  "week_label": "2026-W47",
  "is_example_data": true,
  "health_summary": {
    "credit_health_index": 89,
    "credit_health_band": "Good",
    "credit_health_delta": 5,
    "utilization_pct": 7.9
  },
  "history": [
    {
      "week": "2026-W46",
      "credit_health_index": 84
    },
    {
      "week": "2026-W47",
      "credit_health_index": 89
    }
  ],
  "chart_annotations": [
    {
      "week": "2026-W47",
      "label": "New inquiry"
    }
  ],
  "utilization_meter": {
    "pct": 7.9,
    "band_id": "azeo",
    "band_label": "1-9%",
    "bands": [
      {
        "id": "zero",
        "label": "0"
      },
      {
        "id": "azeo",
        "label": "1–9"
      },
      {
        "id": "benchmark",
        "label": "10–20"
      },
      {
        "id": "ceiling",
        "label": "21–29"
      },
      {
        "id": "blocker",
        "label": "30+"
      }
    ]
  },
  "consumer_alerts": [
    {
      "id": "new_hard_inquiry-HARBOR PREMIER BANK",
      "title": "New inquiry from Harbor Premier Bank on TransUnion.",
      "detail": "Was this you?",
      "status": "Check",
      "tone": "warning"
    },
    {
      "id": "limit_change-SUMMIT BANK NA",
      "title": "Summit Bank raised your limit to $12,000.",
      "detail": "$10,000 to $12,000.",
      "status": "Limit up",
      "tone": "success"
    },
    {
      "id": "balance_change-SUMMIT BANK NA",
      "title": "You paid down Summit Bank by $900.",
      "detail": "$1,850 to $950 (****1234).",
      "status": "Paid down",
      "tone": "success"
    },
    {
      "id": "balance_change-CASCADIA AUTO FINANCE",
      "title": "You paid down Cascadia Auto Finance by $350.",
      "detail": "$11,400 to $11,050 (****9012).",
      "status": "Paid down",
      "tone": "success"
    },
    {
      "id": "balance_change-NORTHSTAR CREDIT UNION",
      "title": "You paid down Northstar Credit Union by $250.",
      "detail": "$650 to $400 (****5678).",
      "status": "Paid down",
      "tone": "success"
    }
  ],
  "next_moves": [
    {
      "title": "Pay $400 on Northstar Credit Union by Dec 8",
      "detail": "That brings this card to $0 so only one card reports a small balance.",
      "status": "Pay by date",
      "tone": "accent"
    },
    {
      "title": "Leave about $240 on Summit Bank by Dec 9",
      "detail": "Keep this as the one card reporting in the 1–9% band.",
      "status": "Keep a balance",
      "tone": "success"
    }
  ],
  "bureaus": [
    {
      "bureau": "equifax",
      "label": "Equifax",
      "utilization_pct": 7.9,
      "on_time_pct": 100.0,
      "hard_inquiries": 0,
      "adverse_count": 0,
      "report_date_display": "Nov 16, 2026"
    },
    {
      "bureau": "experian",
      "label": "Experian",
      "utilization_pct": 7.9,
      "on_time_pct": 100.0,
      "hard_inquiries": 1,
      "adverse_count": 3,
      "report_date_display": "Nov 16, 2026"
    },
    {
      "bureau": "transunion",
      "label": "TransUnion",
      "utilization_pct": 0.0,
      "on_time_pct": 100.0,
      "hard_inquiries": 2,
      "adverse_count": 0,
      "report_date_display": "Nov 16, 2026"
    }
  ],
  "accounts": [
    {
      "bureau": "equifax",
      "creditor_display": "Summit Bank",
      "masked": "****1234",
      "balance": "$950",
      "limit": "$12,000",
      "util": "8%"
    },
    {
      "bureau": "equifax",
      "creditor_display": "Northstar Credit Union",
      "masked": "****5678",
      "balance": "$400",
      "limit": "$5,000",
      "util": "8%"
    },
    {
      "bureau": "experian",
      "creditor_display": "Summit Bank",
      "masked": "****1234",
      "balance": "$950",
      "limit": "$12,000",
      "util": "8%"
    },
    {
      "bureau": "experian",
      "creditor_display": "Northstar Credit Union",
      "masked": "****5678",
      "balance": "$400",
      "limit": "$5,000",
      "util": "8%"
    },
    {
      "bureau": "experian",
      "creditor_display": "Cascadia Auto Finance",
      "masked": "****9012",
      "balance": "$11,050",
      "limit": "—",
      "util": "—"
    },
    {
      "bureau": "transunion",
      "creditor_display": "Summit Bank",
      "masked": "****1234",
      "balance": "$950",
      "limit": "$10,000",
      "util": "10%"
    },
    {
      "bureau": "transunion",
      "creditor_display": "Northstar Credit Union",
      "masked": "****5678",
      "balance": "$400",
      "limit": "$5,000",
      "util": "8%"
    },
    {
      "bureau": "transunion",
      "creditor_display": "Cascadia Auto Finance",
      "masked": "****9012",
      "balance": "$11,050",
      "limit": "—",
      "util": "—"
    }
  ]
} as {
  week_label: string;
  is_example_data: boolean;
  health_summary: {
    credit_health_index: number;
    credit_health_band: string;
    credit_health_delta: number | null;
    utilization_pct: number;
  };
  history: Array<{
    week: string;
    credit_health_index: number;
  }>;
  chart_annotations: Array<{ week: string; label: string }>;
  utilization_meter: {
    pct: number;
    band_id: string;
    band_label: string;
    bands: Array<{ id: string; label: string }>;
  };
  consumer_alerts: Array<{
    id: string;
    title: string;
    detail: string;
    status: string;
    tone: StatusTone;
  }>;
  next_moves: Array<{
    title: string;
    detail: string;
    status: string;
    tone: StatusTone;
  }>;
  bureaus: Array<{
    bureau: BureauKey;
    label: string;
    utilization_pct: number;
    on_time_pct: number;
    hard_inquiries: number;
    adverse_count: number;
    report_date_display: string;
  }>;
  accounts: Array<{
    bureau: BureauKey;
    creditor_display: string;
    masked: string;
    balance: string;
    limit: string;
    util: string;
  }>;
};

function weekLabel(week: string): string {
  const m = week.match(/W(\d+)$/i);
  return m ? `W${m[1]}` : week;
}

function bandTone(band: string): StatusTone {
  if (band === "Excellent" || band === "Good") return "success";
  if (band === "Fair") return "accent";
  if (band === "Needs work") return "warning";
  return "danger";
}

function IndexHero({
  value,
  delta,
}: {
  value: number;
  delta: number | null;
}) {
  const theme = useGrokTheme();
  const deltaText =
    delta === null
      ? "First week on file"
      : delta === 0
        ? "No change from last week"
        : delta > 0
          ? `Up ${delta} from last week`
          : `Down ${Math.abs(delta)} from last week`;
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        alignItems: "baseline",
        gap: 20,
      }}
    >
      <div
        style={{
          ...theme.font.heading1,
          fontSize: 64,
          lineHeight: "72px",
          letterSpacing: "-0.03em",
          color: theme.text.primary,
        }}
      >
        {value}
      </div>
      <div>
        <div style={{ ...theme.font.subtext, color: theme.text.secondary }}>
          {deltaText}
        </div>
        <div style={{ ...theme.font.caption, color: theme.text.tertiary, marginTop: 4 }}>
          Not a FICO score
        </div>
      </div>
    </div>
  );
}

function UtilizationMeter({ pct, bandId }: { pct: number; bandId: string }) {
  const theme = useGrokTheme();
  const bands = DATA.utilization_meter.bands;
  const W = 640;
  const H = 56;
  const padX = 4;
  const gap = 6;
  const trackY = 8;
  const trackH = 14;
  const n = bands.length;
  const segW = (W - padX * 2 - gap * (n - 1)) / n;
  const active = Math.max(0, bands.findIndex((b) => b.id === bandId));
  const markerX = padX + active * (segW + gap) + segW / 2;
  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      role="img"
      aria-label={`Utilization ${pct}% in the ${DATA.utilization_meter.band_label} band`}
    >
      {bands.map((b, i) => {
        const x = padX + i * (segW + gap);
        const on = b.id === bandId;
        return (
          <g key={b.id}>
            <rect
              x={x}
              y={trackY}
              width={segW}
              height={trackH}
              rx={7}
              fill={on ? theme.dataviz.categorical[0] : theme.fill.secondary}
            />
            <text
              x={x + segW / 2}
              y={trackY + trackH + 16}
              textAnchor="middle"
              fill={theme.text.tertiary}
              fontFamily={theme.font.family}
              fontSize={12}
            >
              {b.label}
            </text>
          </g>
        );
      })}
      <polygon
        points={`${markerX},${trackY - 5} ${markerX - 6},${trackY - 13} ${markerX + 6},${trackY - 13}`}
        fill={theme.dataviz.categorical[0]}
      />
    </svg>
  );
}

export default function App() {
  const [range, setRange] = useState<RangeKey>("all");
  const [showAllChanges, setShowAllChanges] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const defaultBureau = (DATA.bureaus[1]?.bureau ?? DATA.bureaus[0]?.bureau ?? "experian") as BureauKey;
  const [reportBureau, setReportBureau] = useState<BureauKey>(defaultBureau);

  const hs = DATA.health_summary;
  const featuredAlerts = DATA.consumer_alerts.slice(0, 3);
  const extraAlerts = DATA.consumer_alerts.slice(3);
  const visibleAlerts = showAllChanges ? DATA.consumer_alerts : featuredAlerts;

  const series = useMemo(() => {
    const pts = DATA.history.map((h) => ({
      label: weekLabel(h.week),
      value: h.credit_health_index,
      week: h.week,
    }));
    const n = range === "4w" ? 4 : range === "12w" ? 12 : pts.length;
    return pts.slice(-Math.max(n, 1));
  }, [range]);

  const annotations = useMemo(() => {
    return DATA.chart_annotations.flatMap((a) => {
      const at = series.findIndex((p) => p.week === a.week);
      if (at < 0) return [];
      return [{ at, label: a.label, line: 0 as const }];
    });
  }, [series]);

  const reportAccounts = DATA.accounts.filter((a) => a.bureau === reportBureau);
  const bureauOptions = DATA.bureaus.map((b) => ({ value: b.bureau, label: b.label }));

  return (
    <Page
      title={"Credit Weekly: Example Dashboard (Jordan Example)"}
      summary={"A simple weekly look at Jordan Example\u2019s reports. The Credit-Health Index is not a FICO score."}
      width="wide"
    >
      <Section heading="Your Credit-Health Index">
        <IndexHero
          value={hs.credit_health_index}
          delta={hs.credit_health_delta}
        />
        <Status tone={bandTone(hs.credit_health_band)}>{hs.credit_health_band}</Status>
        <Segmented
          value={range}
          onChange={setRange}
          options={[
            { value: "4w", label: "4 weeks" },
            { value: "12w", label: "12 weeks" },
            { value: "all", label: "All" },
          ]}
        />
        <LineChart
          points={series.map((p) => ({ label: p.label, value: p.value }))}
          floor={0}
          ceiling={100}
          labels={["Credit-Health Index"]}
          annotations={annotations}
        />
      </Section>

      <Section
        heading="This week"
        caption={DATA.consumer_alerts.length === 0 ? "Nothing new to review." : undefined}
        actions={
          extraAlerts.length > 0 ? (
            <Toggle
              label="See all changes"
              value={showAllChanges}
              onChange={setShowAllChanges}
            />
          ) : undefined
        }
      >
        {visibleAlerts.length === 0 ? (
          <Text>Quiet week. No new inquiries, late marks, or surprises.</Text>
        ) : visibleAlerts.length === 1 ? (
          <Section heading={visibleAlerts[0].title}>
            <Status tone={visibleAlerts[0].tone}>{visibleAlerts[0].status}</Status>
            <Text>{visibleAlerts[0].detail}</Text>
          </Section>
        ) : (
          <Grid columns={visibleAlerts.length === 2 ? 2 : 3}>
            {visibleAlerts.map((a) => (
              <Section heading={a.title} key={a.id}>
                <Status tone={a.tone}>{a.status}</Status>
                <Text>{a.detail}</Text>
              </Section>
            ))}
          </Grid>
        )}
      </Section>

      <Section
        heading="Your next move"
        caption={`Overall utilization is ${hs.utilization_pct}% · ${DATA.utilization_meter.band_label}`}
      >
        {DATA.next_moves.length === 0 ? (
          <Text>You're in good shape. Keep paying on time and stay in this band.</Text>
        ) : DATA.next_moves.length === 1 ? (
          <Section heading={DATA.next_moves[0].title}>
            <Status tone={DATA.next_moves[0].tone}>{DATA.next_moves[0].status}</Status>
            <Text>{DATA.next_moves[0].detail}</Text>
          </Section>
        ) : (
          <Grid columns={DATA.next_moves.length === 2 ? 2 : 3}>
            {DATA.next_moves.map((m) => (
              <Section heading={m.title} key={m.title}>
                <Status tone={m.tone}>{m.status}</Status>
                <Text>{m.detail}</Text>
              </Section>
            ))}
          </Grid>
        )}
        <UtilizationMeter pct={DATA.utilization_meter.pct} bandId={DATA.utilization_meter.band_id} />
      </Section>

      <Section heading="Your three bureaus">
        <Grid columns={3}>
          {DATA.bureaus.map((b) => (
            <Section heading={b.label} key={b.bureau}>
              <Properties
                items={[
                  { label: "Utilization", value: `${b.utilization_pct}%` },
                  { label: "On-time", value: `${b.on_time_pct}%` },
                  { label: "Inquiries", value: String(b.hard_inquiries) },
                  {
                    label: "Negatives",
                    value:
                      b.adverse_count === 0 ? (
                        <Status tone="success">None</Status>
                      ) : (
                        <Status tone="warning">{String(b.adverse_count)}</Status>
                      ),
                  },
                  { label: "Updated", value: b.report_date_display },
                ]}
              />
            </Section>
          ))}
        </Grid>
      </Section>

      <Section
        heading="See full report"
        caption="A simple list of the accounts on file."
        actions={
          <Toggle label="Show accounts" value={showReport} onChange={setShowReport} />
        }
      >
        {showReport ? (
          <>
            <Segmented value={reportBureau} onChange={setReportBureau} options={bureauOptions} />
            <Table
              columns={["Account", "Balance", "Limit", "Use"]}
              rows={reportAccounts.map((a) => [
                `${a.creditor_display} ${a.masked}`,
                a.balance,
                a.limit,
                a.util,
              ])}
            />
          </>
        ) : (
          <Text>Turn this on when you want to look at every account on one bureau.</Text>
        )}
      </Section>
    </Page>
  );
}
