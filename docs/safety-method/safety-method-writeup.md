# Bounding an LLM's authority by code, not prompts: a worked example from a real chemical emergency

> A first-person writeup of the method and the build. Every claim traces to a file in the repo.

**TL;DR.** During a chemical-tank evacuation that moved about 50,000 people near me, I built a dashboard that used an LLM to summarize official and news sources every 30 minutes. The one failure that could get someone killed is the model confidently saying "it's safe" when it isn't. You can't fix that by prompting carefully. So I bounded the model's authority in the system itself. The tool is a pure information conduit: it routes people to officials and writes no safety verdicts of its own. Every model output passes through one validation chokepoint with asymmetric corroboration gates. A 208-test eval harness, with control-specific tests gating corroboration, provenance, freshness, and date sanity, checks the behavior on every update. The design principle is the testable one. You can't write an automated test for "the verdict is correct," but you can write one for "the system never exceeded its authority." This is a small, real instance of scalable oversight and AI control on a deployed consumer system, and the safety work made the product better, not worse.

## The setup

In May 2026 a methyl-methacrylate storage tank at an aerospace facility in Garden Grove, California started venting. About 50,000 people were placed under evacuation. I live downwind. The official channel, the city's emergency page, updated in slow bulk statements. A resident refreshing at 2 a.m. saw the same notice from 6 p.m. The thing residents actually wanted was a current, sourced, plain picture of what changed and what officials were saying, and it was scattered across news live-blogs buried in ads, with nothing in Vietnamese for a heavily Vietnamese-speaking area.

So I built a single-page dashboard. A Python step uses an LLM with web search to gather facts from official and news sources every 30 minutes. A writer step turns those facts into a small `status.json`. A static page renders it. Simple, except for one thing.

The failure that matters isn't "the dashboard is sometimes wrong." It's this: the model hallucinates an all-clear, the dashboard shows "INCIDENT RESOLVED," and a family that was sheltering decides it's safe to go home. A wrong "you're safe" is in a different category from a wrong "still dangerous." The whole problem comes down to one rule:

> The system has to fail visibly stale, never confidently wrong.

You don't get there by adding "please be careful, don't hallucinate" to a prompt. The model will hallucinate eventually. The safety has to live in the system, somewhere the model's output can't reach around.

## First move: be a conduit, not an authority

The early versions (v0.1 through v0.7) did the obvious thing. They geocoded your address, computed a blast radius, and handed you a verdict: ELEVATED, DOWNWIND, SAFE. That's the authority pattern, and it's a trap for three reasons.

It manufactures reliance. A tool that tells you "you're safe" is exactly the thing a wrong answer kills.

It competes with the official source. A confident verdict on my dashboard pulls attention away from the agency that's actually responsible for the call.

It puts the catastrophic failure right in front of the user. A hallucinated all-clear becomes a safety directive.

So I deleted all of it. The address checker, the blast-radius math, the plume layer, gone. I rebuilt the thing as a pure conduit. It never says "you should." It says "officials say X, confirm at the official source," and it sends every protective-action decision back to the authority that owns it. It amplifies, translates, and timestamps official information. It writes none of it.

The reason this is the right safety posture, and not just a careful one, comes down to what you can test:

> You can't write an automated test for "the safety verdict is correct." You can write one for "the system never wrote a safety verdict." Bounded authority is checkable. Correct authority is not.

That sentence is the whole idea. The conduit pattern moves the safety property from an unverifiable claim about output quality to a checkable claim about output authority. And it cost nothing. Removing the verdict made the product more trustworthy, because every statement is now sourced, and more useful, because residents get a clean current feed instead of a guess.

## The control layer

The model never writes the file people see. Its output goes through one chokepoint, `update_status.py`, and every safety-relevant field is validated before it reaches `status.json`. Four controls do the work, and the choice that ties them together is asymmetric trust.

| Direction | Gate | Why |
|---|---|---|
| Danger upgrade (injuries, expansion) | fires on 1 source | over-warning is acceptable |
| Danger downgrade (lifted, resolved) | needs 2+ sources, 1+ official | under-warning is catastrophic |
| Data freshness | advances only on source-backed facts | stale-but-fresh is worse than visibly stale |
| Provenance | dropped unless the URL was actually retrieved | a fabricated source is worse than a missing one |

**P0-1, corroboration gate.** A danger downgrade (`evacuation_lifted: true`, or an `incident_resolved_iso`) needs at least two independent sources, at least one of them an official agency host. Below that bar, the field is forced back to its safe default. One hallucinated boolean can't produce an all-clear. Danger upgrades fire on a single source, on purpose.

**P0-2, provenance check.** Every statement's `source_url` is checked against the URLs actually retrieved that run. A citation to a URL that wasn't fetched gets dropped. An unsourced statement gets rejected. The model can't invent a quote and pin it on an agency.

**P0-3, freshness honesty.** Two separate timestamps. `last_updated_iso` is when we wrote the file. `data_as_of_iso` is when we last actually learned something. An empty run keeps the old data timestamp, and the staleness banner keys off data age, not write age. The system can't stamp old data as fresh.

**P1-1, date sanity.** Future or malformed resolution dates get nulled before they can flip the incident to resolved. Severity is computed from structured fields, never read out of the model's prose.

