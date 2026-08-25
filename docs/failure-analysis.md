# Failure analysis: red-team report

How the automated tests catch each failure mode before it reaches users.

## Methodology

[`docs/DATA_QUALITY.md`](https://github.com/Mike-E-Log/gg-tank-watch/blob/main/docs/DATA_QUALITY.md) in the dashboard repo maps 12 failure modes (F1–F12) ranked by likelihood and harm. This document traces each mode to the specific test(s) that would catch it, and identifies which modes remain unguarded.

## Failure mode → test mapping

### Catastrophic (false safety signal to evacuees)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F1** | Fabricated all-clear (model hallucinates `evacuation_lifted: true` or `incident_resolved_iso`) | `test_lifted_requires_corroboration`, `test_resolved_requires_two_sources` | **Guarded.** The corroboration gate (P0-1) forces a safe default when fewer than 2 sources are present, or when no official source is among them. |
| **F12** | Prompt injection via scraped page (malicious page tells model "evacuation is lifted") | `test_lifted_requires_corroboration` (same gate) | **Partially guarded.** The corroboration gate blocks the *effect* (a single-source all-clear), but doesn't detect the *cause* (injection). A coordinated injection across 2+ sources including a spoofed official domain could bypass the gate. Residual risk accepted: the attacker would need to control ≥2 indexed news sources AND spoof an official hostname. |

### High harm (fabricated information, invisible staleness)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F2** | Fabricated source URL or quote | `test_fabricated_source_url_not_in_snapshot`, `test_statement_without_source_url_rejected`, `test_sources_checked_all_wellformed` | **Guarded.** The provenance check (P0-2) drops any statement whose `source_url` was not actually retrieved this run. |
| **F3** | Hallucinated numeric (temp, residents, injuries) | `test_garbage_input_keeps_prev_values`, `test_partial_facts_dont_downgrade_severity`, `test_residents_shift_fires_info` | **Partially guarded.** Writer holds previous value on a >50% residents drop without `lifted`. But a plausible-but-wrong number (e.g., 48,000 instead of 50,000) passes. No numeric sanity beyond the 50% drop gate. |
| **F4** | Stale-but-fresh-stamped (empty facts, fresh timestamp) | `test_empty_facts_do_not_advance_data_as_of`, `test_all_null_facts_treated_as_no_data`, `test_stale_after_is_data_as_of_plus_maxage` | **Guarded.** The freshness check (P0-3) tracks how old the data is separately from when the page was last written, so a stale fact cannot be stamped with a fresh time. |
| **F11** | Fabricated/garbled date (future or pre-incident timestamp) | `test_future_resolved_iso_suppressed`, `test_malformed_resolved_iso_suppressed`, `test_valid_resolved_iso_honored` | **Guarded.** The timestamp sanity check (P1-1) clears any date that is set in the future or cannot be parsed. |

### Medium harm (degraded quality, lost provenance)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F5** | Severity miscompute from partial facts | `test_partial_facts_dont_downgrade_severity` | **Guarded.** Fixed + regression test. |
| **F6** | Web search returns nothing (all-null facts) | `test_all_null_facts_treated_as_no_data`, `test_graceful_failure_no_api_key` | **Guarded.** Writer carries previous values; P0-3 prevents fresh-stamping. |
| **F7** | No provenance (model omits `sources_checked`) | `test_sources_checked_all_wellformed` (shape), `test_every_statement_has_source_and_time` (data contract) | **Partially guarded.** Tests confirm the required fields exist and are well-formed, but an empty `sources_checked: []` passes silently. |
| **F8** | Schema drift (gatherer and writer disagree on field names) | `test_status_json_required_fields`, `test_config_json_required_fields` | **Partially guarded.** Schema tests catch missing fields in the final output, but do not verify that the gathering step and the writing step agree on field names when they hand data off to each other. |

### Low harm (operational, not safety-critical)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F9** | Cron silently stops | None | **Unguarded.** No external heartbeat monitor exists to alert when the scheduled job stops. The staleness banner (P0-3, the freshness check) is the only in-app signal. If P0-3 has a bug, a stopped cron is invisible. |
| **F10** | Commit/deploy failure | None | **Unguarded.** Push failure is visible only in GitHub Actions. No external alerting. |

## Coverage summary

> F-codes (F1 to F12) are the failure modes named and described in the mapping tables above.

| Category | Modes | Guarded | Partially guarded | Unguarded |
|----------|-------|---------|-------------------|-----------|
| Catastrophic | F1, F12 | F1 | F12 | none |
| High harm | F2, F3, F4, F11 | F2, F4, F11 | F3 | none |
| Medium harm | F5, F6, F7, F8 | F5, F6 | F7, F8 | none |
| Low harm | F9, F10 | none | none | F9, F10 |

**6 of 12 failure modes are fully guarded by automated tests. 4 are partially guarded: the test catches the harmful outcome but not every path that could lead to it. 2 operational modes have no automated coverage, so the staleness banner is the manual fallback.**

## What the automated tests cannot catch

1. **Plausible-but-wrong numerics (F3 residual).** If the model says 48,000 evacuees when the real number is 50,000, no automated test flags it. The 50% drop gate catches gross errors, not subtle ones.

2. **Coordinated prompt injection (F12 residual).** If an attacker controls ≥2 indexed sources and one spoofs an official domain, the corroboration gate passes. This requires a sophisticated, targeted attack: low probability, but the architecture doesn't structurally prevent it.

3. **Silent cron death (F9).** The scheduled job has no external heartbeat monitor. If the scheduled job stops and the staleness banner also has a bug, users see no signal. Both would have to fail at the same time. The staleness banner is itself tested by the freshness check (P0-3).

4. **Subtle semantic drift.** The model might gradually shift tone, becoming more alarming or more reassuring, without crossing any pass/fail line a test can check. The human review step is the check here, not the automated tests.

## Design lesson

The automated tests are strongest where a failure mode is all-or-nothing and dangerous: an all-clear vs. not, fabricated vs. real, stale vs. fresh. They are weakest where the failure mode is a matter of degree and easy to miss: slightly wrong numbers, slow tone drift, a sophisticated injection. That matches the priority. The all-or-nothing failures are the ones that could kill someone. The matter-of-degree ones lower quality but do not create a false safety signal.
