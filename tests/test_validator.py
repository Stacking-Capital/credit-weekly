import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.validator import (  # noqa: E402
    SnapshotValidationError,
    iter_snapshot_errors,
    validate_snapshot,
)


class ValidatorTests(unittest.TestCase):
    def _load(self, name: str) -> dict:
        return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))

    def test_stage_fixtures_and_weeks_validate(self):
        for name in (
            "example_snapshot_week1.json",
            "example_snapshot_week2.json",
            "stage1_snapshot.json",
            "stage2_snapshot.json",
            "stage3_snapshot.json",
        ):
            with self.subTest(name=name):
                snap = self._load(name)
                validate_snapshot(snap)
                self.assertTrue(snap.get("is_example_data"))
                self.assertEqual(snap.get("schema_version"), "1.0.0")

    def test_stage_scores_are_labeled_and_synthetic(self):
        stage2 = self._load("stage2_snapshot.json")
        models = {s["model"] for s in stage2["scores"]}
        self.assertIn("FICO Score 8", models)
        self.assertIn("VantageScore 3.0", models)
        self.assertTrue(any(s["bureau"] == "experian" and s["is_fico"] for s in stage2["scores"]))
        self.assertTrue(any(s["model"] == "VantageScore 3.0" and not s["is_fico"] for s in stage2["scores"]))

        stage3 = self._load("stage3_snapshot.json")
        fico_bureaus = {s["bureau"] for s in stage3["scores"] if s["model"] == "FICO Score 8"}
        self.assertEqual(fico_bureaus, {"equifax", "experian", "transunion"})
        for snap in (stage2, stage3):
            for bureau in snap["bureaus"].values():
                self.assertEqual(bureau["personal_info"].get("ssn_last4"), "0000")

    def test_invalid_snapshot_fails_without_leaking_values(self):
        bad = {"schema_version": "0.0.0", "snapshot_id": "x"}
        with self.assertRaises(SnapshotValidationError) as ctx:
            validate_snapshot(bad)
        msg = str(ctx.exception)
        self.assertIn("constraint failed", msg)
        self.assertNotIn("0.0.0", msg)

    def test_error_list_is_value_free(self):
        errors = iter_snapshot_errors({"schema_version": "9.9.9"})
        self.assertTrue(errors)
        blob = " ".join(errors)
        self.assertNotIn("9.9.9", blob)


if __name__ == "__main__":
    unittest.main()
