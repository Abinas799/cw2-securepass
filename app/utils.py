from __future__ import annotations
import datetime as dt
import re
from typing import Iterable


AMBIGUOUS = set("O0Il1|`'\"")


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat(sep=" ")


def clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def safe_label(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
