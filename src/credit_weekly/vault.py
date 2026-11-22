"""AES-256-GCM envelope/passphrase encryption for local snapshot storage."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

KDF_ITERATIONS = 310_000


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_json_file(data: dict[str, Any], out_path: str | Path, passphrase: str) -> Path:
    """Encrypt a JSON-serializable object to an AES-256-GCM envelope file."""
    if not passphrase or len(passphrase) < 8:
        raise ValueError("Vault passphrase must be at least 8 characters.")
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    plaintext = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    aad = b"credit-weekly-v1"
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)

    envelope = {
        "v": 1,
        "alg": "AES-256-GCM",
        "kdf": "PBKDF2-SHA256",
        "iterations": KDF_ITERATIONS,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "aad": aad.decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }
    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    os.chmod(dest, 0o600)
    return dest


def decrypt_json_file(enc_path: str | Path, passphrase: str) -> dict[str, Any]:
    """Decrypt an AES-256-GCM envelope file back into a Python dict."""
    envelope = json.loads(Path(enc_path).read_text(encoding="utf-8"))
    if envelope.get("alg") != "AES-256-GCM":
        raise ValueError("Unsupported encryption algorithm.")
    salt = base64.b64decode(envelope["salt"])
    nonce = base64.b64decode(envelope["nonce"])
    aad = envelope["aad"].encode("ascii")
    ciphertext = base64.b64decode(envelope["ciphertext"])
    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
    return json.loads(plaintext.decode("utf-8"))
