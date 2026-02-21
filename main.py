from __future__ import annotations
import os

from app.core import SecurePassApp
from app.gui import SecurePassGUI
from app.logger import AppLogger


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base, "assets", "app.log")
    vault_path = os.path.join(base, "assets", "vault.securepass")

    logger = AppLogger(path=log_path)
    app = SecurePassApp(logger=logger, vault_path=vault_path)

    gui = SecurePassGUI(app)
    gui.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
