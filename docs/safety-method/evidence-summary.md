# Evidence Summary — Safety Principle Matrix

One-page cheat sheet mapping each Anthropic safety principle to its implementation and verifiable evidence in this repo.

## Principle → Implementation → Evidence

| Principle | Implementation | Evidence File | Key Test(s) |
|-----------|---------------|---------------|-------------|
| **Honesty / AI transparency** | Persistent disclosure on every page: "compiled with AI assistance, checked by a person." AI involvement is never hidden. | `dashboard.html` (`STRINGS.disclosure`), `docs/CODE_OF_CONDUCT.md` (principle 6) | Visual: disclosure string renders on all views |
| **Avoiding harm** | Information conduit only — amplifies and routes to officials, never authors safety directives. The distinction between "officials say X" and "you should do X" is load-bearing. | `docs/PRIOR_ART.md` (conduit vs. authority), `docs/CODE_OF_CONDUCT.md` (principle 2: no directives) | `eval/test_provenance.py`: fabricated sources dropped; editorial policy enforced by code, not prompting |
| **Human oversight** | Human reviews all AI summaries before publication. The app ships **English only**: we never surface translated safety copy without reliable human verification (G1) — the most conservative form of the rule — and route LEP residents to officials, who publish their own verified translations. | `docs/CODE_OF_CONDUCT.md` (principle 6), `docs/LANGUAGE_ACCESS.md` (G1 binding constraint) | `eval/test_language_access.py` (build-failing G1 gate); pipeline: `gather_facts.py` → human review → `update_status.py` → publish |
| **Scalable oversight** | 210-test eval harness monitors behavioral properties across every update cycle. Control-specific tests enforce corroboration (P0-1), provenance (P0-2), freshness (P0-3), date sanity (P1-1), and the G1 language-access gate. | `docs/AI_CONTROL_ARCHITECTURE.md`, `eval/run_all.py`, `docs/FAILURE_ANALYSIS.md` | `test_lifted_requires_corroboration`, `test_fabricated_source_url_not_in_snapshot`, `test_empty_facts_do_not_advance_data_as_of`, `test_future_resolved_iso_suppressed` |
| **Responsible deployment** | Attorney review gates public launch (Lane B3). Entity + insurance required. `noindex` until legal clearance. Honest coverage reporting: 8/12 modes guarded, 4 partial, 2 unguarded — documented, not hidden. | `CLAUDE.md` (constraints section), `docs/FAILURE_ANALYSIS.md` (coverage summary + "what the harness cannot catch") | Pre-launch: `noindex` meta tag active; eval harness exit-code gated |
| **Alignment tax = zero** | Safety constraints made the product better, not worse. Removing authored verdicts and adding source attribution improved both user trust and legal standing. The conduit pattern is more useful than the authority pattern it replaced. | `docs/PRIOR_ART.md` ("Why Option B is correct"), `docs/AI_CONTROL_ARCHITECTURE.md` (closing section) | Comparative: v0.1–v0.7 (authority pattern) vs. current (conduit pattern) — same codebase, better product |

## Control layer detail

| Control | Property | What it prevents | Test count | Key tests |
|---------|----------|-----------------|------------|-----------|
| **P0-1** Corroboration gate | Danger downgrades require ≥2 sources, ≥1 official | Fabricated all-clear (F1) | 2 | `test_lifted_requires_corroboration`, `test_resolved_requires_two_sources` |
| **P0-2** Source/URL integrity | Statements must cite a URL actually retrieved this run | Fabricated provenance (F2) | 3 | `test_fabricated_source_url_not_in_snapshot`, `test_statement_without_source_url_rejected`, `test_sources_checked_all_wellformed` |
| **P0-3** Freshness honesty | `data_as_of_iso` advances only on source-backed facts | Stale-but-fresh-stamped (F4) | 3 | `test_empty_facts_do_not_advance_data_as_of`, `test_all_null_facts_treated_as_no_data`, `test_stale_after_is_data_as_of_plus_maxage` |
| **P1-1** Date sanity | Future/malformed timestamps nulled | Fabricated resolution date (F11) | 3 | `test_future_resolved_iso_suppressed`, `test_malformed_resolved_iso_suppressed`, `test_valid_resolved_iso_honored` |
| **G1** Language-access gate | App ships English-only — no non-English safety-copy surface at all (the most conservative G1); route LEP residents to officials | Unverified MT/AI safety copy reaching LEP residents | 2 | `test_no_unverified_language_ships`, `test_english_only` |
| Severity derivation | Computed from facts, never extracted from LLM | Severity miscompute (F3/F5) | 1 | `test_partial_facts_dont_downgrade_severity` |
| Gatherer failure | Non-zero exit + empty stdout on failure | Silent bad data (F6/F9) | 1 | `test_graceful_failure_no_api_key` |
| Encoding | UTF-8 survives cp1252 locale | Character corruption | 2 | `test_em_dash_survives_non_utf8_locale`, `test_degree_sign_survives_non_utf8_locale` |

## Design principle: asymmetric trust

| Direction | Gate | Rationale |
|-----------|------|-----------|
| Danger upgrade (injuries, expansion) | Fires on 1 source | Over-warning is acceptable |
| Danger downgrade (lifted, resolved) | Requires ≥2 sources, ≥1 official | Under-warning is catastrophic |
| Data freshness | Advances only on source-backed facts | Stale-but-fresh is worse than visibly stale |
| Provenance | Dropped unless URL was actually retrieved | A fabricated source is worse than a missing one |

## The bottom line

GG Tank Watch is a worked example of Anthropic's core insight: helpful, harmless, and honest are complementary. The safety constraints (harmless) made the product more trustworthy (honest), which made it more useful (helpful). No tradeoff was required. The system fails visibly stale, never confidently wrong.
