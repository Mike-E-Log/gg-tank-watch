"""UTF-8 integrity tests for scripts/update_status.py (data-quality: mojibake root cause).

The facts blob reaches the writer over stdin as UTF-8 bytes (refresh_local.py /
gather_facts.py both emit UTF-8). On a non-UTF-8 locale (Windows cp1252 is the
real case), a plain `sys.stdin.read()` decodes those bytes with the wrong codec
and an em-dash (U+2014, UTF-8 `E2 80 94`) becomes the `â€"` mojibake the
dashboard then has to repair client-side. The fix reads stdin as bytes and
decodes UTF-8 explicitly, so the writer is correct regardless of process locale.

These tests force the non-UTF-8-locale condition deterministically (a cp1252
text stream over UTF-8 bytes) so they fail on any platform if the writer ever
regresses to locale-dependent decoding.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

CATEGORY = "behavioral"

WRITER = Path(__file__).resolve().parent.parent / "scripts" / "update_status.py"


def _load_writer():
    spec = importlib.util.spec_from_file_location("update_status_under_test", WRITER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_facts_with_locale(facts: dict, locale_encoding: str) -> dict:
    """Feed `facts` to read_facts_from_stdin() as UTF-8 bytes behind a text stream
    that *thinks* it is `locale_encoding` — mimics a non-UTF-8 process locale."""
    mod = _load_writer()
    utf8_bytes = json.dumps(facts, ensure_ascii=False).encode("utf-8")
    fake_stdin = io.TextIOWrapper(io.BytesIO(utf8_bytes), encoding=locale_encoding)
    saved = sys.stdin
    sys.stdin = fake_stdin
    try:
        return mod.read_facts_from_stdin()
    finally:
        sys.stdin = saved


def test_em_dash_survives_non_utf8_locale():
    """An em-dash in UTF-8 stdin must not become mojibake under a cp1252 locale."""
    headline = "Cooling continues — crack may relieve pressure"
    got = _read_facts_with_locale({"status_headline": headline}, "cp1252")
    return {
        "passed": got.get("status_headline") == headline,
        "details": f"expected {headline!r}, got {got.get('status_headline')!r}",
    }


def test_degree_sign_survives_non_utf8_locale():
    """A degree sign (used in tank temps text) survives a cp1252 locale."""
    headline = "Tank holding near 100°F"
    got = _read_facts_with_locale({"status_headline": headline}, "cp1252")
    return {
        "passed": got.get("status_headline") == headline,
        "details": f"expected {headline!r}, got {got.get('status_headline')!r}",
    }
