# Cover Letter — Anthropic Fellows Program

I'm applying with a portfolio piece that demonstrates scalable oversight and AI control in a real deployment: **GG Tank Watch**, an emergency information dashboard serving ~50,000 evacuated residents during the Garden Grove chemical tank incident.

The thesis is simple: responsible AI and helpful AI are the same lane. Every safety constraint in GG Tank Watch made the product more trustworthy and more useful — the alignment tax was zero.

## Three evidence points

### 1. Scalable oversight applied to a consumer-facing AI system

An LLM summarizes live news sources every 30 minutes and writes structured data to a dashboard that scared residents are refreshing at 2 AM. If the model hallucinates an "all-clear," a family might stop evacuating.

The eval harness (`eval/run_all.py`) runs 45 behavioral tests that monitor the system's safety contract. Fifteen of these target specific control properties: the corroboration gate (P0-1), source/URL integrity (P0-2), freshness honesty (P0-3), and date sanity (P1-1). The tests catch when the system drifts from its safety contract — fabricated sources, authored directives, stale data presented as fresh — before the drift reaches users.

This is scalable oversight applied to a consumer tool: automated behavioral tests that enforce safety properties a human reviewer couldn't continuously monitor across every 30-minute update cycle.

**Start here:** `docs/AI_CONTROL_ARCHITECTURE.md` (architecture + test mapping) → `eval/test_provenance.py`, `eval/test_freshness.py` (the tests themselves).

### 2. AI control in deployment — the system cannot exceed its authority

GG Tank Watch follows a **conduit pattern**: amplify, translate, and route official information. Never author safety directives. The LLM's output enters through a single chokepoint (`scripts/update_status.py`) where every safety-relevant field passes through validation before reaching the published snapshot.

The key design is **asymmetric gating**: danger upgrades (injuries, expansion) fire on one source, because over-warning is acceptable. Danger downgrades (evacuation lifted, incident resolved) require at least two independent sources including one official agency, because under-warning is catastrophic. This isn't a prompt instruction — it's a structural constraint enforced by code (`apply_corroboration_gate`) and verified by tests (`test_lifted_requires_corroboration`, `test_resolved_requires_two_sources`).

The system's authority is bounded by design, not by instruction. A single hallucinated boolean cannot reach users as an all-clear.

**Start here:** `docs/PRIOR_ART.md` (conduit vs. authority pattern) → `docs/CODE_OF_CONDUCT.md` (8 editorial principles) → `docs/FAILURE_ANALYSIS.md` (12-mode red team).

### 3. Empirical safety thinking — every safety property has a test that fails first

The `docs/FAILURE_ANALYSIS.md` red-team report maps all 12 failure modes to the specific tests that catch them, and honestly identifies which modes remain unguarded. Eight of twelve are fully guarded. Four are partially guarded (the test catches the effect but not all vectors). Two operational modes have no automated coverage.

The honest coverage reporting is itself a safety property: the system knows what it can't catch. Plausible-but-wrong numerics, coordinated prompt injection, silent cron death, and subtle semantic drift are documented as residual risks with explicit rationale for why they're accepted.

Every safety property has a test that fails before the property is violated, not after. The harness is strongest where failures are binary and catastrophic — exactly where it matters most.

**Start here:** `docs/FAILURE_ANALYSIS.md` (failure mode → test mapping) → `eval/test_writer.py`, `eval/test_provenance.py` (the tests).

## Why this matters

Responsible AI deployment is not theoretical — it's engineering discipline. GG Tank Watch is a worked example of Anthropic's core insight that helpful, harmless, and honest are complementary, not competing. The safety constraints (harmless) made the product more trustworthy (honest), which made it more useful (helpful). The bilingual access framework (`docs/LANGUAGE_ACCESS.md`) targets the 57% of local Vietnamese speakers who are limited-English-proficient — the people most at risk and least served by English-only channels.

This is what scalable oversight looks like when it ships: not a research paper, but a dashboard that 50,000 real people needed, built so it fails visibly stale and never confidently wrong.
