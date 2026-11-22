import {
  Callout,
  Grid,
  Legend,
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
  week_label: "2026-W47",
  is_example_data: true,
  page_state: "ready" as PageState,
  scores: [
    {
      bureau: "equifax" as BureauKey,
      label: "Equifax",
      source: "myFICO Free",
      value: 758,
      band: "Very good",
      delta: 8,
      delta_period: "since last capture",
      as_of: "Nov 5, 2026",
    },
    {
      bureau: "experian" as BureauKey,
      label: "Experian",
      source: "Experian free",
      value: 764,
      band: "Very good",
      delta: 0,
      delta_period: "from last week",
      as_of: "Nov 21, 2026",
    },
    {
      bureau: "transunion" as BureauKey,
      label: "TransUnion",
      source: "CreditWise",
      value: 751,
      band: "Very good",
      delta: -4,
      delta_period: "from last week",
      as_of: "Nov 21, 2026",
    },
  ],
  history: [
    { week: "2026-W36", label: "Aug 31", equifax: 742, experian: 741, transunion: 739 },
    { week: "2026-W37", label: "Sep 7", equifax: 742, experian: 743, transunion: 740 },
    { week: "2026-W38", label: "Sep 14", equifax: 742, experian: 744, transunion: 742 },
    { week: "2026-W39", label: "Sep 21", equifax: 742, experian: 746, transunion: 744 },
    { week: "2026-W40", label: "Sep 28", equifax: 742, experian: 748, transunion: 746 },
    { week: "2026-W41", label: "Oct 5", equifax: 750, experian: 749, transunion: 747 },
    { week: "2026-W42", label: "Oct 12", equifax: 750, experian: 751, transunion: 749 },
    { week: "2026-W43", label: "Oct 19", equifax: 750, experian: 753, transunion: 751 },
    { week: "2026-W44", label: "Oct 26", equifax: 750, experian: 755, transunion: 753 },
    { week: "2026-W45", label: "Nov 2", equifax: 758, experian: 756, transunion: 754 },
    { week: "2026-W46", label: "Nov 9", equifax: 758, experian: 764, transunion: 755 },
    { week: "2026-W47", label: "Nov 21", equifax: 758, experian: 764, transunion: 751 },
  ],
  chart_annotations: [
    { week: "2026-W46", label: "Paid down", line: 1 },
    { week: "2026-W47", label: "New inquiry", line: 2 },
  ],
  factors: [
    {
      bureau: "equifax" as BureauKey,
      label: "Equifax",
      items: [
        { label: "Payment history", value: "On time, across the file" },
        { label: "Amounts owed", value: "Utilization is now in the 1\u20139% band" },
        { label: "New credit", value: "No new inquiries on this bureau" },
        { label: "Credit mix", value: "Cards plus an auto loan" },
      ],
    },
    {
      bureau: "experian" as BureauKey,
      label: "Experian",
      items: [
        { label: "Payment history", value: "On time, across the file" },
        { label: "Amounts owed", value: "A $900 paydown and a higher Summit limit" },
        { label: "New credit", value: "One older inquiry still on file from April" },
        { label: "Credit mix", value: "Cards plus an auto loan" },
      ],
    },
    {
      bureau: "transunion" as BureauKey,
      label: "TransUnion",
      items: [
        { label: "Payment history", value: "On time, across the file" },
        { label: "Amounts owed", value: "Balances came down last week" },
        { label: "New credit", value: "A new inquiry from Harbor Premier Bank on Nov 18" },
        { label: "Credit mix", value: "Cards plus an auto loan" },
      ],
    },
  ],
  consumer_alerts: [
    {
      id: "score-transunion",
      title: "Your TransUnion FICO Score 8 dropped 4 points after a new inquiry from Harbor Premier Bank.",
      detail: "Was this you?",
      status: "Check",
      tone: "warning" as StatusTone,
    },
    {
      id: "paydown-summit",
      title: "You paid down Summit Bank by $900.",
      detail: "$1,850 to $950 (****1234).",
      status: "Paid down",
      tone: "success" as StatusTone,
    },
    {
      id: "score-equifax",
      title: "Your Equifax FICO Score 8 is up 8 points since the last monthly capture.",
      detail: "myFICO Free shows 758 as of Nov 5, up from 750.",
      status: "Score up",
      tone: "success" as StatusTone,
    },
    {
      id: "limit-summit",
      title: "Summit Bank raised your limit to $12,000.",
      detail: "$10,000 to $12,000.",
      status: "Limit up",
      tone: "success" as StatusTone,
    },
    {
      id: "paydown-cascadia",
      title: "You paid down Cascadia Auto Finance by $350.",
      detail: "$11,400 to $11,050 (****9012).",
      status: "Paid down",
      tone: "success" as StatusTone,
    },
    {
      id: "paydown-northstar",
      title: "You paid down Northstar Credit Union by $250.",
      detail: "$650 to $400 (****5678).",
      status: "Paid down",
      tone: "success" as StatusTone,
    },
  ],
  next_moves: [
    {
      title: "Pay $400 on Northstar Credit Union by Dec 8",
      detail: "That brings this card to $0 so only one card reports a small balance.",
      status: "Pay by date",
      tone: "accent" as StatusTone,
    },
    {
      title: "Leave about $240 on Summit Bank by Dec 9",
      detail: "Keep this as the one card reporting in the 1\u20139% band.",
      status: "Keep a balance",
      tone: "success" as StatusTone,
    },
  ],
  projection:
    "Paying Northstar down to $0 so only Summit reports a small balance is the kind of move that typically helps FICO scores.",
  utilization_meter: {
    pct: 7.9,
    band_id: "azeo",
    band_label: "1-9%",
    bands: [
      { id: "zero", label: "0" },
      { id: "azeo", label: "1\u20139" },
      { id: "benchmark", label: "10\u201320" },
      { id: "ceiling", label: "21\u201329" },
      { id: "blocker", label: "30+" },
    ],
  },
  bureaus: [
    {
      bureau: "equifax" as BureauKey,
      label: "Equifax",
      fico8: 758,
      utilization_pct: 7.9,
      on_time_pct: 100.0,
      hard_inquiries: 0,
      adverse_count: 0,
      report_date_display: "Nov 21, 2026",
    },
    {
      bureau: "experian" as BureauKey,
      label: "Experian",
      fico8: 764,
      utilization_pct: 7.9,
      on_time_pct: 100.0,
      hard_inquiries: 1,
      adverse_count: 3,
      report_date_display: "Nov 21, 2026",
    },
    {
      bureau: "transunion" as BureauKey,
      label: "TransUnion",
      fico8: 751,
      utilization_pct: 7.9,
      on_time_pct: 100.0,
      hard_inquiries: 2,
      adverse_count: 0,
      report_date_display: "Nov 21, 2026",
    },
  ],
  vantage: [
    {
      label: "Equifax",
      source: "myEquifax / Core Credit",
      value: 772,
      as_of: "Nov 21, 2026",
    },
    {
      label: "TransUnion",
      source: "Credit Essentials",
      value: 768,
      as_of: "Nov 21, 2026",
    },
  ],
  accounts: [
    { bureau: "equifax" as BureauKey, creditor_display: "Summit Bank", masked: "****1234", balance: "$950", limit: "$12,000", util: "8%" },
    { bureau: "equifax" as BureauKey, creditor_display: "Northstar Credit Union", masked: "****5678", balance: "$400", limit: "$5,000", util: "8%" },
    { bureau: "experian" as BureauKey, creditor_display: "Summit Bank", masked: "****1234", balance: "$950", limit: "$12,000", util: "8%" },
    { bureau: "experian" as BureauKey, creditor_display: "Northstar Credit Union", masked: "****5678", balance: "$400", limit: "$5,000", util: "8%" },
    { bureau: "experian" as BureauKey, creditor_display: "Cascadia Auto Finance", masked: "****9012", balance: "$11,050", limit: "n/a", util: "n/a" },
    { bureau: "transunion" as BureauKey, creditor_display: "Summit Bank", masked: "****1234", balance: "$950", limit: "$12,000", util: "8%" },
    { bureau: "transunion" as BureauKey, creditor_display: "Northstar Credit Union", masked: "****5678", balance: "$400", limit: "$5,000", util: "8%" },
    { bureau: "transunion" as BureauKey, creditor_display: "Cascadia Auto Finance", masked: "****9012", balance: "$11,050", limit: "n/a", util: "n/a" },
  ],
};


