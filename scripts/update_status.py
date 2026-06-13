"""Garden Grove MMA Tank dashboard writer.

Reads a JSON facts blob from stdin (produced by the /loop's WebSearch step),
diffs against the previous status.json snapshot with 2-tick hysteresis on
breaking events, writes status.json atomically with retry on Windows file
locks, and logs every invocation.

Stdin format (all fields optional; missing fields fall back to previous value):
  {
    "tank_temp_f": 100,
    "tank_crack_observed": true,
    "evacuation_residents": 50000,
    "evacuation_lifted": false,
    "evacuation_expanded": false,
    "evacuation_boundary_text": "S of Ball Rd · N of Trask Ave · ...",
    "evacuation_area_sq_mi": 9,
    "status_headline": "Cooling continues; crack may relieve pressure",
    "injuries": 0,
    "incident_resolved_iso": null,
    "official_statements": [{"agency":"OCFA","time_iso":"...","text":"...","source_url":"..."}],
    "sources_checked": [{"url":"...","title":"...","fetched_iso":"..."}],
    "schools_closed": ["GGUSD", ...]
  }

CLI: python update_status.py < facts.json
     echo '{...}' | python update_status.py
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "public" / "config.json"
STATUS_PATH = PROJECT_DIR / "public" / "status.json"
STATUS_TMP_PATH = PROJECT_DIR / "public" / "status.json.tmp"
BREAKING_LOG_PATH = PROJECT_DIR / "breaking_events.jsonl"
UPDATES_LOG_PATH = PROJECT_DIR / "updates.log"

WRITER_VERSION = 1
SCHEMA_VERSION = 1

# Breaking banner auto-clears after this many minutes if no fresh trigger.
BREAKING_DECAY_MINUTES = 30

# Residents-shift gate (the only noisy field). Only fire breaking if change
# exceeds BOTH thresholds, AND we haven't fired residents-shift in the last
# RESIDENTS_RATE_LIMIT_MIN minutes. Toggles (lifted, expanded, severity bump,
# resolved, new statement) fire immediately — they're authoritative, not noisy.
RESIDENTS_DELTA_PCT = 0.10
RESIDENTS_DELTA_ABS = 1000
RESIDENTS_RATE_LIMIT_MIN = 120

# Severity is derived, not extracted from sources.
SEVERITY_RANK = {"low": 0, "moderate": 1, "high": 2, "critical": 3}

# Data-freshness window (P0-3): stale_after = data_as_of + MAX_AGE. 40 min = 2x the
# 20-min refresh cadence, tolerating one missed run plus cron lag.
MAX_AGE_MINUTES = 40

# Authoritative agency hosts for the P0-1 corroboration gate. A danger DOWNGRADE
# (evacuation lifted / incident resolved) must be backed by >=1 of these. News
# outlets are trusted for reporting but do not alone authorize an "all-clear".
OFFICIAL_HOSTS = frozenset({
    "ocfa.org", "ocsheriff.gov", "ggcity.org", "caloes.ca.gov", "epa.gov", "aqmd.gov",
})

# A tick advances data_as_of_iso (P0-3) only if it carries >=1 non-null value here.
SUBSTANTIVE_KEYS = (
    "status_headline", "tank_temp_f", "tank_crack_observed", "evacuation_residents",
    "evacuation_area_sq_mi", "evacuation_boundary_text", "evacuation_lifted",
    "evacuation_expanded", "injuries", "incident_resolved_iso",
    "official_statements", "sources_checked", "schools_closed",
)


def _url_host(url) -> str | None:
    """Lowercased host of a well-formed http(s) URL, normalized (www. stripped); else None."""
    if not isinstance(url, str):
        return None
    try:
        p = urlparse(url.strip())
    except (ValueError, AttributeError):
        return None
    if p.scheme not in ("http", "https") or not p.hostname:
        return None
    host = p.hostname.lower()
    return host[4:] if host.startswith("www.") else host


def _host_is_official(host) -> bool:
    return bool(host) and any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)


def _parse_iso(val) -> datetime | None:
    """Parse an ISO 8601 string to an aware UTC datetime; None if malformed."""
    if not isinstance(val, str):
        return None
    try:
        dt = datetime.fromisoformat(val.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def validate_dates(facts: dict) -> dict:
    """Date sanity: drop a malformed or future-dated incident_resolved_iso before
    it can drive a false all-clear. resolved_iso is the only timestamp that forces
    a safety state (non-null -> severity "low"), so a parse artifact or hallucinated
    future time must be suppressed. A small clock-skew tolerance keeps a just-now
    resolution from being rejected. Only acts on the key when present."""
    from datetime import timedelta
    SKEW_MINUTES = 5
    val = facts.get("incident_resolved_iso")
    if not val:
        return facts
    dt = _parse_iso(val)
    if dt is None:
        log_line("WARN", f"date-sanity dropped malformed incident_resolved_iso: {val!r}")
        facts["incident_resolved_iso"] = None
    elif dt > datetime.now(timezone.utc) + timedelta(minutes=SKEW_MINUTES):
        log_line("WARN", f"date-sanity dropped future-dated incident_resolved_iso: {val!r}")
        facts["incident_resolved_iso"] = None
    return facts


def validate_provenance(facts: dict) -> dict:
    """P0-2: drop fabricated/malformed provenance before it reaches the snapshot.

    - sources_checked entries whose URL is not a well-formed http(s) URL are dropped.
    - official_statements whose source_url is malformed, OR whose host is not among
      the (cleaned) sources_checked hosts, are dropped — a statement citing a source
      we never actually retrieved this run is treated as fabricated.
    Only acts on keys present in facts; logs every drop.
    """
    if isinstance(facts.get("sources_checked"), list):
        kept = []
        for s in facts["sources_checked"]:
            if _url_host((s or {}).get("url")):
                kept.append(s)
            else:
                log_line("WARN", f"P0-2 dropped sources_checked entry with bad URL: {(s or {}).get('url')!r}")
        facts["sources_checked"] = kept

    ref_hosts = {h for h in (_url_host((s or {}).get("url")) for s in (facts.get("sources_checked") or [])) if h}

    if isinstance(facts.get("official_statements"), list):
        kept = []
        for st in facts["official_statements"]:
            host = _url_host((st or {}).get("source_url"))
            if host and host in ref_hosts:
                kept.append(st)
            else:
                log_line("WARN", f"P0-2 dropped statement citing unretrieved/bad source_url: {(st or {}).get('source_url')!r}")
        facts["official_statements"] = kept
    return facts


def apply_corroboration_gate(facts: dict) -> dict:
    """P0-1: a danger DOWNGRADE must be backed by >=2 retrieved sources incl >=1
    official-agency host, else force the field to its safe default. Asymmetric —
    danger UPGRADES (injuries, expansion, severity bump) are untouched. Operates on
    the already-validated sources_checked (call after validate_provenance)."""
    hosts = [h for h in (_url_host((s or {}).get("url")) for s in (facts.get("sources_checked") or [])) if h]
    corroborated = len(hosts) >= 2 and any(_host_is_official(h) for h in hosts)

    if facts.get("evacuation_lifted") is True and not corroborated:
        log_line("WARN", f"P0-1 unconfirmed all-clear suppressed: evacuation_lifted forced false (N={len(hosts)}, official={any(_host_is_official(h) for h in hosts)})")
        facts["evacuation_lifted"] = False
    if facts.get("incident_resolved_iso") and not corroborated:
        log_line("WARN", f"P0-1 unconfirmed all-clear suppressed: incident_resolved_iso forced null (N={len(hosts)})")
        facts["incident_resolved_iso"] = None
    return facts


def _facts_are_source_backed(facts: dict) -> bool:
    """True if this tick carries >=1 substantive non-null/non-empty fact (P0-3)."""
    if not facts:
        return False
    for k in SUBSTANTIVE_KEYS:
        if k not in facts:
            continue
        v = facts[k]
        if v is None or (isinstance(v, (list, str)) and len(v) == 0):
            continue
        return True
    return False


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_line(level: str, msg: str) -> None:
    line = f"{utcnow_iso()}  {level:5s}  {msg}\n"
    _retry_io(lambda: UPDATES_LOG_PATH.open("a", encoding="utf-8").write(line), tag="updates.log append")


def _retry_io(fn, *, tag: str, attempts: int = 5):
    """Retry a filesystem op on Windows PermissionError / OSError (OneDrive +
    Defender hold file handles briefly). Exponential backoff with jitter."""
    delay = 0.1
    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except (PermissionError, OSError) as e:
            last_exc = e
            if i == attempts - 1:
                break
            jitter = random.uniform(0.8, 1.2)
            time.sleep(delay * jitter)
            delay *= 2
    sys.stderr.write(f"[{tag}] gave up after {attempts} retries: {last_exc}\n")
    raise last_exc


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_previous_status() -> dict | None:
    if not STATUS_PATH.exists():
        return None
    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log_line("WARN", f"could not parse previous status.json: {e}; treating as first run")
        return None


def read_facts_from_stdin() -> dict:
    # Decode stdin as UTF-8 explicitly. The facts blob is emitted as UTF-8 by
    # refresh_local.py / gather_facts.py; a plain sys.stdin.read() would decode
    # with the process locale (cp1252 on Windows), turning an em-dash into the
    # `â€"` mojibake the dashboard then has to repair. Reading bytes keeps it
    # correct regardless of locale.
    raw = sys.stdin.buffer.read().decode("utf-8").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        log_line("WARN", f"stdin facts JSON parse failed: {e}; treating as empty (will keep prev values)")
        return {}


def derive_severity(facts: dict) -> str:
    """First-match-wins rules from SPEC."""
    if facts.get("incident_resolved_iso"):
        return "low"
    if facts.get("tank_failed") or facts.get("explosion_confirmed") or (facts.get("injuries", 0) or 0) > 0:
        return "critical"
    if (facts.get("evacuation_residents") or 0) > 1000 and not facts.get("evacuation_lifted"):
        return "high"
    if (facts.get("evacuation_residents") or 0) > 0 and not facts.get("evacuation_lifted"):
        return "moderate"
    return "low"


def hash_statement(s: dict) -> str:
    h = hashlib.sha256()
    h.update((s.get("agency", "") + "||" + s.get("text", "")[:200]).encode("utf-8"))
    return h.hexdigest()[:16]


def detect_breaking(prev: dict | None, new_incident: dict, new_evac: dict, new_statements: list, new_injuries: int) -> tuple[bool, str | None, str | None]:
    """Return (should_fire, reason, level).

    level: "urgent"  = act-now changes (evac expanded/lifted/reinstated, severity
                       bumped, first injuries, incident resolved). Red banner + beep.
           "info"    = informational changes (new statement, residents-count shift).
                       Amber banner, no beep.
           None      = no fire.
    """
    if prev is None:
        return False, None, None  # first run is never breaking

    prev_evac = prev.get("evacuation", {}) or {}
    prev_incident = prev.get("incident", {}) or {}

    # --- URGENT (toggles + counts that mean act-now) ---

    if new_incident.get("resolved_iso") and not prev_incident.get("resolved_iso"):
        return True, "INCIDENT RESOLVED — evacuation lifted", "urgent"

    new_sev = SEVERITY_RANK.get(new_incident.get("severity", "low"), 0)
    prev_sev = SEVERITY_RANK.get(prev_incident.get("severity", "low"), 0)
    if new_sev > prev_sev:
        return True, f"Severity bumped: {prev_incident.get('severity')} -> {new_incident.get('severity')}", "urgent"

    if new_evac.get("lifted") and not prev_evac.get("lifted"):
        return True, "Evacuation order LIFTED", "urgent"
    if not new_evac.get("lifted") and prev_evac.get("lifted"):
        return True, "Evacuation order REINSTATED", "urgent"
    if new_evac.get("expanded_since_yesterday") and not prev_evac.get("expanded_since_yesterday"):
        return True, "Evacuation zone EXPANDED", "urgent"

    prev_injuries = (prev.get("_meta", {}).get("injuries") or 0)
    if new_injuries > 0 and prev_injuries == 0:
        return True, f"First reported injuries: {new_injuries}", "urgent"

    # --- INFO (informational updates) ---

    prev_stmt_hashes = set(prev.get("_meta", {}).get("statement_hashes") or [])
    new_stmt_hashes = {hash_statement(s) for s in new_statements}
    novel = new_stmt_hashes - prev_stmt_hashes
    if novel and len(prev_stmt_hashes) > 0:
        return True, f"{len(novel)} new official statement(s)", "info"

    prev_residents = prev_evac.get("residents", 0) or 0
    new_residents = new_evac.get("residents", 0) or 0
    if prev_residents > 0:
        delta_pct = abs(new_residents - prev_residents) / prev_residents
        delta_abs = abs(new_residents - prev_residents)
        if delta_pct > RESIDENTS_DELTA_PCT and delta_abs > RESIDENTS_DELTA_ABS:
            last_fired = prev.get("_meta", {}).get("last_residents_shift_iso")
            if last_fired:
                try:
                    last_dt = datetime.strptime(last_fired, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    age_min = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
                    if age_min < RESIDENTS_RATE_LIMIT_MIN:
                        return False, None, None
                except ValueError:
                    pass
            return True, f"Evacuation residents shifted: {prev_residents:,} -> {new_residents:,} ({'+' if new_residents > prev_residents else '-'}{delta_abs:,})", "info"

    return False, None, None


def append_breaking_event(entry: dict) -> None:
    line = json.dumps(entry, separators=(",", ":")) + "\n"
    _retry_io(lambda: BREAKING_LOG_PATH.open("a", encoding="utf-8").write(line), tag="breaking_events.jsonl append")


def atomic_write_status(snapshot: dict) -> None:
    payload = json.dumps(snapshot, indent=2)
    _retry_io(lambda: STATUS_TMP_PATH.write_text(payload, encoding="utf-8"), tag="status.json.tmp write")
    _retry_io(lambda: os.replace(STATUS_TMP_PATH, STATUS_PATH), tag="status.json atomic rename")


def fetch_air_quality(config: dict) -> dict | None:
    """Fetch current AQI from EPA AirNow. Returns None if key unset or fetch fails."""
    api_key = os.environ.get("AIRNOW_API_KEY")
    if not api_key:
        return None
    fac = (config.get("map") or {}).get("facility") or {}
    lat, lon = fac.get("lat"), fac.get("lon")
    if not lat or not lon:
        return None
    url = (
        f"https://www.airnowapi.org/aq/observation/latLong/current/"
        f"?format=application/json&latitude={lat}&longitude={lon}"
        f"&distance=25&API_KEY={api_key}"
    )
    try:
        req = Request(url, headers={"User-Agent": "GGTankWatch/1.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if not data:
            return None
        # AirNow returns a list of observations; pick the PM2.5 or first entry
        obs = next((d for d in data if d.get("ParameterName") == "PM2.5"), data[0])
        return {
            "aqi": obs.get("AQI"),
            "category": obs.get("Category", {}).get("Name", "Unknown"),
            "parameter": obs.get("ParameterName", "PM2.5"),
            "source": "EPA AirNow",
            "fetched_iso": utcnow_iso(),
        }
    except (URLError, json.JSONDecodeError, KeyError, StopIteration):
        log_line("WARN", "AirNow fetch failed")
        return None


def build_snapshot(prev: dict | None, facts: dict, config: dict) -> dict:
    """Merge prev + new facts into a full snapshot. Missing facts inherit from prev."""
    prev_actual = prev  # preserve None-ness for breaking detector
    prev = prev or {}
    prev_incident = prev.get("incident", {}) or {}
    prev_tank = prev.get("tank", {}) or {}
    prev_evac = prev.get("evacuation", {}) or {}
    prev_you = prev.get("you", {}) or {}

    incident_cfg = config.get("incident", {})

    # Build sub-objects with fall-through to prev
    # Severity is derived from facts, but only re-derive when this tick actually
    # provides the relevant fields. A partial facts dict (e.g., only `videos`)
    # must NOT silently downgrade severity to "low" — it should keep prev.
    severity_relevant_keys = (
        "evacuation_residents", "evacuation_lifted", "incident_resolved_iso",
        "injuries", "tank_failed", "explosion_confirmed"
    )
    if facts and any(k in facts for k in severity_relevant_keys):
        derived_severity = derive_severity(facts)
    else:
        derived_severity = prev_incident.get("severity", "low")

    incident = {
        "name": incident_cfg.get("name") or prev_incident.get("name") or "Garden Grove MMA Tank Leak",
        "facility": incident_cfg.get("facility") or prev_incident.get("facility"),
        "started_iso": incident_cfg.get("started_iso") or prev_incident.get("started_iso"),
        "status_headline": facts.get("status_headline") or prev_incident.get("status_headline") or "Status unknown",
        "severity": derived_severity,
        "resolved_iso": facts.get("incident_resolved_iso") if "incident_resolved_iso" in facts else prev_incident.get("resolved_iso"),
    }
    tank = {
        "temp_f": facts.get("tank_temp_f") if "tank_temp_f" in facts else prev_tank.get("temp_f"),
        "crack_observed": facts.get("tank_crack_observed") if "tank_crack_observed" in facts else prev_tank.get("crack_observed"),
    }
    evacuation = {
        "residents": facts.get("evacuation_residents") if "evacuation_residents" in facts else prev_evac.get("residents"),
        "area_sq_mi": facts.get("evacuation_area_sq_mi") if "evacuation_area_sq_mi" in facts else prev_evac.get("area_sq_mi"),
        "boundary_text": facts.get("evacuation_boundary_text") if "evacuation_boundary_text" in facts else prev_evac.get("boundary_text"),
        "lifted": facts.get("evacuation_lifted") if "evacuation_lifted" in facts else prev_evac.get("lifted", False),
        "expanded_since_yesterday": facts.get("evacuation_expanded") if "evacuation_expanded" in facts else prev_evac.get("expanded_since_yesterday", False),
    }
    you = {
        "zone_status": config.get("zone_status") or prev_you.get("zone_status") or "outside_downwind",
        "address_checker_url": incident_cfg.get("address_checker_url") or prev_you.get("address_checker_url"),
    }

    # Validate residents sanity (catch bad parses)
    new_r = evacuation.get("residents", 0) or 0
    prev_r = prev_evac.get("residents", 0) or 0
    if prev_r > 1000 and new_r > 0 and new_r < prev_r * 0.5 and not evacuation.get("lifted"):
        log_line("WARN", f"suspicious residents drop {prev_r:,} → {new_r:,} without lifted=true; keeping prev value")
        evacuation["residents"] = prev_r

    statements = facts.get("official_statements") or prev.get("official_statements") or []
    sources = facts.get("sources_checked") or prev.get("sources_checked") or []
    schools = facts.get("schools_closed") or prev.get("schools_closed") or []
    injuries = facts.get("injuries", 0) or 0

    # Videos: list of {outlet, title, url, thumbnail_url?, published_iso?, youtube_id?}
    # - Dedupe by URL (keep first occurrence) — live-blog URLs were being
    #   duplicated across "stories" that all point at the same page.
    # - is_video is re-derived from URL pattern; any incoming flag is ignored
    #   so display classification stays consistent with the actual destination.
    # - If youtube_id is set and thumbnail_url is missing, derive YouTube hqdefault.
    raw_videos = facts.get("videos") if "videos" in facts else prev.get("videos") or []
    videos = []
    seen_urls = set()
    for v in raw_videos or []:
        v = dict(v)
        url = (v.get("url") or "").strip()
        if url:
            if url in seen_urls:
                continue
            seen_urls.add(url)
        if v.get("youtube_id") or "youtube.com/" in url or "youtu.be/" in url or "/video/" in url:
            v["is_video"] = True
        else:
            v["is_video"] = False
        if not v.get("thumbnail_url") and v.get("youtube_id"):
            v["thumbnail_url"] = f"https://img.youtube.com/vi/{v['youtube_id']}/hqdefault.jpg"
        videos.append(v)

    # Detect breaking — pass actual prev (preserving None-ness) so first-run guard works.
    fires, reason, level = detect_breaking(prev_actual, incident, evacuation, statements, injuries)

    now_iso = utcnow_iso()
    prev_breaking = (prev_actual or {}).get("breaking", False)
    prev_breaking_since = (prev_actual or {}).get("breaking_since_iso")
    prev_breaking_reason = (prev_actual or {}).get("breaking_reason")
    prev_breaking_level = (prev_actual or {}).get("breaking_level")

    # Decay: if currently breaking and no fresh trigger and >30 min since last, clear.
    if prev_breaking and prev_breaking_since and not fires:
        try:
            since_dt = datetime.strptime(prev_breaking_since, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            age_min = (datetime.now(timezone.utc) - since_dt).total_seconds() / 60
            if age_min > BREAKING_DECAY_MINUTES:
                breaking, breaking_reason, breaking_since, breaking_level = False, None, None, None
            else:
                breaking, breaking_reason, breaking_since, breaking_level = True, prev_breaking_reason, prev_breaking_since, prev_breaking_level
        except ValueError:
            breaking, breaking_reason, breaking_since, breaking_level = prev_breaking, prev_breaking_reason, prev_breaking_since, prev_breaking_level
    elif fires:
        breaking, breaking_reason, breaking_since, breaking_level = True, reason, now_iso, level
    else:
        breaking, breaking_reason, breaking_since, breaking_level = prev_breaking, prev_breaking_reason, prev_breaking_since, prev_breaking_level

    # [#3 follow-up 2026-05-30] Post-resolution invariant: a resolved incident
    # carries NO live "breaking" state on any tick AFTER the resolution
    # transition. The transition tick itself (prev not resolved -> now resolved)
    # still fires urgent above (see detect_breaking + test_t5); this only clears
    # on subsequent ticks, so a routine recovery statement can't re-arm the
    # "UPDATE - N new official statement" banner and status.json stays honest.
    if incident.get("resolved_iso") and prev_incident.get("resolved_iso") and breaking:
        breaking, breaking_reason, breaking_since, breaking_level = False, None, None, None

    # Compute timestamps
    from datetime import timedelta
    now_dt = datetime.now(timezone.utc)
    interval_min = config.get("writer_interval_minutes", 30)
    next_check = (now_dt + timedelta(minutes=interval_min)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # P0-3: data_as_of_iso advances ONLY when this tick learned a source-backed fact;
    # otherwise it inherits prev. stale_after keys off data-age (not write-age), so a
    # writer that runs but learns nothing can no longer look fresh.
    prev_data_as_of = (prev_actual or {}).get("data_as_of_iso")
    if _facts_are_source_backed(facts):
        data_as_of = now_iso
    else:
        data_as_of = prev_data_as_of or now_iso
    try:
        data_as_of_dt = datetime.strptime(data_as_of, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        data_as_of, data_as_of_dt = now_iso, now_dt
    stale_after = (data_as_of_dt + timedelta(minutes=MAX_AGE_MINUTES)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # AirNow removed 2026-05-30 (false reassurance: AQI measures particulates/
    # ozone, not the MMA vapor from this leak). Do not fetch or carry forward;
    # air_quality stays null. fetch_air_quality() is retained but unused.
    air_quality = None

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "writer_version": WRITER_VERSION,
        "last_updated_iso": now_iso,
        "data_as_of_iso": data_as_of,
        "next_check_at_iso": next_check,
        "stale_after_iso": stale_after,
        "incident": incident,
        "tank": tank,
        "evacuation": evacuation,
        "you": you,
        "official_statements": statements,
        "sources_checked": sources,
        "schools_closed": schools,
        "videos": videos,
        "air_quality": air_quality,
        "breaking": breaking,
        "breaking_reason": breaking_reason,
        "breaking_since_iso": breaking_since,
        "breaking_level": breaking_level,
        "_meta": {
            "injuries": injuries,
            "statement_hashes": [hash_statement(s) for s in statements],
            "last_residents_shift_iso": (
                now_iso if (fires and reason and "residents shifted" in reason)
                else (prev_actual or {}).get("_meta", {}).get("last_residents_shift_iso")
            ),
        },
    }
    return snapshot, fires, reason


def main() -> int:
    log_line("INFO", "writer start")
    config = load_config()
    prev = load_previous_status()
    facts = read_facts_from_stdin()

    # Safety gates (order matters): strip fabricated provenance first, then judge
    # whether any surviving sources corroborate a danger downgrade.
    facts = validate_provenance(facts)   # P0-2
    facts = validate_dates(facts)        # date sanity (resolved_iso)
    facts = apply_corroboration_gate(facts)  # P0-1

    if not facts:
        log_line("WARN", "stdin facts empty; producing snapshot from prev only (no fact updates this tick)")

    snapshot, fires, reason = build_snapshot(prev, facts, config)

    breaking_just_flipped = snapshot["breaking"] and not (prev or {}).get("breaking")
    breaking_reason_changed = (
        snapshot["breaking"]
        and (prev or {}).get("breaking")
        and snapshot.get("breaking_reason") != (prev or {}).get("breaking_reason")
    )

    atomic_write_status(snapshot)
    log_line("INFO", f"status.json written; breaking={snapshot['breaking']} severity={snapshot['incident']['severity']}")

    if breaking_just_flipped or breaking_reason_changed:
        msg = snapshot.get("breaking_reason") or "(no reason)"
        append_breaking_event({
            "fired_iso": utcnow_iso(),
            "reason": msg,
            "snapshot_at": snapshot["last_updated_iso"],
        })
        log_line("INFO", f"breaking fired: {msg}")

    log_line("INFO", "writer exit OK")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Best-effort: log the crash. Without ntfy the dashboard's staleness
        # banner (fires when last_updated_iso > stale_after_iso) is now the
        # only writer-down indicator the user will notice.
        tb = traceback.format_exc()
        try:
            log_line("ERROR", f"writer crashed: {e}\n{tb}")
        except Exception:
            pass
        sys.exit(1)
