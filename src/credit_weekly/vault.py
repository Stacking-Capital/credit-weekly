"""AES-256-GCM envelope/passphrase encryption for local snapshot storage."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

KDF_ITERATIONS = 310_000
SALT_BYTES = 16
NONCE_BYTES = 12
AAD = b"credit-weekly-v1"
ALG = "AES-256-GCM"


class VaultError(ValueError):
    """Safe vault failure. Messages must never include passphrase, key, plaintext, or ciphertext."""


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def _b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _b64decode(label: str, value: Any) -> bytes:
    if not isinstance(value, str) or not value:
        raise VaultError(f"Envelope field {label} is missing or not valid.")
    try:
        return base64.b64decode(value, validate=True)
    except Exception as exc:
        raise VaultError(f"Envelope field {label} is missing or not valid.") from exc


def _sibling_salt_nonces(directory: Path, skip: Path | None) -> set[tuple[str, str]]:
    used: set[tuple[str, str]] = set()
    if not directory.is_dir():
        return used
    for path in directory.iterdir():
        if skip is not None and path.resolve() == skip.resolve():
            continue
        if not path.is_file():
            continue
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        salt = envelope.get("salt")
        nonce = envelope.get("nonce")
        if isinstance(salt, str) and isinstance(nonce, str):
            used.add((salt, nonce))
    return used


def _new_salt_and_nonce(dest: Path) -> tuple[bytes, bytes]:
    used = _sibling_salt_nonces(dest.parent, skip=dest if dest.exists() else None)
    for _ in range(16):
        salt = os.urandom(SALT_BYTES)
        nonce = os.urandom(NONCE_BYTES)
        pair = (_b64encode(salt), _b64encode(nonce))
        if pair not in used:
            return salt, nonce
    raise VaultError("Could not allocate a unique salt and nonce.")


def _reject_reused_salt_nonce(dest: Path, salt: bytes, nonce: bytes) -> None:
    pair = (_b64encode(salt), _b64encode(nonce))
    if pair in _sibling_salt_nonces(dest.parent, skip=dest if dest.exists() else None):
        raise VaultError("Refusing to write an envelope that reuses a salt and nonce.")


def encrypt_json_file(data: dict[str, Any], out_path: str | Path, passphrase: str) -> Path:
    """Encrypt a JSON-serializable object to an AES-256-GCM envelope file."""
    if not passphrase or len(passphrase) < 8:
        raise VaultError("Vault passphrase must be at least 8 characters.")
    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    salt, nonce = _new_salt_and_nonce(dest)
    _reject_reused_salt_nonce(dest, salt, nonce)
    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    plaintext = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, AAD)

    envelope = {
        "v": 1,
        "alg": ALG,
        "kdf": "PBKDF2-SHA256",
        "iterations": KDF_ITERATIONS,
        "salt": _b64encode(salt),
        "nonce": _b64encode(nonce),
        "aad": AAD.decode("ascii"),
        "ciphertext": _b64encode(ciphertext),
    }
    dest.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    os.chmod(dest, 0o600)
    return dest


def decrypt_json_file(enc_path: str | Path, passphrase: str) -> dict[str, Any]:
    """Decrypt an AES-256-GCM envelope file back into a Python dict."""
    if not passphrase:
        raise VaultError("Vault passphrase is required.")
    try:
        envelope = json.loads(Path(enc_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise VaultError("Vault envelope could not be read.") from exc
    if not isinstance(envelope, dict):
        raise VaultError("Vault envelope could not be read.")
    if envelope.get("alg") != ALG:
        raise VaultError("Unsupported encryption algorithm.")
    salt = _b64decode("salt", envelope.get("salt"))
    nonce = _b64decode("nonce", envelope.get("nonce"))
    if len(salt) != SALT_BYTES or len(nonce) != NONCE_BYTES:
        raise VaultError("Vault envelope is malformed.")
    aad_value = envelope.get("aad")
    if not isinstance(aad_value, str):
        raise VaultError("Vault envelope is malformed.")
    try:
        aad = aad_value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise VaultError("Vault envelope is malformed.") from exc
    ciphertext = _b64decode("ciphertext", envelope.get("ciphertext"))
    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
    except InvalidTag as exc:
        raise VaultError("Decryption failed.") from exc
    except Exception as exc:
        raise VaultError("Decryption failed.") from exc
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VaultError("Decryption failed.") from exc
    if not isinstance(payload, dict):
        raise VaultError("Decryption failed.")
    return payload
