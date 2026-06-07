"""Shareable save codes (pure logic, offline).

Encodes a small JSON-able dict (e.g. a result + seed) into a compact,
copy-pasteable, case-insensitive Base32 string with a version prefix. Fully
offline — nothing is sent anywhere; a code is just text another player can paste
to replay/verify a result. Corrupt input decodes to ``None``.
"""
from __future__ import annotations

import base64
import json
import zlib
from typing import Any

_PREFIX = "NHC1-"


def encode(data: dict[str, Any]) -> str:
    raw = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    comp = zlib.compress(raw, 9)
    body = base64.b32encode(comp).decode("ascii").rstrip("=")
    return _PREFIX + body


def decode(code: str) -> dict[str, Any] | None:
    if not isinstance(code, str):
        return None
    s = code.strip()
    if s.upper().startswith(_PREFIX):
        s = s[len(_PREFIX):]
    s = s.upper()
    try:
        pad = "=" * (-len(s) % 8)
        comp = base64.b32decode(s + pad)
        raw = zlib.decompress(comp)
        out = json.loads(raw)
    except (ValueError, zlib.error, json.JSONDecodeError):
        return None
    return out if isinstance(out, dict) else None
