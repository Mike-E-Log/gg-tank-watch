# Test fixtures

This directory is for held-out gold-standard data used by the eval suite. Add files here when you have data that:

1. Doesn't change run-to-run (frozen ground truth)
2. Would be expensive to regenerate (e.g., manually-corrected extractions)
3. Doesn't belong inline in a test file (too large)

## Suggested files (not yet seeded — populate as the project matures)

| File | Purpose |
|---|---|
| `gold_extractions/tick_<timestamp>.json` | Pairs of `{source_snippets, gold_facts}` for the LLM-as-judge data-quality rubric. |
| `safety_test_points.json` | Lat/lon points with hand-labeled safety verdicts. Used by `test_safety.py` to expand beyond the inline cases. |
| `known_evac_addresses.json` | Addresses known to be inside/outside the official evac zone, for cross-validation against the polygon. |

## Why this isn't seeded yet

The project is days old. Real gold-standard data accumulates as the writer runs over time and Nancy reviews extractions. Seeding fake fixtures now would just create noise.
