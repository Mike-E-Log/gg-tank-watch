# Rubric: writer data-quality (LLM-as-judge for fact extraction)

LLM-as-judge prompt template for evaluating how well the writer turns news-derived facts into a `status.json` snapshot. Tests for precision (no hallucinated facts), recall (no missed material updates), and consistency (same input → same output).

## How to use

1. Pick a recent `/loop` tick.
2. Capture the raw WebSearch snippets that fed that tick into `{source_snippets}`.
3. Capture the JSON facts that were piped to `update_status.py` into `{extracted_facts}`.
4. Capture the produced `status.json` snapshot into `{snapshot}`.
5. Run the prompt against your LLM judge.
6. Append the result to `eval/scores.jsonl`.

## Prompt

```
You are evaluating an information-extraction pipeline that turns raw news snippets about an emergency incident into a structured snapshot.

Pipeline:
  raw news snippets → structured facts JSON → snapshot (status.json)

Your job: score the EXTRACTION step (snippets → facts JSON) on three axes.

RAW SOURCE SNIPPETS (input to the extractor):
"""
{source_snippets}
"""

EXTRACTED FACTS JSON (the structured output):
"""
{extracted_facts}
"""

FINAL SNAPSHOT (for context, downstream of extraction):
"""
{snapshot}
"""

SCORE ON THESE THREE AXES (0.0–1.0 float each):

1. **Precision** — every claim in the extracted facts is supported by the source snippets. Score 1.0 if no hallucinations; 0.0 if facts appear that have no basis in the sources.
   - For each numeric/categorical field in extracted_facts, verify it appears (or is reasonably derivable) from the snippets.
   - Penalize fabricated quotes in `official_statements`, fabricated agency names, made-up `time_iso` values.

2. **Recall** — every material update mentioned in the snippets appears in the extracted facts. Score 1.0 if nothing important is missed; 0.0 if the snippets contain a major fact (e.g., "evacuation lifted at 3pm") that isn't reflected in the extraction.
   - List material facts in snippets that are missing from extraction.

3. **Schema fidelity** — extracted_facts conforms to the documented schema (correct field names, correct types, ISO timestamps, etc.). Score 1.0 if perfectly conforming; reduce for malformed fields.

SCORE OUTPUT:

{
  "tick_iso": "<the tick timestamp>",
  "precision": <float 0-1>,
  "recall": <float 0-1>,
  "schema_fidelity": <float 0-1>,
  "composite": <float, average of the three>,
  "hallucinations": [<list of facts in extraction not supported by sources>],
  "missed_facts": [<list of material facts in sources not extracted>],
  "schema_issues": [<list of fields with wrong type/shape>],
  "verdict": "<one of: gold | acceptable | concerning | unusable>"
}

Output strict JSON only.
```

## Verdict bands

| Composite | Verdict | Action |
|---|---|---|
| 0.95+ | gold | nothing |
| 0.80–0.94 | acceptable | review hallucinations/missed_facts; tune prompt if pattern emerges |
| 0.50–0.79 | concerning | hand-correct the snapshot; investigate why the extractor missed/hallucinated |
| < 0.50 | unusable | the snapshot is wrong; correct manually + harden the extraction prompt |

## What gets ground-truthed

For a held-out gold-standard set, capture 5-10 ticks where:
- The raw snippets are saved verbatim
- A human (Anna) reviews the extraction and corrects any errors → produces a "gold" facts JSON
- The judge scores the actual extraction against the gold

Over time, regressions in extraction quality become visible: composite score drops, hallucinations rise, missed facts cluster around a specific field.

## Inter-rater agreement (recommended)

Run the same prompt against 2-3 judges (Claude, GPT, Gemini) and compute:
- Mean composite ± stddev
- Kendall's τ rank-agreement on hallucinations and missed_facts lists

If judges disagree by more than ±0.15 on composite, the rubric is too subjective — refine the prompt.
