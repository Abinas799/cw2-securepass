from __future__ import annotations
from typing import List

from .models import PasswordPolicy, StrengthReport, VaultEntry
from .generator import generate_password, PolicyError
from .strength import score_password
from .vault import init_vault, unlock_entries, add_entry, VaultError
from .logger import AppLogger
from .datastructures import HashTable
from .utils import safe_label


class SecurePassApp:
    """
    Orchestrator (similar style to CW1 core.py):
      - generates password using policy
      - scores password strength
      - manages encrypted vault
      - uses custom HashTable for common-password checks
    """

    def __init__(self, logger: AppLogger, vault_path: str) -> None:
        self.log = logger
        self.vault_path = vault_path

        # small offline common-password list (can expand later)
        self.common = HashTable[str, bool](capacity=211)
        for p in ["password", "123456", "qwerty", "admin", "letmein", "iloveyou", "welcome", "12345678"]:
            self.common.put(p, True)

    def is_common_password(self, pw: str) -> bool:
        return self.common.contains(pw.lower())

    def generate_and_score(self, policy: PasswordPolicy) -> tuple[str, StrengthReport]:
        pw = generate_password(policy)
        rep = score_password(pw, common_hit=self.is_common_password(pw))
        self.log.info("Generated password (value not logged)")
        return pw, rep

    # Vault actions
    def ensure_vault(self, master_password: str) -> None:
        init_vault(self.vault_path, master_password)

    def vault_list(self, master_password: str) -> List[VaultEntry]:
        return unlock_entries(self.vault_path, master_password)

    def vault_add(self, master_password: str, label: str, username: str, password: str) -> VaultEntry:
        label = safe_label(label)
        username = safe_label(username)
        if not label:
            label = "Saved Password"
        e = add_entry(self.vault_path, master_password, label, username, password)
        self.log.info(f"Vault add entry label='{label}'")
        return e
