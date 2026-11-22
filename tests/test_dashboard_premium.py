"""Premium consumer dashboard locks and empty / updating states."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.canvas_export import build_dashboard_bundle, render_canvas_tsx  # noqa: E402
from credit_weekly.diff import diff_snapshots  # noqa: E402


def _load(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


class DashboardPremiumTests(unittest.TestCase):
    def test_example_pages_keep_locks_and_premium_structure(self) -> None:
        beta = (ROOT / "dashboard" / "ExampleDashboard.canvas.tsx").read_text(encoding="utf-8")
        dream = (ROOT / "dashboard" / "DreamStateDashboard.canvas.tsx").read_text(encoding="utf-8")
        for src, name in ((beta, "beta"), (dream, "dream")):
            self.assertIn("What to do this week", src, name)
            self.assertIn("collapsible", src, name)
            self.assertIn("example data", src.lower(), name)
            self.assertNotIn("\u2014", src, name)
            self.assertNotIn("—", src, name)
            self.assertNotIn("will increase your score by", src.lower(), name)
            self.assertNotIn("points guaranteed", src.lower(), name)
        self.assertIn("Not a FICO score", beta)
        self.assertIn("Paid down", beta)
        self.assertIn("New inquiry", beta)
        self.assertIn("2026-W36", beta)
        self.assertIn('"credit_health_index": 76', beta)
        # Stage 1 must not present the index as a FICO Score product name
        self.assertNotIn("FICO Score", beta.split("Not a FICO score")[0] + beta.split("Not a FICO score")[-1])
        for bureau, source in (
            ("Equifax", "myFICO Free"),
            ("Experian", "Experian free"),
            ("TransUnion", "CreditWise"),
        ):
            self.assertIn(bureau, dream)
            self.assertIn(source, dream)
            self.assertIn("FICO Score 8", dream)
        self.assertIn("VantageScore 3.0", dream)
        self.assertIn("typically helps FICO scores", dream)
        self.assertNotIn("will raise your FICO", dream.lower())
        self.assertIn("joinSentences", beta)
        self.assertIn("joinSentences", dream)
        self.assertIn("by Dec 8", beta)
        self.assertRegex(beta, r'"week":\s*"2026-W46"[\s\S]*?"label":\s*"Paid down"')
        self.assertRegex(beta, r'"week":\s*"2026-W47"[\s\S]*?"label":\s*"New inquiry"')
        self.assertRegex(dream, r'week:\s*"2026-W46"[\s\S]*?label:\s*"Paid down"')
        self.assertRegex(dream, r'week:\s*"2026-W47"[\s\S]*?label:\s*"New inquiry"')
        fig = dream.split("function ScoreFigure")[1].split("function UtilizationMeter")[0]
        self.assertNotIn("FICO Score 8", fig)
        self.assertIn("FICO Score 8 · ${s.source}", dream)
        self.assertEqual(dream.count("caption={`FICO Score 8 · ${s.source}`}"), 1)
        self.assertIn('label: "Nov 21"', dream)
        self.assertIn('as_of: "Nov 21, 2026"', dream)
        self.assertIn('as_of: "Nov 5, 2026"', dream)
        self.assertIn('report_date_display: "Nov 21, 2026"', dream)
        self.assertNotIn('label: "Nov 16"', dream)
        for src in (beta, dream):
            self.assertIn("$10,000 to $12,000", src)
            self.assertIn("$1,850 to $950", src)
            self.assertIn("$240", src)
            self.assertIn("$400", src)
            self.assertNotIn('limit: "$10,000"', src)
            self.assertNotIn('"limit": "$10,000"', src)
        self.assertIn("const labelPx = 14", beta)
        self.assertIn("const labelPx = 14", dream)
        self.assertIn("function HistoryChart", beta)
        self.assertIn("function HistoryChart", dream)
        hist = beta[beta.index("function HistoryChart"):beta.index("function IndexHero")]
        self.assertIn("theme.text.secondary", hist)
        self.assertNotIn("theme.text.tertiary", hist)

    def test_export_matches_beta_layout_and_states(self) -> None:
        s1 = _load("example_snapshot_week1.json")
        s2 = _load("example_snapshot_week2.json")
        bundle = build_dashboard_bundle([s1, s2], diff_snapshots(s1, s2))
        bundle["is_example_data"] = True
        tsx = render_canvas_tsx(bundle)
        self.assertIn("Not a FICO score", tsx)
        self.assertIn("What to do this week", tsx)
        self.assertIn("Quiet week. No new inquiries, late marks, or surprises.", tsx)
        self.assertIn("Your history will build here after the next weekly pull.", tsx)
        self.assertIn("Updating this week", tsx)
        self.assertIn("Last week stays on the page until the new pull is ready.", tsx)
        self.assertIn("This page uses example data for Jordan Example", tsx)
        self.assertIn("collapsible", tsx)
        self.assertIn("page_state", tsx)
        self.assertIn("as_of_display", tsx)
        self.assertIn("function chiScale", tsx)
        updating = dict(bundle)
        updating["page_state"] = "updating"
        self.assertIn('"page_state": "updating"', render_canvas_tsx(updating))
        first = dict(bundle)
        first["page_state"] = "first_week"
        first["history"] = [bundle["history"][-1]]
        first["health_summary"] = dict(bundle["health_summary"], credit_health_delta=None)
        first_tsx = render_canvas_tsx(first)
        self.assertIn("first_week", first_tsx)
        self.assertIn("First week on file", first_tsx)

    def test_empty_moves_copy_is_calm(self) -> None:
        s1 = _load("example_snapshot_week1.json")
        s2 = _load("example_snapshot_week2.json")
        bundle = build_dashboard_bundle([s1, s2], diff_snapshots(s1, s2))
        bundle["next_moves"] = []
        bundle["consumer_alerts"] = []
        tsx = render_canvas_tsx(bundle)
        self.assertIn("You are in good shape. Keep paying on time and stay in this band.", tsx)
        self.assertIn("Quiet week. No new inquiries, late marks, or surprises.", tsx)
        self.assertNotIn("TODO", tsx)
        self.assertNotIn("No data", tsx)


if __name__ == "__main__":
    unittest.main()
