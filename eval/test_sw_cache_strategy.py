"""Guard (T4, archive pivot): sw.js serves the frozen status.json cache-first, and the
cache name is bumped so returning users get the archived shell."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
SW = REPO_ROOT / "public" / "sw.js"


def test_cache_bumped_v92():
    t = SW.read_text(encoding="utf-8")
    return {"passed": 'CACHE_NAME = "gg-tank-v92"' in t,
            "details": f"v92 present={'gg-tank-v92' in t}"}


def test_status_json_cache_first():
    t = SW.read_text(encoding="utf-8")
    # frozen snapshot => cache-first; the old network-first marker must be gone
    no_network_first = "Network-first for status.json" not in t
    # Fable 5 audit D4 (2026-07-21): the dashboard fetches its JSON with ?t=Date.now()
    # cache-busters, but caches.match() is query-sensitive by default, so the precached
    # bare paths could NEVER be hit and "cache-first" silently never happened. Every
    # caches.match(event.request) must ignore the query string.
    query_sensitive = ("caches.match(event.request)." in t
                       or "caches.match(event.request);" in t
                       or "caches.match(event.request))" in t)
    ignore_search = "ignoreSearch" in t
    passed = no_network_first and ignore_search and not query_sensitive
    return {"passed": passed,
            "details": (f"network-first marker removed={no_network_first} "
                        f"ignoreSearch={ignore_search} query_sensitive_match={query_sensitive}")}


def test_frozen_status_offline_robust():
    """A frozen snapshot must survive offline: status.json is precached in
    STATIC_ASSETS and the cache-first handler has a network-failure fallback."""
    t = SW.read_text(encoding="utf-8")
    precached = '"/status.json"' in t
    fallback = ".catch(function () {" in t
    return {"passed": precached and fallback,
            "details": f"status.json precached={precached}, offline fallback={fallback}"}
