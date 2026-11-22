import {
  Callout,
  Grid,
  Page,
  Properties,
  Rows,
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
type PageState = "ready" | "updating" | "first_week";
type RowTone = "success" | "warning" | "danger";

const DATA = {
  "week_label": "2026-W47",
  "is_example_data": true,
  "page_state": "ready",
  "as_of_display": "Nov 16, 2026",
  "health_summary": {
    "credit_health_index": 89,
    "credit_health_band": "Good",
    "credit_health_delta": 0,
    "utilization_pct": 7.9
  },
  "history": [
    {
      "week": "2026-W36",
      "credit_health_index": 76
    },
    {
      "week": "2026-W37",
      "credit_health_index": 76
    },
    {
      "week": "2026-W38",
      "credit_health_index": 77
    },
    {
      "week": "2026-W39",
      "credit_health_index": 78
    },
    {
      "week": "2026-W40",
      "credit_health_index": 80
    },
    {
      "week": "2026-W41",
      "credit_health_index": 81
    },
    {
      "week": "2026-W42",
      "credit_health_index": 82
    },
    {
      "week": "2026-W43",
      "credit_health_index": 82
    },
    {
      "week": "2026-W44",
      "credit_health_index": 83
    },
    {
      "week": "2026-W45",
      "credit_health_index": 83
    },
    {
      "week": "2026-W46",
      "credit_health_index": 89
    },
    {
      "week": "2026-W47",
      "credit_health_index": 89
    }
  ],
  "chart_annotations": [
    {
      "week": "2026-W46",
      "label": "Paid down"
    },
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
      "utilization_pct": 7.9,
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
      "limit": "n/a",
      "util": "n/a"
    },
    {
      "bureau": "transunion",
      "creditor_display": "Summit Bank",
      "masked": "****1234",
      "balance": "$950",
      "limit": "$12,000",
      "util": "8%"
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
      "limit": "n/a",
      "util": "n/a"
    }
  ]
} as {
  week_label: string;
  is_example_data: boolean;
  page_state: PageState;
  as_of_display: string;
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
  chart_annotations: Array<{ week: string; label: string; line?: number; value?: number }>;
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

function sparseLabel(label: string, index: number, count: number): string {
  if (count <= 5) return label;
  const last = count - 1;
  const keep = new Set([0, last, Math.round(last / 3), Math.round((2 * last) / 3)]);
  return keep.has(index) ? label : "";
}

function chiScale(values: number[]): { floor: number; ceiling: number } {
  if (values.length === 0) return { floor: 0, ceiling: 100 };
  const raw = Math.min(...values);
  const floor = Math.max(0, Math.min(70, Math.floor((raw - 5) / 10) * 10));
  return { floor, ceiling: 100 };
}

function bandTone(band: string): StatusTone {
  if (band === "Excellent" || band === "Good") return "success";
  if (band === "Fair") return "accent";
  if (band === "Needs work") return "warning";
  return "danger";
}

function rowTone(tone: StatusTone): RowTone | undefined {
  if (tone === "success" || tone === "warning" || tone === "danger") return tone;
  return undefined;
}

function joinSentences(title: string, detail: string): string {
  const head = title.trim();
  const lead = /[.!?]$/.test(head) ? head : `${head}.`;
  return `${lead} ${detail.trim()}`;
}

type ChartSeries = { label: string; values: number[] };
type ChartNote = { at: number; label: string; line?: number; value?: number };

function HistoryChart({
  series,
  xLabels,
  floor,
  ceiling,
  annotations,
}: {
  series: ChartSeries[];
  xLabels: string[];
  floor: number;
  ceiling: number;
  annotations: ChartNote[];
}) {
  const theme = useGrokTheme();
  const W = 1280;
  const H = 360;
  const pad = { l: 64, r: 40, t: 48, b: 48 };
  const innerW = W - pad.l - pad.r;
  const innerH = H - pad.t - pad.b;
  const last = Math.max(xLabels.length - 1, 1);
  const xAt = (i: number) => pad.l + (i / last) * innerW;
  const span = Math.max(ceiling - floor, 1);
  const yAt = (v: number) => pad.t + ((ceiling - v) / span) * innerH;
  const mid = Math.round((floor + ceiling) / 2);
  const ticks = Array.from(new Set([floor, mid, ceiling]));
  const labelPx = 14;
  const ink = theme.text.secondary;
  const colors = series.map((_, i) => theme.dataviz.categorical[i] ?? theme.dataviz.other);
  const bySlot: Record<number, ChartNote[]> = {};
  annotations.forEach((a) => {
    bySlot[a.at] = bySlot[a.at] ? [...bySlot[a.at], a] : [a];
  });
  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      role="img"
      aria-label={series.map((s) => s.label).join(", ")}
    >
      {ticks.map((tick) => (
        <g key={`t-${tick}`}>
          <line
            x1={pad.l}
            x2={W - pad.r}
            y1={yAt(tick)}
            y2={yAt(tick)}
            stroke={theme.border.subtle}
            strokeWidth={1}
          />
          <text
            x={pad.l - 12}
            y={yAt(tick) + 5}
            textAnchor="end"
            fill={ink}
            fontFamily={theme.font.family}
            fontSize={labelPx}
          >
            {String(tick)}
          </text>
        </g>
      ))}
      {xLabels.map((lab, i) =>
        lab ? (
          <text
            key={`x-${i}`}
            x={xAt(i)}
            y={H - 16}
            textAnchor={i === 0 ? "start" : i === last ? "end" : "middle"}
            fill={ink}
            fontFamily={theme.font.family}
            fontSize={labelPx}
          >
            {lab}
          </text>
        ) : null,
      )}
      {series.map((s, si) => {
        const pts = s.values.map((v, i) => `${xAt(i)},${yAt(v)}`);
        const d = pts.map((pt, i) => `${i === 0 ? "M" : "L"}${pt}`).join(" ");
        const area = `${d} L${xAt(s.values.length - 1)},${yAt(floor)} L${xAt(0)},${yAt(floor)} Z`;
        return (
          <g key={s.label}>
            {si === 0 ? (
              <path d={area} fill={colors[si]} opacity={0.16} />
            ) : null}
            <path d={d} fill="none" stroke={colors[si]} strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round" />
          </g>
        );
      })}
      {Object.entries(bySlot).flatMap(([slot, notes]) =>
        notes.map((a, ni) => {
          const at = Number(slot);
          const vals = series[a.line ?? 0]?.values ?? series[0].values;
          const dataY = vals[at];
          const lift = ((notes.length - 1 - ni) * (span * 0.08));
          const pin = Math.min(ceiling, (a.value ?? dataY) + span * 0.14 + lift);
          const x = xAt(at);
          const y = yAt(pin);
          const ly = yAt(dataY);
          const nearRight = at >= xLabels.length - 2;
          const tx = nearRight ? x - 8 : x;
          const ty = y - 4;
          return (
            <g key={`${a.label}-${at}`}>
              <line x1={x} y1={ly - 6} x2={tx} y2={ty + 4} stroke={ink} strokeWidth={1} />
              <text
                x={tx}
                y={ty}
                textAnchor={nearRight ? "end" : "middle"}
                fill={ink}
                fontFamily={theme.font.family}
                fontSize={labelPx}
              >
                {a.label}
              </text>
            </g>
          );
        }),
      )}
    </svg>
  );
}

