import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_weekly.vault import (  # noqa: E402
    VaultError,
    decrypt_json_file,
    encrypt_json_file,
)


PASSPHRASE = "correct-horse-battery-staple"
PAYLOAD = {"week_label": "2026-W47", "accounts": [{"creditor": "SUMMIT BANK NA", "masked": "****1234"}]}


class VaultHardeningTests(unittest.TestCase):
    def test_wrong_key_fails_without_leaking_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            enc_path = Path(tmp) / "snap.enc.json"
            encrypt_json_file(PAYLOAD, enc_path, PASSPHRASE)
            with self.assertRaises(VaultError) as ctx:
                decrypt_json_file(enc_path, "wrong-passphrase")
            msg = str(ctx.exception)
            self.assertEqual(msg, "Decryption failed.")
            self.assertNotIn("SUMMIT BANK NA", msg)
            self.assertNotIn(PASSPHRASE, msg)
            self.assertNotIn("wrong-passphrase", msg)

    def test_tampered_ciphertext_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            enc_path = Path(tmp) / "snap.enc.json"
            encrypt_json_file(PAYLOAD, enc_path, PASSPHRASE)
            envelope = json.loads(enc_path.read_text(encoding="utf-8"))
            raw = bytearray(__import__("base64").b64decode(envelope["ciphertext"]))
            raw[0] ^= 0x01
            envelope["ciphertext"] = __import__("base64").b64encode(bytes(raw)).decode("ascii")
            enc_path.write_text(json.dumps(envelope), encoding="utf-8")
            with self.assertRaises(VaultError) as ctx:
                decrypt_json_file(enc_path, PASSPHRASE)
            self.assertEqual(str(ctx.exception), "Decryption failed.")
            self.assertNotIn("SUMMIT BANK NA", str(ctx.exception))

    def test_nonce_reuse_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "one.enc.json"
            second = Path(tmp) / "two.enc.json"
            encrypt_json_file(PAYLOAD, first, PASSPHRASE)
            first_env = json.loads(first.read_text(encoding="utf-8"))
            salt = __import__("base64").b64decode(first_env["salt"])
            nonce = __import__("base64").b64decode(first_env["nonce"])
            # Force the next write to reuse the same salt and nonce.
            with patch("credit_weekly.vault.os.urandom", side_effect=lambda n: salt if n == 16 else nonce):
                with self.assertRaises(VaultError) as ctx:
                    encrypt_json_file({"week_label": "other"}, second, PASSPHRASE)
            self.assertIn("unique salt and nonce", str(ctx.exception).lower())
            self.assertFalse(second.exists())

    def test_two_encrypts_use_distinct_nonces_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.enc.json"
            b = Path(tmp) / "b.enc.json"
            encrypt_json_file(PAYLOAD, a, PASSPHRASE)
            encrypt_json_file(PAYLOAD, b, PASSPHRASE)
            ea = json.loads(a.read_text(encoding="utf-8"))
            eb = json.loads(b.read_text(encoding="utf-8"))
            self.assertNotEqual((ea["salt"], ea["nonce"]), (eb["salt"], eb["nonce"]))
            self.assertEqual(decrypt_json_file(a, PASSPHRASE), PAYLOAD)
            self.assertEqual(decrypt_json_file(b, PASSPHRASE), PAYLOAD)
            self.assertNotIn("SUMMIT BANK NA", a.read_text(encoding="utf-8"))

    def test_cli_decrypt_stdout_has_no_payload_or_secret(self):
        from credit_weekly.cli import cmd_decrypt

        with tempfile.TemporaryDirectory() as tmp:
            enc_path = Path(tmp) / "snap.enc.json"
            out_path = Path(tmp) / "out.json"
            encrypt_json_file(PAYLOAD, enc_path, PASSPHRASE)
            args = type("Args", (), {"input": str(enc_path), "out": str(out_path), "passphrase": PASSPHRASE})()
            buf = io.StringIO()
            with patch("sys.stdout", buf):
                cmd_decrypt(args)
            printed = buf.getvalue()
            self.assertIn(str(out_path), printed)
            self.assertNotIn("SUMMIT BANK NA", printed)
            self.assertNotIn(PASSPHRASE, printed)
            self.assertEqual(decrypt_json_file(enc_path, PASSPHRASE), json.loads(out_path.read_text(encoding="utf-8")))
            mode = oct(out_path.stat().st_mode & 0o777)
            self.assertEqual(mode, "0o600")


if __name__ == "__main__":
    unittest.main()
