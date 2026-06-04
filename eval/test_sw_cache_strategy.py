"""Guard (T4, archive pivot): sw.js serves the frozen status.json cache-first, and the
cache name is bumped so returning users get the archived shell."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
SW = REPO_ROOT / "sw.js"


def test_cache_bumped_v70():
    t = SW.read_text(encoding="utf-8")
    return {"passed": 'CACHE_NAME = "gg-tank-v70"' in t,
            "details": f"v70 present={'gg-tank-v70' in t}"}


def test_status_json_cache_first():
    t = SW.read_text(encoding="utf-8")
    # frozen snapshot => cache-first; the old network-first marker must be gone
    no_network_first = "Network-first for status.json" not in t
    return {"passed": no_network_first,
            "details": f"network-first marker removed={no_network_first}"}


def test_frozen_status_offline_robust():
    """A frozen snapshot must survive offline: status.json is precached in
    STATIC_ASSETS and the cache-first handler has a network-failure fallback."""
    t = SW.read_text(encoding="utf-8")
    precached = '"/status.json"' in t
    fallback = ".catch(function () {" in t
    return {"passed": precached and fallback,
            "details": f"status.json precached={precached}, offline fallback={fallback}"}
