import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.canvas_export import build_dashboard_bundle, render_canvas_tsx  # noqa: E402
from credit_weekly.diff import diff_snapshots  # noqa: E402
from credit_weekly.models import mask_account_number, mask_ssn, new_snapshot  # noqa: E402
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