function IndexHero({
  value,
  delta,
  asOf,
}: {
  value: number;
  delta: number | null;
  asOf: string;
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
        gap: 28,
        padding: "8px 0 12px",
      }}
    >
      <div
        style={{
          ...theme.font.heading1,
          fontSize: 80,
          lineHeight: "88px",
          letterSpacing: "-0.04em",
          fontVariantNumeric: "tabular-nums",
          color: theme.text.primary,
        }}
      >
        {value}
      </div>
      <div style={{ minWidth: 160, paddingBottom: 8 }}>
        <div style={{ ...theme.font.subtext, color: theme.text.secondary }}>
          {deltaText}
        </div>
        <div style={{ ...theme.font.caption, color: theme.text.secondary, marginTop: 6 }}>
          Not a FICO score
        </div>
        {asOf ? (
          <div style={{ ...theme.font.caption, color: theme.text.secondary, marginTop: 4 }}>
            {`As of ${asOf}`}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function UtilizationMeter({ pct, bandId }: { pct: number; bandId: string }) {
  const theme = useGrokTheme();
  const bands = DATA.utilization_meter.bands;
  const W = 640;
  const H = 64;
  const padX = 0;
  const gap = 8;
  const trackY = 14;
  const trackH = 12;
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
              rx={6}
              fill={on ? theme.dataviz.categorical[0] : theme.fill.secondary}
            />
            <text
              x={x + segW / 2}
              y={trackY + trackH + 22}
              textAnchor="middle"
              fill={on ? theme.text.primary : theme.text.secondary}
              fontFamily={theme.font.family}
              fontSize={13}
            >
              {b.label}
            </text>
          </g>
        );
      })}
      <polygon
        points={`${markerX},${trackY - 6} ${markerX - 6},${trackY - 14} ${markerX + 6},${trackY - 14}`}
        fill={theme.dataviz.categorical[0]}
      />
    </svg>
  );
}

