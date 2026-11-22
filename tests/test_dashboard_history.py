import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.canvas_export import build_dashboard_bundle, render_canvas_tsx  # noqa: E402
from credit_weekly.diff import diff_snapshots  # noqa: E402


class DashboardHistoryTests(unittest.TestCase):
    def test_example_history_is_twelve_weeks_with_marks(self):
        history = json.loads((ROOT / "fixtures" / "example_chi_history.json").read_text(encoding="utf-8"))
        s1 = json.loads((ROOT / "fixtures" / "example_snapshot_week1.json").read_text(encoding="utf-8"))
        s2 = json.loads((ROOT / "fixtures" / "example_snapshot_week2.json").read_text(encoding="utf-8"))
        bundle = build_dashboard_bundle([*history, s1, s2], diff_snapshots(s1, s2))
        weeks = [h["week"] for h in bundle["history"]]
        self.assertEqual(len(weeks), 12)
        self.assertEqual(weeks[0], "2026-W36")
        self.assertEqual(weeks[-2:], ["2026-W46", "2026-W47"])
        self.assertEqual(bundle["history"][0]["credit_health_index"], 76)
        self.assertEqual(bundle["history"][-2]["credit_health_index"], 84)
        self.assertEqual(bundle["history"][-1]["credit_health_index"], 89)
        labels = {a["label"] for a in bundle["chart_annotations"]}
        self.assertEqual(labels, {"Paid down", "New inquiry"})
        self.assertTrue(all(a["week"] == "2026-W47" for a in bundle["chart_annotations"]))
        tsx = render_canvas_tsx(bundle)
        self.assertIn("Not a FICO score", tsx)
        self.assertIn("is_example_data", tsx)
        self.assertIn('"is_example_data": true', tsx)
        self.assertNotIn("FICO Score", tsx)
        self.assertNotIn("000-00-0000", tsx)


if __name__ == "__main__":
    unittest.main()
