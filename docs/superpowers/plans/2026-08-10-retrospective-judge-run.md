# Retrospective Judge Run (data_quality rubric, adapted) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task in the MAIN thread (operator rule: no per-task subagent builds). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the repo's never-run LLM-as-judge instrument honestly — as a clearly labeled retrospective source-consistency check — record 64 judge rows in eval/scores.jsonl, and publish a results doc whose headline carries its own limitations.

**Architecture:** Two independent Opus judge seats (already run, identical prompts, separate contexts) scored 32/67 frozen timeline events against archived source metadata. This plan aggregates their JSON, restores the dirty ledger to HEAD before appending, and writes a results doc that inlines the adapted prompt and the four audit-measured honesty facts.

**Tech Stack:** Python 3 stdlib only (repo rule: no new deps), git, the existing eval ledger format.

## Global Constraints

- **No new `test_` functions anywhere** — the census guard locks doc counts to the discovered census (currently default=212, full=214, files=66); a new test function stales every "212" doc string. Verification = commands, never committed tests.
- **No push, no PR** without operator approval (public repo).
- **No suite run between the ledger append and the commit** — one suite run appends 634 lines (212 own + two 211-test child runs from `eval/test_summary_export.py`).
- **Halt tripwire:** any judge composite < 0.50 → stop, surface to operator (freeze-policy collision: rubric says "correct manually"; timeline.json is annotate-don't-erase incident content).
- **Framing rules (audit-mandated):** results titled "retrospective source-consistency check, adapted from the data_quality rubric" — never "the rubric, executed". Same-vendor judge delta reported descriptively, never as passing the rubric's cross-vendor ±0.15 bar. The four measured facts appear in the headline sentence AND limitations: 32/67 events judgeable (2 categories at zero coverage), median source = 103 chars (median 85.5% of event tokens absent from cited source — recomputed by this plan's own script; the audit's coarser tokenizer read 90.5%), 25 post-all-clear events pruned at freeze before any judging, judges are same-vendor (Claude) only.
- **Ledger row schema** (must match `eval/run_all.py` writer keys exactly, in order): `run_iso, module, test, category, passed, details, metrics`.
- Note: this plans/ directory is itself flagged for un-publishing at the PR gate (recruiter-audit fix list); committing here is correct for the branch, the directory's public fate is the operator's PR-gate call.

---

### Task 1: Pre-flight — suite green, then ledger restored to HEAD

**Files:**
- Modify (restore): `eval/scores.jsonl`

**Interfaces:**
- Produces: a 977-line HEAD-clean `eval/scores.jsonl` ending in a newline, ready for a clean 64-row append.

- [ ] **Step 1: Run the suite unpiped, read the summary line and exit code**

Run: `python eval/run_all.py --skip integration; echo "EXIT=$?"`
Expected: final block `TOTAL           212/212  (100.0% pass)` and `EXIT=0`.

- [ ] **Step 2: Restore the ledger (discards ~3,100 uncommitted local suite-run lines — operator-side ruling logged 2026-08-10; repo audit F21 recommends exactly this)**

Run: `git checkout -- eval/scores.jsonl && git diff --numstat eval/scores.jsonl; wc -l eval/scores.jsonl`
Expected: numstat prints nothing (clean); `977 eval/scores.jsonl`.

### Task 2: Aggregate the two judge JSONs and compute agreement (tool-run arithmetic)

**Files:**
- Create: `<session-scratchpad>/judge_a.json`, `<session-scratchpad>/judge_b.json` (the two seats' returned JSON, saved verbatim)
- Create: `<session-scratchpad>/judge_stats.json`

**Interfaces:**
- Consumes: Judge A/B final JSON (`{"judge","events":[{id,precision,recall,schema_fidelity,composite,notes}],"overall":{...}}`).
- Produces: `judge_stats.json` = `{per_judge_mean, per_judge_sd, mean_abs_delta, max_abs_delta, n_delta_gt_015, kendall_tau_composite, thin_source: {median_summary_chars, median_token_nonoverlap}, halts: [ids with composite<0.50]}`.

- [ ] **Step 1: Save both judge JSONs verbatim to scratchpad, then run the aggregator**

```python
# <session-scratchpad>/aggregate_judges.py
import json, statistics
from itertools import combinations
SP = r"<session-scratchpad>"
A = json.load(open(SP + r"\judge_a.json", encoding="utf-8"))
B = json.load(open(SP + r"\judge_b.json", encoding="utf-8"))
ae = {e["id"]: e for e in A["events"]}; be = {e["id"]: e for e in B["events"]}
assert set(ae) == set(be) and len(ae) == 32, f"id mismatch: {len(ae)}/{len(be)}"
deltas = {i: abs(ae[i]["composite"] - be[i]["composite"]) for i in ae}
def tau(xs, ys):
    pairs = list(combinations(range(len(xs)), 2)); c = d = 0
    for i, j in pairs:
        s = (xs[i]-xs[j]) * (ys[i]-ys[j])
        c += s > 0; d += s < 0
    return (c - d) / len(pairs)
ids = sorted(ae)
stats = {
  "per_judge_mean": {"A": statistics.mean(ae[i]["composite"] for i in ids),
                      "B": statistics.mean(be[i]["composite"] for i in ids)},
  "per_judge_sd": {"A": statistics.pstdev(ae[i]["composite"] for i in ids),
                    "B": statistics.pstdev(be[i]["composite"] for i in ids)},
  "mean_abs_delta": statistics.mean(deltas.values()),
  "max_abs_delta": max(deltas.values()),
  "n_delta_gt_015": sum(v > 0.15 for v in deltas.values()),
  "kendall_tau_composite": tau([ae[i]["composite"] for i in ids], [be[i]["composite"] for i in ids]),
  "halts": [i for i in ids if min(ae[i]["composite"], be[i]["composite"]) < 0.50],
}
json.dump(stats, open(SP + r"\judge_stats.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(stats, indent=1))
```

Run: `python <session-scratchpad>/aggregate_judges.py`
Expected: stats JSON printed; **if `halts` is non-empty → STOP, surface to operator, do not proceed to Task 3.**

- [ ] **Step 2: Recompute the thin-source facts for the results doc (from the committed packet rule, not the temp packet)**

```python
# <session-scratchpad>/thin_source.py
import json, re, statistics
R = r"<repo-root>"
t = json.load(open(R + r"\data\timeline.json", encoding="utf-8"))["events"]
a = json.load(open(R + r"\public\data\news_archive.json", encoding="utf-8"))["items"]
by = {i["url"]: i for i in a}
tok = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))
rows = []
for e in t:
    s = by.get(e.get("source_url"))
    if not s: continue
    ev = tok(e["title"] + " " + e["description"]); src = tok(s["title"] + " " + (s.get("summary") or "") + " " + s["outlet"])
    rows.append((len(s.get("summary") or ""), 1 - len(ev & src) / len(ev)))
print("n =", len(rows))
print("median_summary_chars =", statistics.median(r[0] for r in rows))
print("median_token_nonoverlap =", round(statistics.median(r[1] for r in rows), 3))
```

Run: `python <session-scratchpad>/thin_source.py`
Expected: `n = 32`, medians close to the audit's 103 chars / 0.905 (recomputed values go in the doc verbatim).

### Task 3: Append exactly 64 judge rows to the clean ledger

**Files:**
- Modify: `eval/scores.jsonl` (977 → 1,041 lines)

**Interfaces:**
- Consumes: `judge_a.json`, `judge_b.json`.
- Produces: 64 ledger rows, schema-identical to the writer's: `{"run_iso","module":"rubrics/data_quality_retrospective","test":"<event-id>/<A|B>","category":"judge","passed":<composite>=0.80>,"details","metrics":{precision,recall,schema_fidelity,composite,judge}}`.

- [ ] **Step 1: Append via script**

```python
# <session-scratchpad>/append_rows.py
import json, datetime
SP = r"<session-scratchpad>"; R = r"<repo-root>"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rows = []
for path, tag in ((SP + r"\judge_a.json", "A"), (SP + r"\judge_b.json", "B")):
    J = json.load(open(path, encoding="utf-8"))
    for e in sorted(J["events"], key=lambda x: x["id"]):
        rows.append({"run_iso": now, "module": "rubrics/data_quality_retrospective",
                     "test": f"{e['id']}/{tag}", "category": "judge",
                     "passed": e["composite"] >= 0.80,
                     "details": (e.get("notes") or "")[:200],
                     "metrics": {"precision": e["precision"], "recall": e["recall"],
                                  "schema_fidelity": e["schema_fidelity"],
                                  "composite": e["composite"], "judge": tag}})
assert len(rows) == 64, len(rows)
with open(R + r"\eval\scores.jsonl", "a", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print("appended", len(rows))
```

Run: `python <session-scratchpad>/append_rows.py`
Expected: `appended 64`.

- [ ] **Step 2: Verify the append is exactly 64 parseable lines**

Run: `wc -l eval/scores.jsonl && git diff --numstat eval/scores.jsonl && python -c "import json;[json.loads(l) for l in open(r'eval/scores.jsonl',encoding='utf-8')];print('all parse')"`
Expected: `1041`, numstat `64	0`, `all parse`.

### Task 4: Results doc + rubric pointer + ledger-category note

**Files:**
- Create: `eval/rubrics/data_quality_results.md`
- Modify: `eval/rubrics/data_quality.md` (one pointer line at top)
- Modify: `eval/README.md` (one line explaining `category:"judge"`)

**Interfaces:**
- Consumes: `judge_stats.json`, thin-source medians, both judges' per-event scores.
- Produces: the public results artifact; headline sentence carries artifact + subset + source depth.

- [ ] **Step 1: Write `eval/rubrics/data_quality_results.md`** — MUST contain, in order: (1) a headline sentence of the form "A retrospective source-consistency check — adapted from this repo's unrun data_quality rubric — scored 32 of 67 frozen timeline events (2 categories had zero judgeable rows; 25 post-all-clear events were pruned at freeze before any judging) against archived source metadata whose median summary is ~<N> characters, using two same-vendor (Claude) judges."; (2) the verbatim adapted judge prompt (copy from the session transcript block, both seats identical); (3) the reproducible selection rule: "the 32 of 67 `data/timeline.json` events whose `source_url` exactly matches an item `url` in `public/data/news_archive.json`"; (4) per-event score table (id | A composite | B composite | |Δ| | min verdict band); (5) agreement stats reported descriptively ("two same-vendor seats differed by mean |Δ|=<x>, max <y>, Kendall τ=<z> on composite ranks; the rubric's ±0.15 bar was written for cross-vendor panels and is NOT claimed"); (6) the limitations paragraph naming all four measured facts plus "fabrication detection is out of reach at ~100 characters of source — precision is a consistency floor, not a hallucination audit"; (7) what would upgrade it (cross-vendor seats; full-text sources; the unrun original prompt needing retained snippets).

- [ ] **Step 2: Add the pointer line at the top of `eval/rubrics/data_quality.md`** (below the H1): `> **Status:** the prompt below has never been run as written (its raw live snippets were not retained). A retrospective adaptation was run 2026-08-10 — see [data_quality_results.md](data_quality_results.md) for scores and limitations.`

- [ ] **Step 3: Add to `eval/README.md`** (ledger section): `Rows with category:"judge" are LLM-as-judge rubric scores (see rubrics/data_quality_results.md), not pass/fail test runs; their "passed" flag means composite ≥ 0.80 (the rubric's acceptable band).`

- [ ] **Step 4: Verify census guard still green (no test functions were added)**

Run: `python -c "import sys;sys.path.insert(0,'eval');import test_readme_archive_count as t;r=t.test_readme_breakdown_matches_data();print(r['passed'],r['details'][:120])"`
Expected: `True ...`.

### Task 5: Tripwire check, then commit

**Files:**
- Commit: `eval/scores.jsonl`, `eval/rubrics/data_quality_results.md`, `eval/rubrics/data_quality.md`, `eval/README.md`, `docs/superpowers/plans/2026-08-10-retrospective-judge-run.md`

- [ ] **Step 1: Stage by pathspec and run the staged-numstat tripwire**

Run: `git add eval/scores.jsonl eval/rubrics/data_quality_results.md eval/rubrics/data_quality.md eval/README.md docs/superpowers/plans/2026-08-10-retrospective-judge-run.md && git diff --cached --numstat eval/scores.jsonl`
Expected: `64	0	eval/scores.jsonl` — **anything other than 64 additions → halt, unstage (`git restore --staged eval/scores.jsonl`), re-run Task 1 Step 2 + Task 3.**

- [ ] **Step 2: Commit (no suite run happened since the append)**

```bash
git commit -m "Run the judge rubric retrospectively: 64 scores + honest results doc

The recruiter audit found the authored LLM-as-judge rubric had never been
executed (zero judge rows anywhere in the ledger; committed baseline 977 lines). Raw live snippets were
never retained, so this is a labeled retrospective source-consistency
check (32/67 events, archived one-line sources, two same-vendor judges)
- limitations carried in the headline, ledger restored to HEAD first per
audit F21 so exactly 64 rows land.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: commit lands on `fix/recruiter-audit-packaging`; branch now 3 ahead of `cdb9f1c`. **No push** — operator approval at the PR gate.
