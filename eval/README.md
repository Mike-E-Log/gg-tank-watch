# Eval suite

Behavioral + schema + LLM-as-judge evaluation for GG Tank Watch. Designed to ship the data-quality discipline an analytics engineer would expect: schema validation, regression coverage on every load-bearing decision, append-only score history, and prompt-templates for LLM-judged subjective grading.

## What gets evaluated

| Suite | File | What it checks | Type |
|---|---|---|---|
| Writer behavior | `test_writer.py` | 5-state sequence (baseline → no-diff → urgent-toggle → stable → resolved) + new-statement detection + residents-shift rate-limiting + classification of URGENT vs INFO level | Behavioral |
| Conduit guard | `test_safety.py` | Asserts the dashboard authors no hazard verdicts (no `blast_zones_mi`, no plume layer, no injury-radius copy) and routes users to an official source. | Behavioral |
| Geocoder (legacy) | `test_geocoder.py` | Live Nominatim regression for the pre-conduit address checker (two fixed-point intersections + a full street address). The checker was removed in the conduit pivot; retained as a skipped integration test. Requires internet. | Integration |
| Schema | `test_schema.py` | `status.json` and `config.json` validate against expected shape (required fields, type expectations, semantic invariants). | Schema |
| Design quality (rubric) | `rubrics/design_quality.md` | LLM-as-judge prompt template for grading any `DESIGN_LOG.md` entry on a 1-10 rubric. Not invoked by `run_all.py` — paste into your LLM of choice. | Subjective |
| Data quality (rubric) | `rubrics/data_quality.md` | LLM-as-judge prompt template for grading writer fact extraction (precision, recall, hallucination check) against a held-out gold-standard JSON. | Subjective |

## Running

```powershell
# from the repo root
python eval/run_all.py
```

What you get:
- A scorecard printed to stdout
- One JSON line appended to `scores.jsonl` per test
- Exit code 0 if all pass, non-zero if any fail

Skip the geocoder (internet-dependent) with:

```powershell
# from the repo root
python eval/run_all.py --skip integration
```

## Design — why this is shaped the way it is

- **Pure stdlib.** No `pytest`, no `pydantic`, no fixtures library. The "tests" are functions that return `{passed, details}`. This keeps the eval suite runnable on any Python 3.10+ install without `pip install`-ing anything.
- **Append-only history (`scores.jsonl`).** Every run leaves a trace. Regression tracking comes free: `grep "test_writer" scores.jsonl` shows the history of that test.
- **Classification: behavioral / schema / integration / subjective.** Run flags can skip categories that aren't appropriate for the current context (e.g., skip `integration` in air-gapped CI).
- **LLM-as-judge as prompt templates, not auto-invoked.** Adding an actual Anthropic/OpenAI call requires an API key. The rubric prompts are reproducible and copy-paste-able into whatever judge you have access to. When you run a judge, paste the result into `scores.jsonl` manually with `--manual-score` (see `run_all.py --help`).
- **Held-out test cases that don't change.** The geocoder regression points (e.g., "Magnolia & Talbert" → fixed coordinates) are pinned expected outputs. If Nominatim drifts, the legacy integration test catches it.

## What's NOT covered (yet)

- **Real LLM-as-judge invocation.** Rubrics exist; `run_all.py` doesn't call any LLM. Adding this requires an API key + per-run cost — left as a manual step.
- **Browser / DOM tests.** No headless Chrome or Playwright. Would need additional deps. The dashboard renders are eyeball-checked by Nancy.
- **Wind data freshness.** NOAA API call is in the dashboard JS, not in the Python eval path. Could add a `test_wind.py` that hits api.weather.gov; not done yet.
- **Atomic-write retry under contention.** Hard to test deterministically (the OneDrive race is non-deterministic). Manual fault injection would be the right approach; deferred.

## Adding a new test

1. Create `eval/test_<thing>.py`
2. Define functions starting with `test_` returning `{"passed": bool, "details": str, "metrics": dict}`
3. Re-run `python run_all.py` — your test is auto-discovered.

Example:

```python
def test_my_new_thing():
    actual = compute_something()
    expected = 42
    return {
        "passed": actual == expected,
        "details": f"got {actual}, expected {expected}",
        "metrics": {"actual": actual, "expected": expected}
    }
```
