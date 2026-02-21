from __future__ import annotations
import secrets
from typing import List

from .models import PasswordPolicy
from .utils import AMBIGUOUS, clamp_int


LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/<>~"


class PolicyError(ValueError):
    pass


def _build_charset(policy: PasswordPolicy) -> str:
    chars = ""
    if policy.use_lower:
        chars += LOWER
    if policy.use_upper:
        chars += UPPER
    if policy.use_digits:
        chars += DIGITS
    if policy.use_symbols:
        chars += SYMBOLS

    if policy.exclude_ambiguous:
        chars = "".join(c for c in chars if c not in AMBIGUOUS)

    return chars


def generate_password(policy: PasswordPolicy) -> str:
    length = clamp_int(policy.length, 6, 64)
    charset = _build_charset(policy)
    if not charset:
        raise PolicyError("Select at least one character type.")

    required_pools: List[str] = []
    if policy.require_each_selected:
        if policy.use_lower:
            required_pools.append("".join(c for c in LOWER if (not policy.exclude_ambiguous) or (c not in AMBIGUOUS)))
        if policy.use_upper:
            required_pools.append("".join(c for c in UPPER if (not policy.exclude_ambiguous) or (c not in AMBIGUOUS)))
        if policy.use_digits:
            required_pools.append("".join(c for c in DIGITS if (not policy.exclude_ambiguous) or (c not in AMBIGUOUS)))
        if policy.use_symbols:
            required_pools.append("".join(c for c in SYMBOLS if (not policy.exclude_ambiguous) or (c not in AMBIGUOUS)))

        if len(required_pools) > length:
            raise PolicyError("Length is too small for the required character groups.")

    # Start with required chars
    pw_chars: List[str] = []
    for pool in required_pools:
        if not pool:
            continue
        pw_chars.append(secrets.choice(pool))

    # Fill the remaining length with secure random choices
    while len(pw_chars) < length:
        pw_chars.append(secrets.choice(charset))

    # Shuffle using secure random
    secrets.SystemRandom().shuffle(pw_chars)
    return "".join(pw_chars)