There's also a failure contract. If the gather step fails (no key, network down, the model refuses), it exits non-zero with empty output, the writer is skipped, `status.json` is left untouched, and the staleness banner fires on schedule. Failure degrades to visibly stale, never to confidently wrong.

This is the part I think of as AI control. The system's authority is bounded by design, not by instruction. The corroboration gate doesn't ask the model to be careful. It makes a single hallucinated value unable to reach users as an official-looking all-clear.

## Scalable oversight: the eval harness

Structural controls are only worth trusting if you can show they hold, and keep holding as the code changes. So the controls come with a 208-test eval harness (208/208 via `python eval/run_all.py --skip integration`) whose control-specific tests gate corroboration, provenance, freshness, and date sanity, run every cycle and gate on exit code. A few of them:

- `test_lifted_requires_corroboration` and `test_resolved_requires_two_sources`: a single source can't authorize a downgrade.
- `test_fabricated_source_url_not_in_snapshot` and `test_statement_without_source_url_rejected`: invented provenance is dropped.
- `test_empty_facts_do_not_advance_data_as_of`: an empty run can't fake currency.
- `test_future_resolved_iso_suppressed`: a bad date can't resolve the incident.
- a conduit guard (`test_safety.py`) that asserts the dashboard writes no hazard verdicts (no blast-zone fields, no plume layer, no injury-radius copy) and always routes to an official source. The "be a conduit" decision is held by a test, not by my good intentions.

The harness is deliberately plain. Pure standard library, no pytest, no installs. Tests return `{passed, details}`. An append-only `scores.jsonl` means every run leaves a regression trace. The subjective checks (fact-extraction precision and recall, design quality) are LLM-as-judge rubric prompts rather than auto-run calls, so they're reproducible without an API key. The count isn't the point. The point is that each safety property the architecture claims has a test that fails before the property breaks, not after.

## The legal posture is the same principle

I did a fair amount of liability research before thinking about distribution. It's in `docs/LEGAL.md`, it's research and not legal advice, and a licensed attorney has to clear any public launch. What stood out is that the legally-safe posture and the AI-safe posture are the same posture.

- *Winter v. G.P. Putnam's Sons* (9th Cir. 1991) gives publishers a strong baseline shield for pure information, but it carves out technical data "used directly in dangerous activities." An interactive "is my address safe" verdict is exactly the functional output that loses that shield. Removing it pushed the tool back toward protected speech.
- The negligent-undertaking doctrine (Restatement 323 and 324A) turns on reliance. A conduit that writes no verdict gives reliance nothing to grab onto.
- Negligent misrepresentation (Restatement 552) needs a pecuniary interest. A free, non-commercial tool has none.
- Section 230 protects a conduit for other people's content, not for its own words. That's one more reason the summaries stay factual and sourced and the system writes no analysis.

So "bound your authority, route to the real authority, and don't manufacture reliance" is the alignment move and the liability move at the same time. Same lane.

## What this can't catch

The harness is strongest where failure is binary and catastrophic, and weakest where it's gradual and subtle. Honestly: 8 of 12 mapped failure modes are fully guarded by tests, 4 are partly guarded, and 2 operational ones have no automated coverage at all. It does not catch:

- Plausible-but-wrong numbers. 48,000 evacuees instead of 50,000 sails through. The gross-error gate catches a 50%-plus drop, not a small one.
- Coordinated prompt injection across two or more sources where one spoofs an official hostname. The corroboration gate blocks the single-source effect, not a determined multi-source cause. I accept that residual and write it down instead of pretending the architecture closes it.
- Silent cron death. There's no external heartbeat, so the staleness banner is the only in-app signal, and a banner bug plus a stopped cron would have to fail together.
- Gradual tone drift, the model slowly getting more reassuring. No binary test catches tone. The human review step is the control there, not the harness.

I'd rather a reviewer read that section than not. A safety system whose author can't tell you its blind spots isn't a safety system. It's a demo.

## Does the method generalize?

The safety contract here is hazard-agnostic. Disclose the AI, write no directives, route to officials, gate downgrades on corroboration, mark stale data stale, attach provenance to every fact. The parts that change between a chemical release and a wildfire or a flood are the data layers and the official sources, not the contract. In principle a typed per-incident config could carry the same controls and the same eval harness across hazard types, so a new incident would be a config file instead of a rewrite. I want to be careful about the claim, though. This is designed across hazards and built and evaluated for one. The generalization is a hypothesis with a clean shape, not a result I've shipped, and that's how I'd put it to a reviewer.

## Why I think this is an AI-safety artifact and not just a civic app

The thing worth writing down is small and concrete. A consumer-facing LLM system, deployed under real pressure for real people, whose authority is held by code and watched by an eval harness instead of by careful prompting. Every safety property is a structural invariant with a test behind it. The system fails toward visible staleness instead of confident error. And the constraints that made it safe are the same ones that made it more trustworthy and more useful. That's scalable oversight and AI control at hobby scale, but it's the same shape that matters at frontier scale. Don't ask the model to behave. Build the system so that when it misbehaves, the misbehavior can't reach the user looking like the truth.

I built it on my own, during the emergency, as someone who was downwind. The code, the control architecture, the eval harness, the failure analysis, and the legal research are all in the repo.

---

*Status: the tool is held behind a pre-distribution gate (attorney review) and stays `noindex` until that clears, so this is a writeup of the method and the build, not the launch of a public service. The legal section is research, not advice.*