export default function App() {
  const [range, setRange] = useState<RangeKey>("12w");
  const [showAllChanges, setShowAllChanges] = useState(false);
  const defaultBureau = (DATA.bureaus[1]?.bureau ?? DATA.bureaus[0]?.bureau ?? "experian") as BureauKey;
  const [reportBureau, setReportBureau] = useState<BureauKey>(defaultBureau);

  const hs = DATA.health_summary;
  const pageState = DATA.page_state;
  const featuredAlerts = DATA.consumer_alerts.slice(0, 3);
  const extraAlerts = DATA.consumer_alerts.slice(3);
  const visibleAlerts = showAllChanges ? DATA.consumer_alerts : featuredAlerts;
  const leadMove = DATA.next_moves[0];
  const moreMoves = DATA.next_moves.slice(1);

  const series = useMemo(() => {
    const n = range === "4w" ? 4 : range === "12w" ? 12 : DATA.history.length;
    const slice = DATA.history.slice(-Math.max(n, 1));
    return slice.map((h, i) => ({
      label: sparseLabel(weekLabel(h.week), i, slice.length),
      value: h.credit_health_index,
      week: h.week,
    }));
  }, [range]);

  const scale = useMemo(() => chiScale(series.map((p) => p.value)), [series]);

  const annotations = useMemo(() => {
    return DATA.chart_annotations.flatMap((a) => {
      const at = series.findIndex((p) => p.week === a.week);
      if (at < 0) return [];
      return [{ at, label: a.label, line: 0 as const }];
    });
  }, [series]);

  const reportAccounts = DATA.accounts.filter((a) => a.bureau === reportBureau);
  const bureauOptions = DATA.bureaus.map((b) => ({ value: b.bureau, label: b.label }));
  const showChart = DATA.history.length >= 2 && pageState !== "first_week";
  const showRange = DATA.history.length >= 4;

  return (
    <Page
      title={"Credit Weekly: Example Dashboard (Jordan Example)"}
      summary={"A simple weekly look at Jordan Example\u2019s reports. The Credit-Health Index is not a FICO score."}
      width="wide"
    >
      {pageState === "updating" ? (
        <Callout tone="info" lead="Updating this week">
          Last week stays on the page until the new pull is ready.
        </Callout>
      ) : null}

      <Section heading="Your Credit-Health Index">
        <IndexHero
          value={hs.credit_health_index}
          delta={hs.credit_health_delta}
          asOf={DATA.as_of_display}
        />
        <Status tone={bandTone(hs.credit_health_band)}>{hs.credit_health_band}</Status>
        {showRange ? (
          <Segmented
            value={range}
            onChange={setRange}
            options={[
              { value: "4w", label: "4 weeks" },
              { value: "12w", label: "12 weeks" },
              { value: "all", label: "All" },
            ]}
          />
        ) : null}
        {showChart ? (
          <HistoryChart
            series={[{ label: "Credit-Health Index", values: series.map((p) => p.value) }]}
            xLabels={series.map((p) => p.label)}
            floor={scale.floor}
            ceiling={scale.ceiling}
            annotations={annotations}
          />
        ) : (
          <Text>Your history will build here after the next weekly pull.</Text>
        )}
      </Section>

      <Section
        heading="What to do this week"
        caption={`Overall utilization is ${hs.utilization_pct}% in the ${DATA.utilization_meter.band_label} band`}
      >
        {DATA.next_moves.length === 0 ? (
          <Text>You are in good shape. Keep paying on time and stay in this band.</Text>
        ) : (
          <>
            <Callout lead={leadMove.status}>{joinSentences(leadMove.title, leadMove.detail)}</Callout>
            {moreMoves.length > 0 ? (
              <Rows
                rows={moreMoves.map((m) => ({
                  title: m.title,
                  detail: m.detail,
                  status: rowTone(m.tone) ? { label: m.status, tone: rowTone(m.tone) } : { label: m.status },
                }))}
              />
            ) : null}
          </>
        )}
        <UtilizationMeter pct={DATA.utilization_meter.pct} bandId={DATA.utilization_meter.band_id} />
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
        ) : (
          <Rows
            rows={visibleAlerts.map((a) => ({
              title: a.title,
              detail: a.detail,
              status: rowTone(a.tone) ? { label: a.status, tone: rowTone(a.tone) } : { label: a.status },
            }))}
          />
        )}
      </Section>

      <Section heading="Your three bureaus">
        <Grid columns={3} joined>
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
        collapsible
        defaultOpen={false}
      >
        <Segmented value={reportBureau} onChange={setReportBureau} options={bureauOptions} />
        <Table
          columns={["Account", "Balance", "Limit", "Use"]}
          align={["start", "end", "end", "end"]}
          rows={reportAccounts.map((a) => [
            `${a.creditor_display} ${a.masked}`,
            a.balance,
            a.limit,
            a.util,
          ])}
        />
      </Section>

      {DATA.is_example_data ? (
        <Text>This page uses example data for Jordan Example. It is not a live credit pull.</Text>
      ) : null}
    </Page>
  );
}
