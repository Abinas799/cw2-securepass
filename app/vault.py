from __future__ import annotations
import base64
import json
import os
from dataclasses import asdict
from typing import List

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .models import VaultEntry
from .utils import now_iso


class VaultError(Exception):
    pass


def _kdf(master_password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(master_password.encode("utf-8"))


def init_vault(path: str, master_password: str) -> None:
    if os.path.exists(path):
        return
    salt = os.urandom(16)
    key = _kdf(master_password, salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    empty_payload = json.dumps({"entries": []}).encode("utf-8")
    ct = aes.encrypt(nonce, empty_payload, None)
    blob = {
        "v": 1,
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct": base64.b64encode(ct).decode(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blob, f, indent=2)


def _load_blob(path: str) -> dict:
    if not os.path.exists(path):
        raise VaultError("Vault file not found. Initialize vault first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def unlock_entries(path: str, master_password: str) -> List[VaultEntry]:
    blob = _load_blob(path)
    salt = base64.b64decode(blob["salt"])
    nonce = base64.b64decode(blob["nonce"])
    ct = base64.b64decode(blob["ct"])
    key = _kdf(master_password, salt)
    aes = AESGCM(key)
    try:
        pt = aes.decrypt(nonce, ct, None)
    except Exception as e:
        raise VaultError("Invalid master password or corrupted vault.") from e

    data = json.loads(pt.decode("utf-8"))
    out: List[VaultEntry] = []
    for item in data.get("entries", []):
        out.append(VaultEntry(**item))
    return out


def save_entries(path: str, master_password: str, entries: List[VaultEntry]) -> None:
    blob = _load_blob(path)
    salt = base64.b64decode(blob["salt"])
    key = _kdf(master_password, salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    payload = json.dumps({"entries": [asdict(e) for e in entries]}).encode("utf-8")
    ct = aes.encrypt(nonce, payload, None)
    blob["nonce"] = base64.b64encode(nonce).decode()
    blob["ct"] = base64.b64encode(ct).decode()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blob, f, indent=2)


def add_entry(path: str, master_password: str, label: str, username: str, password: str) -> VaultEntry:
    entries = unlock_entries(path, master_password)
    entry = VaultEntry(label=label, username=username, password=password, created_at_iso=now_iso())
    entries.append(entry)
    save_entries(path, master_password, entries)
    return entry
