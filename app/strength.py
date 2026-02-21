from __future__ import annotations
import math
import re
from typing import Tuple, List

from .models import StrengthReport


SEQ_PATTERNS = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
]


KEYBOARD_SEQS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]


def _charset_size(pw: str) -> int:
    has_lower = any("a" <= c <= "z" for c in pw)
    has_upper = any("A" <= c <= "Z" for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_symbol = any(not c.isalnum() for c in pw)

    size = 0
    if has_lower:
        size += 26
    if has_upper:
        size += 26
    if has_digit:
        size += 10
    if has_symbol:
        size += 32
    return max(size, 1)


def estimate_entropy_bits(pw: str) -> float:
    size = _charset_size(pw)
    return len(pw) * math.log2(size)


def _has_repetition(pw: str) -> bool:
    return bool(re.search(r"(.)\1\1", pw))  # 3 repeated


def _has_sequence(pw: str) -> bool:
    for base in SEQ_PATTERNS:
        for i in range(len(base) - 3):
            seq = base[i:i+4]
            if seq in pw or seq[::-1] in pw:
                return True
    return False


def _has_keyboard_pattern(pw: str) -> bool:
    low = pw.lower()
    for row in KEYBOARD_SEQS:
        for i in range(len(row) - 3):
            s = row[i:i+4]
            if s in low or s[::-1] in low:
                return True
    return False


def score_password(pw: str, common_hit: bool = False) -> StrengthReport:
    issues: List[str] = []
    suggestions: List[str] = []

    if len(pw) < 8:
        issues.append("Password length is too short.")
        suggestions.append("Use at least 12 characters.")
    elif len(pw) < 12:
        suggestions.append("Increase length to 12+ for better security.")

    entropy = estimate_entropy_bits(pw)

    score = 0

    # Base score from entropy (cap)
    score += int(min(entropy, 80))

    # Penalties for weaknesses
    if common_hit:
        issues.append("Password appears in common-password list.")
        score -= 40
        suggestions.append("Avoid common passwords or predictable phrases.")

    if _has_repetition(pw):
        issues.append("Repeated character pattern detected.")
        score -= 10
        suggestions.append("Avoid repeating characters (e.g., aaa).")

    if _has_sequence(pw):
        issues.append("Sequential pattern detected (e.g., 1234, abcd).")
        score -= 12
        suggestions.append("Avoid sequences like 1234 or abcd.")

    if _has_keyboard_pattern(pw):
        issues.append("Keyboard pattern detected (e.g., qwert).")
        score -= 12
        suggestions.append("Avoid keyboard patterns like qwert.")

    # Bonus for variety
    variety = 0
    variety += 1 if any("a" <= c <= "z" for c in pw) else 0
    variety += 1 if any("A" <= c <= "Z" for c in pw) else 0
    variety += 1 if any(c.isdigit() for c in pw) else 0
    variety += 1 if any(not c.isalnum() for c in pw) else 0
    score += (variety - 1) * 4  # up to +12

    score = max(0, min(100, score))

    if score < 40:
        label = "Weak"
    elif score < 60:
        label = "Medium"
    elif score < 80:
        label = "Strong"
    else:
        label = "Very Strong"

    if not issues and score >= 60:
        suggestions.append("Good password. Store it securely and avoid reuse.")

    return StrengthReport(score=score, label=label, entropy_bits=round(entropy, 2), issues=issues, suggestions=suggestions)
