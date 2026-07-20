# Failure Analysis: Red Team Report

How the eval harness catches each failure mode before it reaches users.

## Methodology

`docs/DATA_QUALITY.md` maps 12 failure modes (F1-F12) ranked by likelihood and harm. This document traces each mode to the specific test(s) that would catch it, and identifies which modes remain unguarded.

## Failure mode → test mapping

### Catastrophic (false safety signal to evacuees)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F1** | Fabricated all-clear (model hallucinates `evacuation_lifted: true` or `incident_resolved_iso`) | `test_lifted_requires_corroboration`, `test_resolved_requires_two_sources` | **Guarded.** P0-1 corroboration gate forces safe default when source count < 2 or no official source present. |
| **F12** | Prompt injection via scraped page (prompt injection: an attack that smuggles hidden commands into text the model reads, such as a malicious page that tells the model "evacuation is lifted") | `test_lifted_requires_corroboration` (same gate) | **Partially guarded.** The corroboration gate blocks the *effect* (a single-source all-clear), but doesn't detect the *cause* (injection). A coordinated injection across 2+ sources including a spoofed official domain could bypass the gate. Residual risk accepted: the attacker would need to control ≥2 indexed news sources AND spoof an official hostname. |

### High harm (fabricated information, invisible staleness)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F2** | Fabricated source URL or quote | `test_fabricated_source_url_not_in_snapshot`, `test_statement_without_source_url_rejected`, `test_sources_checked_all_wellformed` | **Guarded.** P0-2 (the provenance gate) drops any statement whose `source_url` wasn't actually retrieved this run. |
| **F3** | Hallucinated numeric (temp, residents, injuries) | `test_garbage_input_keeps_prev_values`, `test_partial_facts_dont_downgrade_severity`, `test_residents_shift_fires_info` | **Partially guarded.** Writer holds previous value on a >50% residents drop without `lifted`. But a plausible-but-wrong number (e.g., 48,000 instead of 50,000) passes. No numeric sanity beyond the 50% drop gate. |
| **F4** | Stale-but-fresh-stamped (empty facts, fresh timestamp) | `test_empty_facts_do_not_advance_data_as_of`, `test_all_null_facts_treated_as_no_data`, `test_stale_after_is_data_as_of_plus_maxage` | **Guarded.** P0-3 (the staleness gate) separates data age from write age. |
| **F11** | Fabricated/garbled date (future or pre-incident timestamp) | `test_future_resolved_iso_suppressed`, `test_malformed_resolved_iso_suppressed`, `test_valid_resolved_iso_honored` | **Guarded.** P1-1 (the timestamp validation gate) nulls future-dated and malformed timestamps. |

### Medium harm (degraded quality, lost provenance)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F5** | Severity miscompute from partial facts | `test_partial_facts_dont_downgrade_severity` | **Guarded.** Fixed + regression test. |
| **F6** | Web search returns nothing (all-null facts) | `test_all_null_facts_treated_as_no_data`, `test_graceful_failure_no_api_key` | **Guarded.** Writer carries previous values; P0-3 prevents fresh-stamping. |
| **F7** | No provenance (model omits `sources_checked`) | `test_sources_checked_all_wellformed` (shape), `test_every_statement_has_source_and_time` (data contract) | **Partially guarded.** Tests verify shape and presence, but an empty `sources_checked: []` passes silently. |
| **F8** | Schema mismatch: the data-collection step and the data-writing step use different names for the same fields (schema drift) | `test_status_json_required_fields`, `test_config_json_required_fields` | **Partially guarded.** Schema tests catch missing fields in the output, but don't verify that the data-collection step and the data-writing step agree on the exact format they exchange. |

### Low harm (operational, not safety-critical)

| Mode | Description | Tests that catch it | Verdict |
|------|-------------|--------------------|---------| 
| **F9** | Scheduled update job silently stops (cron: the automated task that runs the update pipeline on a timer) | None | **Unguarded.** No dead-man's switch. Staleness banner (P0-3, the staleness gate) is the only in-app signal. If P0-3 has a bug, a stopped cron is invisible. |
| **F10** | Commit/deploy failure | None | **Unguarded.** Push failure is visible only in GitHub Actions. No external alerting. |

## Coverage summary

| Category | Modes | Guarded | Partially guarded | Unguarded |
|----------|-------|---------|-------------------|-----------|
| Catastrophic | F1, F12 | F1 | F12 | none |
| High harm | F2, F3, F4, F11 | F2, F4, F11 | F3 | none |
| Medium harm | F5, F6, F7, F8 | F5, F6 | F7, F8 | none |
| Low harm | F9, F10 | none | none | F9, F10 |

**6 of 12 failure modes are fully guarded by automated tests. 4 are partially guarded (the test catches the effect but not all vectors). 2 operational modes have no automated coverage (staleness banner is the manual fallback).**

## What the eval harness cannot catch

1. **Plausible-but-wrong numerics (F3 residual).** If the model says 48,000 evacuees when the real number is 50,000, no automated test flags it. The 50% drop gate catches gross errors, not subtle ones.

2. **Coordinated prompt injection (F12 residual).** Prompt injection is an attack that smuggles hidden commands into text the model reads. If an attacker controls ≥2 indexed sources and one spoofs an official domain, the corroboration gate passes. This requires a sophisticated, targeted attack. Low probability, but the architecture does not structurally prevent it.

3. **Silent scheduled-job death (F9).** The pipeline has no external heartbeat monitor. If the scheduled update job (cron) stops and the staleness banner has a bug, users see no signal. Mitigation: the staleness banner is tested by P0-3 (the staleness gate), so both would have to fail simultaneously.

4. **Subtle semantic drift.** The model might gradually shift tone (more alarming, more reassuring) without triggering any binary test. The human review step is the control here, not the eval harness.

## Design lesson

The eval harness is strongest where a failure mode is yes-or-no and catastrophic: all-clear vs. not, fabricated vs. real, stale vs. fresh. It is weakest where a failure mode is gradual and subtle: slightly wrong numbers, tone drift, or sophisticated injection. This matches the priority. The yes-or-no catastrophic failures are the ones that could kill someone. The gradual subtle ones degrade quality but do not create false safety signals.
