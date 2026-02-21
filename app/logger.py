from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from .utils import now_iso


@dataclass
class AppLogger:
    path: str

    def _write(self, level: str, msg: str) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"{now_iso()} [{level}] {msg}\n")

    def info(self, msg: str) -> None:
        self._write("INFO", msg)

    def error(self, msg: str) -> None:
        self._write("ERROR", msg)
