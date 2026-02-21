import os
import tempfile

from app.vault import init_vault, unlock_entries, add_entry


def test_vault_init_and_add_unlock():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "vault.securepass")
        init_vault(path, "master123")
        add_entry(path, "master123", "Test", "user", "Pass123!")
        entries = unlock_entries(path, "master123")
        assert len(entries) == 1
        assert entries[0].label == "Test"
