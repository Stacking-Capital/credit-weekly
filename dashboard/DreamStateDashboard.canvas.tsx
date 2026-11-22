import {
  Callout,
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
  week_label: "2026-W47",
  is_example_data: true,
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
      delta: 6,
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
    { week: "2026-W46", label: "Nov 9", equifax: 758, experian: 758, transunion: 755 },
    { week: "2026-W47", label: "Nov 16", equifax: 758, experian: 764, transunion: 751 },
  ],
  chart_annotations: [
    { week: "2026-W47", label: "Paid down", line: 1 },
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
        { label: "Amounts owed", value: "Balances came down this week" },
        { label: "New credit", value: "A new inquiry from Harbor Premier Bank on Nov 14" },
        { label: "Credit mix", value: "Cards plus an auto loan" },
      ],
    },
  ],
  consumer_alerts: [
    {
      id: "score-experian",
      title: "Your Experian FICO Score 8 rose 6 points this week.",
      detail: "It moved from 758 to 764, still in the Very good band.",
      status: "Score up",
      tone: "success" as StatusTone,
    },
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
      report_date_display: "Nov 16, 2026",
    },
    {
      bureau: "experian" as BureauKey,
      label: "Experian",
      fico8: 764,
      utilization_pct: 7.9,
      on_time_pct: 100.0,
      hard_inquiries: 1,
      adverse_count: 3,
      report_date_display: "Nov 16, 2026",
    },
    {
      bureau: "transunion" as BureauKey,
      label: "TransUnion",
      fico8: 751,
      utilization_pct: 0.0,
      on_time_pct: 100.0,
      hard_inquiries: 2,
      adverse_count: 0,
      report_date_display: "Nov 16, 2026",
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
    { bureau: "experian" as BureauKey, creditor_display: "Cascadia Auto Finance", masked: "****9012", balance: "$11,050", limit: "\u2014", util: "\u2014" },
    { bureau: "transunion" as BureauKey, creditor_display: "Summit Bank", masked: "****1234", balance: "$950", limit: "$10,000", util: "10%" },
    { bureau: "transunion" as BureauKey, creditor_display: "Northstar Credit Union", masked: "****5678", balance: "$400", limit: "$5,000", util: "8%" },
    { bureau: "transunion" as BureauKey, creditor_display: "Cascadia Auto Finance", masked: "****9012", balance: "$11,050", limit: "\u2014", util: "\u2014" },
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

function ScoreFigure({ value }: { value: number }) {
  const theme = useGrokTheme();
  return (
    <div>
      <div
        style={{
          ...theme.font.heading1,
          fontSize: 56,
          lineHeight: "64px",
          letterSpacing: "-0.03em",
          color: theme.text.primary,
        }}
      >
        {value}
      </div>
      <div style={{ ...theme.font.caption, color: theme.text.tertiary, marginTop: 2 }}>
        FICO Score 8
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
  const [range, setRange] = useState<RangeKey>("12w");
  const [showAllChanges, setShowAllChanges] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const defaultBureau = (DATA.bureaus[1]?.bureau ?? DATA.bureaus[0]?.bureau ?? "experian") as BureauKey;
  const [reportBureau, setReportBureau] = useState<BureauKey>(defaultBureau);

  const featuredAlerts = DATA.consumer_alerts.slice(0, 3);
  const extraAlerts = DATA.consumer_alerts.slice(3);
  const visibleAlerts = showAllChanges ? DATA.consumer_alerts : featuredAlerts;

  const series = useMemo(() => {
    const n = range === "4w" ? 4 : range === "12w" ? 12 : DATA.history.length;
    return DATA.history.slice(-Math.max(n, 1));
  }, [range]);

  const chartPoints = useMemo(() => {
    return series.map((p, i) => ({
      label: sparseLabel(p.label, i, series.length),
      value: p.equifax,
    }));
  }, [series]);

  const chartLines = useMemo(() => {
    return [
      { label: "Experian", values: series.map((p) => p.experian) },
      { label: "TransUnion", values: series.map((p) => p.transunion) },
    ];
  }, [series]);

  const annotations = useMemo(() => {
    return DATA.chart_annotations.flatMap((a) => {
      const at = series.findIndex((p) => p.week === a.week);
      if (at < 0) return [];
      return [{ at, label: a.label, line: a.line }];
    });
  }, [series]);

  const reportAccounts = DATA.accounts.filter((a) => a.bureau === reportBureau);
  const bureauOptions = DATA.bureaus.map((b) => ({ value: b.bureau, label: b.label }));

  return (
    <Page
      title={"Credit Weekly: Dream State (Jordan Example, all 3 FICO 8 scores)"}
      summary={
        "A simple look at how Jordan Example\u2019s weekly dashboard can feel once Equifax, Experian, and TransUnion FICO Score 8s are connected. This is example data, not a live pull."
      }
      width="wide"
    >
      <Section heading="Your FICO Score 8" caption="Equifax from myFICO Free, Experian from Experian free, and TransUnion from CreditWise.">
        <Grid columns={3}>
          {DATA.scores.map((s) => (
            <Section heading={s.label} caption={`FICO Score 8 \u00b7 ${s.source}`} key={s.bureau}>
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
          points={chartPoints}
          lines={chartLines}
          floor={720}
          ceiling={800}
          labels={["Equifax"]}
          annotations={annotations}
        />
        <Callout tone="info" lead="All three sit in Very good">
          The TransUnion dip is likely the new Harbor Premier Bank inquiry. If that was not you, it is worth a closer look.
        </Callout>
      </Section>

      <Section heading="What's moving your score" caption="Plain-English factors on each bureau, not a FICO model breakdown.">
        <Grid columns={3}>
          {DATA.factors.map((f) => (
            <Section heading={f.label} key={f.bureau}>
              <Properties items={f.items} />
            </Section>
          ))}
        </Grid>
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
        {visibleAlerts.length === 1 ? (
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
        caption={`Overall utilization is ${DATA.utilization_meter.pct}% \u00b7 ${DATA.utilization_meter.band_label}`}
      >
        <Grid columns={2}>
          {DATA.next_moves.map((m) => (
            <Section heading={m.title} key={m.title}>
              <Status tone={m.tone}>{m.status}</Status>
              <Text>{m.detail}</Text>
            </Section>
          ))}
        </Grid>
        <Text>{DATA.projection}</Text>
        <UtilizationMeter pct={DATA.utilization_meter.pct} bandId={DATA.utilization_meter.band_id} />
      </Section>

      <Section heading="Your three bureaus">
        <Grid columns={3}>
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
      >
        <Grid columns={2}>
          {DATA.vantage.map((v) => (
            <Section heading={v.label} key={v.label} caption={v.source}>
              <Properties
                items={[
                  { label: "VantageScore 3.0", value: String(v.value) },
                  { label: "As of", value: v.as_of },
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

      <Text>
        This is example data for Jordan Example. The scores shown are FICO Score 8 from free sources once those accounts are connected.
      </Text>
    </Page>
  );
}
