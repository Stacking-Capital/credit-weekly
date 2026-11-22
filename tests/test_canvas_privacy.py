import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.canvas_export import (  # noqa: E402
    assert_canvas_safe,
    build_dashboard_bundle,
    render_canvas_tsx,
)
from credit_weekly.cli import cmd_demo  # noqa: E402
from credit_weekly.diff import diff_snapshots  # noqa: E402


class CanvasPrivacyTests(unittest.TestCase):
    def test_example_page_and_bundle_have_no_secrets_or_pii(self):
        s1 = json.loads((ROOT / "fixtures" / "example_snapshot_week1.json").read_text(encoding="utf-8"))
        s2 = json.loads((ROOT / "fixtures" / "example_snapshot_week2.json").read_text(encoding="utf-8"))
        bundle = build_dashboard_bundle([s1, s2], diff_snapshots(s1, s2))
        tsx = render_canvas_tsx(bundle)
        blob = json.dumps(bundle) + "\n" + tsx
        assert_canvas_safe(blob)
        for token in ("000-00-0000", "100 Maple", "password=", "otp=", "BEGIN RSA", "passphrase="):
            self.assertNotIn(token, blob)

    def test_guard_rejects_ssn(self):
        with self.assertRaises(ValueError):
            assert_canvas_safe("ssn 000-00-0000")

    def test_demo_stdout_has_no_pii(self):
        buf = io.StringIO()
        args = type("Args", (), {"root": str(ROOT)})()
        with redirect_stdout(buf):
            cmd_demo(args)
        out = buf.getvalue()
        self.assertNotIn("000-00-0000", out)
        self.assertNotIn("100 Maple", out)
        self.assertNotIn("correct-horse-battery-staple", out)

    def test_demo_does_not_overwrite_canonical_example_page(self):
        path = ROOT / "dashboard" / "ExampleDashboard.canvas.tsx"
        before = path.read_text(encoding="utf-8")
        buf = io.StringIO()
        args = type("Args", (), {"root": str(ROOT)})()
        with redirect_stdout(buf):
            cmd_demo(args)
        after = path.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        generated = ROOT / "dashboard" / "generated-demo.canvas.tsx"
        self.assertTrue(generated.is_file())


if __name__ == "__main__":
    unittest.main()
