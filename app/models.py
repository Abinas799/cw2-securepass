from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PasswordPolicy:
    length: int
    use_lower: bool
    use_upper: bool
    use_digits: bool
    use_symbols: bool
    exclude_ambiguous: bool
    require_each_selected: bool


@dataclass(frozen=True)
class VaultEntry:
    label: str
    username: str
    password: str
    created_at_iso: str  # ISO timestamp string


@dataclass
class StrengthReport:
    score: int  # 0..100
    label: str  # "Weak" / "Medium" / "Strong" / "Very Strong"
    entropy_bits: float
    issues: list[str]
    suggestions: list[str]
