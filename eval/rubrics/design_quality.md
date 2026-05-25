# Rubric: design-decision quality

LLM-as-judge prompt template. Paste into Claude / GPT / Gemini with the target decision filled in.

## How to use

1. Pick a decision from `DESIGN_LOG.md` (e.g., D-003, D-016).
2. Paste the FULL decision block into the `{decision}` placeholder below.
3. Paste any relevant code excerpts into `{code_context}` (often the function/file the decision shaped).
4. Run the prompt against your LLM of choice.
5. Append the result to `eval/scores.jsonl` with `module: rubric_design_quality, test: D-NNN, passed: <bool>, metrics: <scores>`.

## Prompt

```
You are an experienced engineering manager evaluating a design decision on a personal-emergency-monitoring dashboard built by a single developer in <12 hours during an active chemical-tank incident in their neighborhood.

Background: the project is a Python writer + vanilla-JS dashboard, no backend, no build step. Read this design log entry and the code context it shaped, then score the decision on the rubric below.

DESIGN LOG ENTRY:
"""
{decision}
"""

CODE CONTEXT (the artifact the decision produced):
"""
{code_context}
"""

THE 6 PRINCIPLES THE PROJECT FOLLOWS:
P1 completeness — ship the whole thing
P2 boil lakes — fix everything in blast radius
P3 pragmatic — pick the cleaner of two viable options
P4 DRY — reject duplicates
P5 explicit — 10-line obvious fix > 200-line abstraction
P6 bias to action — merge > review cycles

SCORE THE DECISION ON THESE AXES (1-10 integer each):

1. **Correctness** — does it solve the actual problem stated in the Context? Score 10 if the problem is clearly resolved, 1 if the decision fails to address the real issue.

2. **Maintainability** — could another engineer pick up this codebase in 6 months and understand WHY this decision was made? Are the alternatives + rationale captured well? Are the principles applied transparently? Score 10 for a fully self-explaining decision, 1 for a "magic" choice with no traceable reasoning.

3. **User-fit** — based on the Status (Active / Superseded / Reverted), does the decision survive contact with the user? Active = high score. Superseded after extensive use = mid score. Reverted within hours = low score. Account for whether the supersession was "user discovered new requirements" (acceptable) vs "decision was wrong from the start" (low score).

4. **Reversibility** — if this decision turns out to be wrong, how expensive is the revert? Score 10 for "delete a function and move on", 1 for "rewrite from scratch."

5. **Principle alignment** — do the cited principles actually apply, or are they cargo-cult? Score 10 if the principles genuinely explain the choice, 1 if they're tacked on.

OUTPUT FORMAT (strict JSON only):

{
  "decision_id": "D-NNN",
  "scores": {
    "correctness": <int>,
    "maintainability": <int>,
    "user_fit": <int>,
    "reversibility": <int>,
    "principle_alignment": <int>
  },
  "composite": <float, average of the five>,
  "verdict": "<one of: excellent | sound | mixed | weak | wrong>",
  "strongest_aspect": "<one short sentence>",
  "biggest_concern": "<one short sentence, or null if none>",
  "would_revisit_in_6_months": <bool>
}

Do not include any text outside the JSON.
```

## Verdict bands (for the categorical `verdict` field)

| Composite | Verdict |
|---|---|
| 9.0–10.0 | excellent |
| 7.0–8.9 | sound |
| 5.0–6.9 | mixed |
| 3.0–4.9 | weak |
| < 3.0 | wrong |

## Notes

- The judge is asked to output strict JSON so the result can be machine-appended to `scores.jsonl`.
- If you want to cross-check, run the same prompt against multiple judges (Claude + GPT + Gemini) and look at inter-rater agreement (Kendall's τ or just visual diff). The `cross-vendor-judges` skill if available is the right tool.
- The rubric intentionally separates `correctness` from `user_fit` — a decision can be technically correct and still fail user-fit (see D-001).
