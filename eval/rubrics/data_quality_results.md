# Retrospective source-consistency check — results (2026-08-10)

**What this is, in one sentence:** a retrospective source-consistency check — adapted
from this repo's unrun `data_quality.md` rubric — scored 32 of 67 frozen timeline events
(2 categories, community_impact and air_quality, had zero judgeable rows; 25 post-all-clear
events were pruned at the June 2026 freeze before any judging) against archived source
metadata whose median summary is 103 characters (median 85.5% of an event's content tokens
do not appear in its cited source's metadata), using two same-vendor (Claude Opus) judges.

That sentence is the honest headline. Everything below expands it.

## Why this exists, and what it is not

The rubric at [data_quality.md](data_quality.md) was authored during the incident but its
prompt was never run as written: it requires the raw WebSearch snippets that fed each live
tick, and those were never retained. This run is therefore NOT "the rubric, executed." It
scores a different, adjacent artifact pair — the frozen curated timeline against the frozen
source archive — because that is the only input pair that still exists. It measures
citation consistency of the archived outputs, not extraction quality of the live pipeline.

## The judge prompt (verbatim, identical for both seats; separate contexts, neither saw the other)

```
You are Judge {A|B}, an independent LLM-as-judge seat in a retrospective data-quality
audit of a frozen emergency-information archive. Evidence bar: judge only from the files
named below; never invent facts.

Read these two files:
1. <session scratchpad>/judge_packet.json — 32 timeline events, each paired with its cited
   archived source (title, outlet, type, published_iso, one-line summary).
2. <repo>/eval/rubrics/data_quality.md — the rubric being adapted (its original inputs,
   raw live snippets, were never retained; this is a retrospective run against archived
   source metadata).

For EACH of the 32 events, score three axes, 0.0-1.0 floats:
- precision — every claim in the event's title+description is supported by or consistent
  with the cited source's archived metadata. Penalize claims the cited source cannot
  plausibly carry (wrong topic, contradicting fact). When the one-line summary is too
  thin to confirm a specific detail (an exact temperature, a street boundary), score on
  consistency and flag the detail in notes as "thin-source" rather than calling it a
  hallucination.
- recall — the event captures the central fact of its cited source (curated brevity is
  expected; only score down when the source's headline fact is absent or distorted).
- schema_fidelity — timestamp_utc is well-formed ISO-8601 Zulu, falls within
  2026-05-21T00:00:00Z..2026-05-27T23:59:59Z, the "day" number is consistent with the
  timestamp (day 1 = May 21 local Pacific), and the category label fits the content.

composite = mean of the three.

Return ONLY strict JSON as your final message — no prose, no markdown fences:
{"judge":"{A|B}","events":[{"id":"...","precision":0.0,"recall":0.0,"schema_fidelity":0.0,
"composite":0.0,"notes":"..."}],"overall":{"mean_composite":0.0,"hallucinations":["..."],
"thin_source_count":0,"verdict":"gold|acceptable|concerning|unusable"}}
```

## Reproducible selection rule

The judged set is exactly: the 32 of 67 `data/timeline.json` events whose `source_url`
exactly matches an item `url` in `public/data/news_archive.json`. No other filtering.
The skew this rule introduces: community_impact (0 of 6) and air_quality (0 of 2) events
have no judgeable rows; Day 1 contributes only 1 of its 5 events; excluded citations
include Wikipedia (9 events) and VnExpress (3, Vietnamese-language).

## Per-event scores

Band = the rubric's verdict band applied to the LOWER of the two composites
(gold ≥ 0.95, acceptable 0.80–0.94, concerning 0.50–0.79, unusable < 0.50).

| event | Judge A | Judge B | \|Δ\| | band (min) |
|---|---|---|---|---|
| evt-20260521-004 | 0.917 | 0.883 | 0.034 | acceptable |
| evt-20260522-004 | 0.917 | 0.933 | 0.016 | acceptable |
| evt-20260522-007 | 0.857 | 0.867 | 0.010 | acceptable |
| evt-20260522-010 | 0.943 | 0.933 | 0.010 | acceptable |
| evt-20260522-011 | 0.910 | 0.867 | 0.043 | acceptable |
| evt-20260523-002 | 0.850 | 0.867 | 0.017 | acceptable |
| evt-20260523-004 | 0.933 | 0.900 | 0.033 | acceptable |
| evt-20260523-006 | 0.790 | 0.800 | 0.010 | concerning |
| evt-20260523-008 | 1.000 | 1.000 | 0.000 | gold |
| evt-20260523-010 | 0.867 | 0.817 | 0.050 | acceptable |
| evt-20260523-012 | 0.843 | 0.850 | 0.007 | acceptable |
| evt-20260523-014 | 0.750 | 0.767 | 0.017 | concerning |
| evt-20260524-002 | 0.933 | 0.917 | 0.016 | acceptable |
| evt-20260524-007 | 0.827 | 0.800 | 0.027 | acceptable |
| evt-20260524-009 | 0.933 | 0.917 | 0.016 | acceptable |
| evt-20260524-010 | 0.633 | 0.650 | 0.017 | concerning |
| evt-20260524-011 | 0.943 | 0.950 | 0.007 | acceptable |
| evt-20260524-014 | 0.917 | 0.900 | 0.017 | acceptable |
| evt-20260525-001 | 0.960 | 0.950 | 0.010 | gold |
| evt-20260525-002 | 0.917 | 0.917 | 0.000 | acceptable |
| evt-20260525-003 | 0.883 | 0.883 | 0.000 | acceptable |
| evt-20260525-006 | 0.967 | 0.967 | 0.000 | gold |
| evt-20260526-001 | 0.960 | 0.933 | 0.027 | acceptable |
| evt-20260526-002 | 0.850 | 0.850 | 0.000 | acceptable |
| evt-20260526-003 | 0.900 | 0.900 | 0.000 | acceptable |
| evt-20260526-004 | 0.857 | 0.850 | 0.007 | acceptable |
| evt-20260526-005 | 0.550 | 0.517 | 0.033 | concerning |
| evt-20260526-006 | 0.890 | 0.850 | 0.040 | acceptable |
| evt-20260526-008 | 0.817 | 0.700 | 0.117 | concerning |
| evt-20260527-001 | 0.857 | 0.817 | 0.040 | acceptable |
| evt-20260527-002 | 0.890 | 0.833 | 0.057 | acceptable |
| evt-20260527-004 | 0.733 | 0.650 | 0.083 | concerning |

Band counts (min of two judges): **3 gold · 23 acceptable · 6 concerning · 0 unusable.**

## Agreement — reported descriptively, no validity claim

Judge A mean composite 0.869 (sd 0.094); Judge B mean 0.851 (sd 0.101). Mean per-event
\|Δ\| = 0.024, max 0.117, zero events differ by more than 0.15; Kendall τ on composite
ranks = 0.81. Two caveats bound what this means. First, the rubric's ±0.15 subjectivity
bar was written for a cross-vendor panel (Claude, GPT, Gemini); these are two same-vendor
seats, so that bar is NOT claimed as passed. Second, a mean delta this small (< 0.05)
between same-vendor seats given an identical protocol is better read as shared priors
than as independent agreement — the number describes consistency, not objectivity.

## What the judges found (convergent, both seats independently)

- **Three wrong-article citations** — real defects, not thin sources: evt-20260526-005
  (a May 26 council meeting cited to the May 21 initial evacuation order — worst in the
  set, composites 0.55/0.52), evt-20260524-010 (a school-closure roster cited to the
  May 26 orders-lifted update), evt-20260526-008 (a tank-transfer operation cited to an
  unrelated day-earlier page).
- **A weekday-label cluster**: evt-20260526-004, evt-20260527-001, evt-20260527-004 each
  carry a weekday word one day earlier than their timestamp (calendar-verified by both
  seats); evt-20260527-004 also holds the set's only schema violation (timestamp
  2026-05-28T01:00:00Z, outside the incident window, though day-7-consistent locally).
- **One probable duplicate**: insulation removal reported twice ~29 hours apart
  (evt-20260524-009 vs evt-20260526-002).
- **One uncited second outlet**: the Fox News half of evt-20260524-014.

Per the archive's freeze policy (corrections annotate in place, never erase), whether
these findings produce dated correction notes in the timeline is an operator decision,
tracked outside this file. Nothing in the timeline was altered by this run.

## Limitations (the facts that bound every number above)

Only 32 of 67 events were judgeable, with two whole categories at zero coverage. The
judged set is post-curation: 25 post-all-clear events were pruned at the freeze, so the
rows most likely to score badly were removed before any judging. The evidence base is
thin: median cited-source summary is 103 characters, and a median 85.5% of an event's
content tokens do not appear anywhere in its cited source's metadata — so precision here
is a consistency floor with a stated evidence ceiling, and fabrication detection is out
of reach at ~100 characters of source. Both judges are the same vendor and model family.
`passed` in the score ledger means composite ≥ 0.80 (the rubric's acceptable band).

## What would upgrade this

Cross-vendor seats (the rubric's own inter-rater spec); full-text sources instead of
one-line summaries; and, for the original instrument, retained raw snippets — without
them the rubric's own prompt remains unrunnable as written.
