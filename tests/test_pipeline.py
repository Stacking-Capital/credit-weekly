import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.canvas_export import build_dashboard_bundle, render_canvas_tsx  # noqa: E402
from credit_weekly.diff import diff_snapshots  # noqa: E402
from credit_weekly.models import (  # noqa: E402
    compute_credit_health_index,
    credit_health_band,
    mask_account_number,
    mask_ssn,
    new_snapshot,
)
from credit_weekly.parsers import parse_report_file  # noqa: E402
from credit_weekly.vault import decrypt_json_file, encrypt_json_file  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_pii_masking(self):
        self.assertEqual(mask_ssn("123-45-6789"), "6789")
        self.assertEqual(mask_account_number("4111009988771234"), "****1234")
        self.assertEqual(mask_account_number("411100****1234"), "****1234")

    def test_parse_and_diff_and_bundle(self):
        tu1 = parse_report_file(ROOT / "fixtures" / "example_week1_transunion.txt", bureau="transunion")
        tu2 = parse_report_file(ROOT / "fixtures" / "example_week2_transunion.txt", bureau="transunion")
        self.assertEqual(len(tu1["accounts"]), 3)
        self.assertEqual(tu1["personal_info"]["ssn_last4"], "0000")
        self.assertEqual(tu1["personal_info"]["dob_year"], "1990")

        s1 = new_snapshot({"transunion": tu1}, week_label="2026-W46", is_example_data=True)
        s2 = new_snapshot({"transunion": tu2}, week_label="2026-W47", is_example_data=True)
        diff = diff_snapshots(s1, s2)
        categories = {a["category"] for a in diff["alerts"]}
        self.assertIn("new_hard_inquiry", categories)
        self.assertIn("balance_change", categories)

        bundle = build_dashboard_bundle([s1, s2], diff)
        tsx = render_canvas_tsx(bundle)
        self.assertIn('from "grok/canvas"', tsx)
        self.assertNotIn("000-00-0000", tsx)

        self.assertIn("Not a FICO score", tsx)
        self.assertIn("credit_health_index", tsx)

    def test_credit_health_index_formula(self):
        # 7.9% util is in the 1–9 band (30 pts); 100% on-time (35);
        # 1 adverse (20-8=12); 3 hard inquiries (15-3=12) => 89.
        self.assertEqual(compute_credit_health_index(7.9, 100.0, 1, 0, 0, 3), 89)
        self.assertEqual(credit_health_band(89), "Good")
        # 16.7% util interpolates 9–20 (22 pts); 2 inquiries stay at 15 => 84.
        self.assertEqual(compute_credit_health_index(16.7, 100.0, 1, 0, 0, 2), 84)
        self.assertEqual(credit_health_band(84), "Good")
        # A 0% balance is slightly dinged versus 1–9%.
        self.assertEqual(compute_credit_health_index(0.0, 100.0, 0, 0, 0, 0), 97)
        self.assertEqual(credit_health_band(97), "Excellent")
        self.assertEqual(credit_health_band(70), "Fair")
        self.assertEqual(credit_health_band(49), "At risk")

    def test_consumer_dashboard_bundle(self):
        s1 = json.loads((ROOT / "fixtures" / "example_snapshot_week1.json").read_text(encoding="utf-8"))
        s2 = json.loads((ROOT / "fixtures" / "example_snapshot_week2.json").read_text(encoding="utf-8"))
        diff = diff_snapshots(s1, s2)
        bundle = build_dashboard_bundle([s1, s2], diff)
        self.assertEqual(bundle["health_summary"]["credit_health_index"], 89)
        self.assertEqual(bundle["health_summary"]["credit_health_band"], "Good")
        self.assertEqual(bundle["health_summary"]["credit_health_delta"], 5)
        self.assertEqual(bundle["history"][0]["credit_health_index"], 84)
        self.assertEqual(bundle["history"][1]["credit_health_index"], 89)
        self.assertTrue(any(a["week"] == "2026-W47" for a in bundle["chart_annotations"]))
        self.assertLessEqual(len(bundle["next_moves"]), 3)
        self.assertGreaterEqual(len(bundle["next_moves"]), 1)
        self.assertTrue(any("Harbor Premier" in a["title"] for a in bundle["consumer_alerts"]))
        self.assertTrue(any("Was this you?" in a["detail"] for a in bundle["consumer_alerts"]))
        tsx = render_canvas_tsx(bundle)
        self.assertIn("Not a FICO score", tsx)
        self.assertIn("Your Credit-Health Index", tsx)
        self.assertIn("This week", tsx)
        self.assertIn("What to do this week", tsx)
        self.assertIn("See all changes", tsx)
        self.assertIn("Your three bureaus", tsx)
        self.assertIn("See full report", tsx)
        self.assertIn("collapsible", tsx)
        self.assertIn("Not a FICO score", tsx)  # hero label lock
        self.assertIn("New inquiry", tsx)
        self.assertNotIn("000-00-0000", tsx)
        self.assertNotIn("type ViewTab", tsx)

    def test_aes_gcm_vault_roundtrip(self):
        payload = {"week_label": "2026-W47", "accounts": [{"creditor": "SUMMIT BANK NA", "masked": "****1234"}]}
        with tempfile.TemporaryDirectory() as tmp:
            enc_path = Path(tmp) / "snap.enc.json"
            encrypt_json_file(payload, enc_path, "correct-horse-battery-staple")
            raw_text = enc_path.read_text(encoding="utf-8")
            self.assertNotIn("SUMMIT BANK NA", raw_text)
            decrypted = decrypt_json_file(enc_path, "correct-horse-battery-staple")
            self.assertEqual(decrypted, payload)
            with self.assertRaises(Exception):
                decrypt_json_file(enc_path, "wrong-passphrase")


if __name__ == "__main__":
    unittest.main()
