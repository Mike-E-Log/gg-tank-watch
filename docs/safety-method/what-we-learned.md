# What we learned

> A companion to the [method writeup](safety-method-writeup.md). That one is *how* the system works. This is *how the thinking changed*: the help-versus-restraint calls we kept re-making while building it, and one honest fact about how far it reached.

## The first instinct was to do more

The early versions tried to be as useful as possible. They took your address, drew a danger zone around the source, and handed back a verdict: SAFE, DOWNWIND, ELEVATED. Translations and a map showing where airborne chemicals were drifting were on the roadmap. Helpfulness, the way we framed it then, meant deciding things for you. The more the tool answered, the more it felt like it was helping.

## The most useful move turned out to be holding back

The failure that mattered was never "the dashboard is sometimes wrong." It was one exact failure: the tool says you're safe, a family that was sheltering goes home, and it wasn't safe. A wrong "you're safe" is a different kind of mistake than a wrong "still dangerous." Once that was clear, the verdict stopped looking like the most helpful feature and started looking like the most dangerous one.

So we deleted it. The address checker, the blast math, the plume, gone. What was left is a conduit: it amplifies what officials say, timestamps it, sources it, and routes every protective-action decision back to the agency that owns the call. It writes no verdict of its own. Restraint wasn't the cautious, lesser version of the product. It was the better one. Every line is now traceable to a source, and no one is being asked to trust a guess. That is the whole project in a sentence. Helping in an emergency meant knowing when to hold back.

## The same call, pointed at the AI

The harder version of that lesson was about where to trust the model. The early ambition was broad: let it do as much as it could. Over the build, the boundary got deliberate instead. The model is genuinely good at the messy, fragile part, searching, reading scattered live-blogs, pulling facts out of noise. It is not something you let near the safety-critical call.

So the line we settled on (recorded as decision [D-003](../DESIGN_LOG.md#d-003-fact-extraction-websearchregex-vs-per-site-scrapers) in the design log, the decision everything else in the code depends on) is: let the model handle the messy, variable work; let plain code handle anything that must produce the same answer every time. The model gathers; plain Python does the comparison work, the corroboration gates, and the final page a resident actually sees. The model never writes that file. Where the AI was trusted did not grow as the work went on. It narrowed on purpose. The AI moved off the safety verdicts and onto the search, the code writing, and the checks where it performs reliably. That last part is literal. An AI assistant helped write the guardrails and the tests that bound it.

## Responsible AI was a consequence, not the goal

None of this began as a deliberate AI-safety project. It began as not wanting to get a neighbor killed. It turned out the moves we made (bound the authority, keep a person on the safety calls, fail visibly stale rather than confidently wrong) line up closely with published responsible-AI guidance, Anthropic's among it. That overlap is a useful confirmation. It was never the headline. The headline was always the family refreshing the page at 2 a.m.

## How far it actually reached

The honest part. This was never used at scale. The two of us who built it were essentially the people who used it. It went up downwind of a real emergency, under real time pressure, and it stayed a small thing, not a service that informed a city. The worth here isn't a usage number we don't have. It is that the reasoning is written down, the boundary is enforced in code rather than promised in a prompt, and the limits are stated plainly instead of hidden. The incident resolved, so the dashboard is frozen as an archive of those decisions. If there is anything to take from it, it is the method and the honesty, not the reach.

---

*Built downwind of the May 2026 Garden Grove methyl-methacrylate evacuation by two local volunteers, with an AI assistant on the code. The frozen archive is kept out of search-engine results (`noindex`) permanently by choice. Attorney review was judged unnecessary once the incident resolved. This is a writeup of the build, not the launch of a public service.*