function bandTone(band: string): StatusTone {
  if (band === "Exceptional" || band === "Very good") return "success";
  if (band === "Good") return "accent";
  if (band === "Fair") return "warning";
  return "danger";
}

function changeText(delta: number, period: string): string {
  if (delta === 0) return `No change ${period}`;
  if (delta > 0) return `Up ${delta} ${period}`;
  return `Down ${Math.abs(delta)} ${period}`;
}

function sparseLabel(label: string, index: number, count: number): string {
  if (count <= 5) return label;
  const last = count - 1;
  const keep = new Set(
    [0, last, Math.round(last / 3), Math.round((2 * last) / 3)].map((n) => n),
  );
  return keep.has(index) ? label : "";
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

function ScoreFigure({ value }: { value: number }) {
  const theme = useGrokTheme();
  return (
    <div style={{ padding: "4px 0 8px" }}>
      <div
        style={{
          ...theme.font.heading1,
          fontSize: 64,
          lineHeight: "72px",
          letterSpacing: "-0.04em",
          fontVariantNumeric: "tabular-nums",
          color: theme.text.primary,
        }}
      >
        {value}
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

  const featuredAlerts = DATA.consumer_alerts.slice(0, 3);
  const extraAlerts = DATA.consumer_alerts.slice(3);
  const visibleAlerts = showAllChanges ? DATA.consumer_alerts : featuredAlerts;
  const leadMove = DATA.next_moves[0];
  const moreMoves = DATA.next_moves.slice(1);
  const pageState = DATA.page_state;

  const series = useMemo(() => {
    const n = range === "4w" ? 4 : range === "12w" ? 12 : DATA.history.length;
    return DATA.history.slice(-Math.max(n, 1));
  }, [range]);

  const annotations = useMemo(() => {
    return DATA.chart_annotations.flatMap((a) => {
      const at = series.findIndex((p) => p.week === a.week);
      if (at < 0) return [];
      return [{ at, label: a.label, line: a.line }];
    });
  }, [series]);

  const reportAccounts = DATA.accounts.filter((a) => a.bureau === reportBureau);
  const bureauOptions = DATA.bureaus.map((b) => ({ value: b.bureau, label: b.label }));
  const showChart = DATA.history.length >= 2 && pageState !== "first_week";
  const showRange = DATA.history.length >= 4;

  return (
    <Page
      title={"Credit Weekly: Dream State (Jordan Example, all 3 FICO 8 scores)"}
      summary={
        "A simple look at how Jordan Example\u2019s weekly dashboard can feel once Equifax, Experian, and TransUnion FICO Score 8s are connected. This is example data, not a live pull."
      }
      width="wide"
    >
      {pageState === "updating" ? (
        <Callout tone="info" lead="Updating this week">
          Last week stays on the page until the new pull is ready.
        </Callout>
      ) : null}

      <Section heading="Your FICO Score 8" caption="Equifax from myFICO Free, Experian from Experian free, and TransUnion from CreditWise.">
        <Grid columns={3} joined>
          {DATA.scores.map((s) => (
            <Section heading={s.label} caption={`FICO Score 8 · ${s.source}`} key={s.bureau}>
              <ScoreFigure value={s.value} />
              <Status tone={bandTone(s.band)}>{s.band}</Status>
              <Properties
                items={[
                  { label: "Change", value: changeText(s.delta, s.delta_period) },
                  { label: "As of", value: s.as_of },
                ]}
              />
            </Section>
          ))}
        </Grid>
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
          <>
            <Legend names={["Equifax FICO Score 8", "Experian FICO Score 8", "TransUnion FICO Score 8"]} />
            <HistoryChart
              series={[
                { label: "Equifax FICO Score 8", values: series.map((p) => p.equifax) },
                { label: "Experian FICO Score 8", values: series.map((p) => p.experian) },
                { label: "TransUnion FICO Score 8", values: series.map((p) => p.transunion) },
              ]}
              xLabels={series.map((p, i) => sparseLabel(p.label, i, series.length))}
              floor={720}
              ceiling={800}
              annotations={annotations}
            />
          </>
        ) : (
          <Text>Your history will build here after the next weekly pull.</Text>
        )}
      </Section>

      <Section
        heading="What to do this week"
        caption={`Overall utilization is ${DATA.utilization_meter.pct}% in the ${DATA.utilization_meter.band_label} band`}
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
        <Text>{DATA.projection}</Text>
        <UtilizationMeter pct={DATA.utilization_meter.pct} bandId={DATA.utilization_meter.band_id} />
      </Section>

      <Section
        heading="This week"
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

      <Section heading="What's moving your score" caption="Plain-English factors on each bureau, not a FICO model breakdown.">
        <Grid columns={3} joined>
          {DATA.factors.map((f) => (
            <Section heading={f.label} key={f.bureau}>
              <Properties items={f.items} />
            </Section>
          ))}
        </Grid>
      </Section>

      <Section heading="Your three bureaus">
        <Grid columns={3} joined>
          {DATA.bureaus.map((b) => (
            <Section heading={b.label} key={b.bureau}>
              <Properties
                items={[
                  { label: "FICO Score 8", value: String(b.fico8) },
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
        heading="VantageScore 3.0"
        caption="A different model than FICO Score 8, from myEquifax / Core Credit and TransUnion Credit Essentials."
        collapsible
        defaultOpen={false}
      >
        <Rows
          rows={DATA.vantage.map((v) => ({
            title: v.label,
            detail: `${v.source} · ${v.as_of}`,
            meta: String(v.value),
          }))}
        />
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

      <Text>
        This is example data for Jordan Example. The scores shown are FICO Score 8 from free sources once those accounts are connected.
      </Text>
    </Page>
  );
}
