"""Export PII-minimized weekly credit snapshot + diff into Grok Page (.canvas.tsx) and dashboard data."""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any

from .models import ADVERSE_RATINGS, BUREAUS, BUREAU_LABELS, compute_health_summary, credit_health_band
from .optimizer import classify_utilization_band, optimize_snapshot


ALERT_PRIORITY = {
    "new_hard_inquiry": 0,
    "new_collection": 1,
    "new_public_record": 1,
    "new_late": 1,
    "adverse_change": 1,
    "new_account": 2,
    "limit_change": 3,
    "balance_change": 4,
}

METER_BANDS = [
    {"id": "zero", "label": "0"},
    {"id": "azeo", "label": "1–9"},
    {"id": "benchmark", "label": "10–20"},
    {"id": "ceiling", "label": "21–29"},
    {"id": "blocker", "label": "30+"},
]

_METER_ID = {
    "zero": "zero",
    "azeo_prime": "azeo",
    "benchmark": "benchmark",
    "ceiling_watch": "ceiling",
    "blocker": "blocker",
}


def _fmt_usd(cents: int | None) -> str:
    if cents is None:
        return "—"
    return f"${cents / 100:,.0f}" if cents % 100 == 0 else f"${cents / 100:,.2f}"


def _fmt_short_day(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        d = date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso)
    return f"{d.strftime('%b')} {d.day}"


