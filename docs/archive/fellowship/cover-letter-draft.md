# Cover Letter — Anthropic Fellows Program

I'm applying with a portfolio piece that demonstrates scalable oversight and AI control in a real deployment: **GG Tank Watch**, an emergency information dashboard serving ~50,000 evacuated residents during the Garden Grove chemical tank incident.

**Live:** https://gg-tank-watch.vercel.app (running; English, routing non-English speakers to officials). **Run the harness:** `python eval/run_all.py --skip integration` (48/48, exits 0). The repo trail below maps each safety principle to its code and tests.

The thesis: responsible AI and helpful AI are the same lane. Every safety constraint in GG Tank Watch made the product more trustworthy and more useful — the alignment tax was zero.

## Three evidence points

### 1. Scalable oversight applied to a consumer-facing AI system

An LLM summarizes live news roughly every 20–30 minutes into a dashboard that scared residents refresh at 2 AM. If the model hallucinates an "all-clear," a family might stop evacuating.

The eval harness (`eval/run_all.py`) runs 45 behavioral tests monitoring the system's safety contract. Fifteen target specific control properties: the corroboration gate (P0-1), source/URL integrity (P0-2), freshness honesty (P0-3), and date sanity (P1-1). These catch drift — fabricated sources, authored directives, stale data stamped as fresh — before it reaches users.

**Start here:** `docs/AI_CONTROL_ARCHITECTURE.md` → `eval/test_provenance.py`, `eval/test_freshness.py`

### 2. AI control in deployment — the system cannot exceed its authority

GG Tank Watch follows a **conduit pattern**: amplify, translate, and route official information. Never author safety directives. The LLM's output passes through a single validation chokepoint (`scripts/update_status.py`) before reaching the published snapshot.

The key design is **asymmetric gating**: danger upgrades fire on one source (over-warning is acceptable). Danger downgrades require two independent sources including one official agency (under-warning is catastrophic). This is a structural constraint enforced by code and verified by tests — not a prompt instruction. A single hallucinated boolean cannot reach users as an all-clear.

**Start here:** `docs/PRIOR_ART.md` → `docs/CODE_OF_CONDUCT.md` → `docs/FAILURE_ANALYSIS.md`

### 3. Empirical safety thinking — every safety property has a test that fails first

The `docs/FAILURE_ANALYSIS.md` red-team report maps 12 failure modes to their catching tests. Eight are fully guarded. Four are partially guarded. Two operational modes have no automated coverage — documented as residual risks with explicit rationale, not hidden.

The honest coverage reporting is itself a safety property: the system knows what it can't catch. The harness is strongest where failures are binary and catastrophic — exactly where it matters most.

**Start here:** `docs/FAILURE_ANALYSIS.md` → `eval/test_writer.py`, `eval/test_provenance.py`

## Why this matters

GG Tank Watch is a worked example of Anthropic's core insight: helpful, harmless, and honest are complementary. The safety constraints made the product more trustworthy, which made it more useful. The hardest call was language: this is Little Saigon, with the nation's highest Vietnamese limited-English rate (57%) — the residents most at risk. But an unverifiable machine translation of an evacuation instruction can get someone killed, so the conduit refuses to author or surface translations it can't reliably verify, and routes non-English speakers to the officials who publish verified copy (`docs/LANGUAGE_ACCESS.md`). Choosing not to ship is itself the safety decision.

This is what scalable oversight looks like when it ships: not a research paper, but a dashboard that 50,000 real people needed, built so it fails visibly stale and never confidently wrong.