def _fmt_long_day(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        d = date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def _pretty_creditor(name: str) -> str:
    raw = re.sub(r"\s+", " ", (name or "").strip())
    if not raw:
        return "a creditor"
    parts: list[str] = []
    skip_tail = {"NA", "N.A.", "N.A", "LLC", "INC", "INC.", "CO", "CO.", "CORP", "CORP."}
    words = raw.replace("_", " ").split()
    while words and words[-1].upper().rstrip(".") in {s.rstrip(".") for s in skip_tail}:
        words.pop()
    for w in words:
        up = w.upper()
        if up in {"CU", "FICO", "USB", "HSBC", "BBVA", "TD", "PNC", "USAA"}:
            parts.append(up)
        else:
            parts.append(w.capitalize())
    return " ".join(parts) or "a creditor"


def _as_of(snapshot: dict[str, Any]) -> date:
    raw = str(snapshot.get("captured_at") or snapshot.get("week_label") or "")
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return date.today()


def _enriched_health(snapshot: dict[str, Any]) -> dict[str, Any]:
    bureaus = snapshot.get("bureaus") or {}
    if bureaus:
        return compute_health_summary(bureaus)
    hs = dict(snapshot.get("health_summary") or {})
    if hs.get("credit_health_index") is None:
        from .models import index_from_health_summary

        idx = index_from_health_summary(hs)
        hs["credit_health_index"] = idx
        hs["credit_health_band"] = credit_health_band(idx)
    elif not hs.get("credit_health_band"):
        hs["credit_health_band"] = credit_health_band(int(hs["credit_health_index"]))
    return hs


def _bureau_on_time(accounts: list[dict[str, Any]]) -> float:
    total = 0
    on_time = 0
    for acct in accounts:
        for ph in acct.get("payment_history", []):
            rating = str(ph.get("rating", "")).upper()
            if rating in {"OK", "C", "0"}:
                total += 1
                on_time += 1
            elif rating in ADVERSE_RATINGS:
                total += 1
    return round((on_time / total) * 100, 1) if total else 100.0


def _creditor_from_alert(title: str, category: str) -> str:
    if ":" in title:
        tail = title.split(":", 1)[1].strip()
        if category == "new_hard_inquiry":
            return tail
        m = re.search(r"^(.*?)\s+(balance|credit limit|limit)\b", tail, re.I)
        if m:
            return m.group(1).strip()
        m = re.search(r"^(.*?)\s+(added|opened|closed|changed)\b", tail, re.I)
        if m:
            return m.group(1).strip()
        return tail
    return ""


def _plain_alerts(raw_alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: list[dict[str, Any]] = []
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for al in raw_alerts:
        cat = str(al.get("category") or "other")
        title = str(al.get("title") or "")
        detail = str(al.get("detail") or "")
        bureau = str(al.get("bureau") or "")
        creditor = _creditor_from_alert(title, cat)
        pretty = _pretty_creditor(creditor) if creditor else ""
        label = BUREAU_LABELS.get(bureau, bureau.title() if bureau else "")
        merge_key = (cat, creditor.lower()) if cat in {"balance_change", "limit_change"} and creditor else None

        if merge_key and merge_key in index:
            item = index[merge_key]
            if label and label not in item["bureaus"]:
                item["bureaus"].append(label)
            continue

        status = "Update"
        tone = "neutral"
        heading = title
        body = detail

        if cat == "new_hard_inquiry":
            heading = f"New inquiry from {pretty or 'a creditor'} on {label or 'a bureau'}"
            body = "Was this you?"
            status = "Check"
            tone = "warning"
        elif cat == "new_account":
            heading = f"A new account from {pretty or 'a creditor'} showed up on {label or 'a bureau'}"
            body = "If you didn’t open this, freeze your reports and call the issuer."
            status = "New account"
            tone = "warning"
        elif cat in {"new_collection", "new_public_record", "new_late", "adverse_change"}:
            heading = title
            body = detail or "Take a look and decide whether this is yours."
            status = "Needs a look"
            tone = "danger"
        elif cat == "limit_change":
            amounts = re.findall(r"\$[\d,]+", detail)
            new_lim = amounts[-1] if amounts else ""
            heading = (
                f"{pretty or 'A card'} raised your limit to {new_lim}"
                if new_lim
                else f"{pretty or 'A card'} changed your credit limit"
            )
            body = detail.replace("->", "to") if detail else ""
            status = "Limit up"
            tone = "success"
        elif cat == "balance_change":
            down = "decreased" in title.lower() or "decreased" in detail.lower()
            amt_m = re.search(r"\$[\d,]+(?:\.\d+)?", title)
            amt = amt_m.group(0) if amt_m else ""
            if down:
                heading = f"You paid down {pretty or 'a card'}" + (f" by {amt}" if amt else "")
                body = detail.replace("->", "to") if detail else "Your reported balance went down."
                status = "Paid down"
                tone = "success"
            else:
                heading = f"{pretty or 'A card'} reported a higher balance" + (f" of {amt}" if amt else "")
                body = detail.replace("->", "to") if detail else "Your reported balance went up."
                status = "Balance up"
                tone = "warning"
        else:
            heading = title
            body = detail

        item = {
            "id": f"{cat}-{creditor or bureau or len(grouped)}",
            "category": cat,
            "title": heading.rstrip(".") + ".",
            "detail": body,
            "status": status,
            "tone": tone,
            "bureaus": [label] if label else [],
            "priority": ALERT_PRIORITY.get(cat, 9),
        }
        grouped.append(item)
        if merge_key:
            index[merge_key] = item

    def _dollars(item: dict[str, Any]) -> int:
        m = re.search(r"\$([\d,]+)", f"{item.get('title','')} {item.get('detail','')}")
        return int(m.group(1).replace(",", "")) if m else 0

    grouped.sort(key=lambda x: (int(x["priority"]), -_dollars(x), x["title"]))
    return grouped


def _next_moves(latest: dict[str, Any], as_of: date) -> list[dict[str, Any]]:
    plan = optimize_snapshot(latest, as_of_date=as_of)
    moves: list[dict[str, Any]] = []
    seen: set[str] = set()
    azeo = plan.get("azeo_plan") or {}

    for z in azeo.get("zero_cards") or []:
        amt = int(z.get("current_balance_cents") or 0)
        if amt <= 0:
            continue
        cred = str(z.get("creditor") or "")
        day = _fmt_short_day(z.get("pay_by_date"))
        key = cred.lower()
        seen.add(key)
        moves.append(
            {
                "title": f"Pay {_fmt_usd(amt)} on {_pretty_creditor(cred)} by {day}",
                "detail": "That brings this card to $0 so only one card reports a small balance.",
                "status": "Pay by date",
                "tone": "accent",
                "pay_by_date": z.get("pay_by_date") or "",
                "amount_usd": _fmt_usd(amt),
            }
        )

    keep = azeo.get("keep_balance_card") or {}
    if keep.get("creditor"):
        cred = str(keep["creditor"])
        target = int(keep.get("target_balance_cents") or 0)
        day = _fmt_short_day(keep.get("pay_by_date"))
        seen.add(cred.lower())
        if target > 0:
            moves.append(
                {
                    "title": f"Leave about {_fmt_usd(target)} on {_pretty_creditor(cred)} by {day}",
                    "detail": "Keep this as the one card reporting in the 1–9% band.",
                    "status": "Keep a balance",
                    "tone": "success",
                    "pay_by_date": keep.get("pay_by_date") or "",
                    "amount_usd": _fmt_usd(target),
                }
            )

    for row in plan.get("per_card_pay_by") or []:
        cred = str(row.get("creditor") or "")
        if cred.lower() in seen:
            continue
        pay9 = int(row.get("paydown_to_9_cents") or 0)
        pay20 = int(row.get("paydown_to_20_cents") or 0)
        day = _fmt_short_day(row.get("recommended_pay_by_date"))
        pretty = _pretty_creditor(cred)
        if pay9 > 0:
            moves.append(
                {
                    "title": f"Pay {_fmt_usd(pay9)} on {pretty} by {day} to report under 9%",
                    "detail": "A balance in the 1–9% band is the sweet spot on this card.",
                    "status": "Pay by date",
                    "tone": "accent",
                    "pay_by_date": row.get("recommended_pay_by_date") or "",
                    "amount_usd": _fmt_usd(pay9),
                }
            )
            seen.add(cred.lower())
        elif pay20 > 0:
            moves.append(
                {
                    "title": f"Pay {_fmt_usd(pay20)} on {pretty} by {day} to report under 20%",
                    "detail": "Getting under 20% is the first benchmark before a tighter 1–9% paydown.",
                    "status": "Pay by date",
                    "tone": "warning",
                    "pay_by_date": row.get("recommended_pay_by_date") or "",
                    "amount_usd": _fmt_usd(pay20),
                }
            )
            seen.add(cred.lower())
        if len(moves) >= 3:
            break

    return moves[:3]


def build_dashboard_bundle(
    snapshots: list[dict[str, Any]],
    latest_diff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a strictly PII-scrubbed bundle safe for Grok Page (Canvas) or local UI."""
    ordered = sorted(snapshots, key=lambda s: s.get("captured_at", ""))
    latest = ordered[-1]
    health_by_week: list[dict[str, Any]] = []
    history_points = []
    for s in ordered:
        hs_s = _enriched_health(s)
        health_by_week.append(hs_s)
        history_points.append(
            {
                "week": s.get("week_label", ""),
                "credit_health_index": int(hs_s.get("credit_health_index", 0) or 0),
                "credit_health_band": hs_s.get("credit_health_band") or credit_health_band(int(hs_s.get("credit_health_index", 0) or 0)),
                "utilization_pct": hs_s.get("utilization_pct", 0.0),
                "revolving_balance_usd": round((hs_s.get("revolving_balance_cents", 0) or 0) / 100.0, 2),
                "adverse_accounts": hs_s.get("adverse_accounts", 0),
            }
        )

    hs = health_by_week[-1]
    prev_index = health_by_week[-2]["credit_health_index"] if len(health_by_week) > 1 else None
    current_index = int(hs.get("credit_health_index", 0) or 0)
    delta = None if prev_index is None else current_index - int(prev_index)

    bureau_cards = []
    accounts_flat = []
    inquiries_flat = []
    collections_flat = []
    public_records_flat = []

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
        report_date = rep.get("source", {}).get("report_date", "") or latest.get("captured_at", "")

        bureau_cards.append(
            {
                "bureau": b_key,
                "label": label,
                "report_date": report_date,
                "report_date_display": _fmt_long_day(str(report_date)[:10] if report_date else ""),
                "confidence": rep.get("source", {}).get("confidence", 0),
                "open_accounts": sum(1 for a in accts if a.get("is_open")),
                "total_accounts": len(accts),
                "utilization_pct": util,
                "revolving_balance_usd": _fmt_usd(rev_bal),
                "revolving_limit_usd": _fmt_usd(rev_lim),
                "on_time_pct": _bureau_on_time(accts),
                "adverse_count": sum(1 for a in accts if a.get("is_adverse")) + len(cols) + len(prs),
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
                    "creditor_display": _pretty_creditor(str(a.get("creditor", ""))),
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


    raw_alerts = list((latest_diff or {}).get("alerts", []))
    consumer_alerts = _plain_alerts(raw_alerts)

    inquiry_weeks: list[dict[str, str]] = []
    seen_weeks: set[str] = set()
    current_week = latest.get("week_label", "")
    for al in raw_alerts:
        if al.get("category") != "new_hard_inquiry":
            continue
        week = current_week
        if week and week not in seen_weeks:
            inquiry_weeks.append({"week": week, "label": "New inquiry"})
            seen_weeks.add(week)

    band = classify_utilization_band(
        float(hs.get("utilization_pct", 0.0) or 0.0),
        int(hs.get("revolving_balance_cents", 0) or 0),
    )
    as_of = _as_of(latest)

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
            "credit_health_index": current_index,
            "credit_health_band": hs.get("credit_health_band") or credit_health_band(current_index),
            "credit_health_delta": delta,
        },
        "history": history_points,
        "chart_annotations": inquiry_weeks,
        "utilization_meter": {
            "pct": hs.get("utilization_pct", 0.0),
            "band_id": _METER_ID.get(str(band.get("id")), "benchmark"),
            "band_label": band.get("range") or "",
            "bands": METER_BANDS,
        },
        "consumer_alerts": consumer_alerts,
        "next_moves": _next_moves(latest, as_of),
        "bureaus": bureau_cards,
        "alerts": raw_alerts,
        "metric_deltas": (latest_diff or {}).get("metric_deltas", {}),
        "accounts": accounts_flat,
        "collections": collections_flat,
        "inquiries": inquiries_flat,
        "public_records": public_records_flat,
    }


TSX_TEMPLATE = r'''import {
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

const DATA = __DATA_JSON__ as {
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
      title={__PAGE_TITLE__}
      summary={__PAGE_SUMMARY__}
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
'''


def render_canvas_tsx(bundle: dict[str, Any]) -> str:
    """Emit a self-contained grok/canvas .tsx page from the PII-scrubbed bundle."""
    hs = bundle.get("health_summary") or {}
    page_bundle = {
        "week_label": bundle.get("week_label", ""),
        "is_example_data": bool(bundle.get("is_example_data")),
        "health_summary": {
            "credit_health_index": hs.get("credit_health_index", 0),
            "credit_health_band": hs.get("credit_health_band", ""),
            "credit_health_delta": hs.get("credit_health_delta"),
            "utilization_pct": hs.get("utilization_pct", 0.0),
        },
        "history": [
            {"week": h.get("week", ""), "credit_health_index": h.get("credit_health_index", 0)}
            for h in bundle.get("history") or []
        ],
        "chart_annotations": bundle.get("chart_annotations") or [],
        "utilization_meter": bundle.get("utilization_meter") or {},
        "consumer_alerts": [
            {
                "id": a.get("id", ""),
                "title": a.get("title", ""),
                "detail": a.get("detail", ""),
                "status": a.get("status", ""),
                "tone": a.get("tone", "neutral"),
            }
            for a in bundle.get("consumer_alerts") or []
        ],
        "next_moves": [
            {
                "title": m.get("title", ""),
                "detail": m.get("detail", ""),
                "status": m.get("status", ""),
                "tone": m.get("tone", "neutral"),
            }
            for m in bundle.get("next_moves") or []
        ],
        "bureaus": [
            {
                "bureau": b.get("bureau", ""),
                "label": b.get("label", ""),
                "utilization_pct": b.get("utilization_pct", 0.0),
                "on_time_pct": b.get("on_time_pct", 100.0),
                "hard_inquiries": b.get("hard_inquiries", 0),
                "adverse_count": b.get("adverse_count", 0),
                "report_date_display": b.get("report_date_display", ""),
            }
            for b in bundle.get("bureaus") or []
        ],
        "accounts": [
            {
                "bureau": a.get("bureau", ""),
                "creditor_display": a.get("creditor_display", ""),
                "masked": a.get("masked", "****"),
                "balance": a.get("balance", "—"),
                "limit": a.get("limit", "—"),
                "util": a.get("util", "—"),
            }
            for a in bundle.get("accounts") or []
        ],
    }
    data_json = json.dumps(page_bundle, indent=2, ensure_ascii=False)
    if bundle.get("is_example_data"):
        title = "Credit Weekly: Example Dashboard (Jordan Example)"
        summary = (
            "A simple weekly look at Jordan Example’s reports. "
            "The Credit-Health Index is not a FICO score."
        )
    else:
        week = bundle.get("week_label") or "this week"
        title = f"Credit Weekly · {week}"
        summary = "A simple weekly look at your reports. The Credit-Health Index is not a FICO score."
    return (
        TSX_TEMPLATE.replace("__DATA_JSON__", data_json)
        .replace("__PAGE_TITLE__", json.dumps(title))
        .replace("__PAGE_SUMMARY__", json.dumps(summary))
    )
