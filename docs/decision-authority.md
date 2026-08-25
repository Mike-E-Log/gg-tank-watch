# Decision authority: the human keeps the final verdict

In an emergency dashboard, the failure that can kill someone is a wrong "all-clear." So the design question that matters most is not how good the model is. It is who is allowed to declare safety, and what stops the model from doing it alone.

This system answers with a hard boundary. The AI is scoped to situational awareness, meaning it pulls scattered updates into one calm view: gathering, corroborating, and surfacing facts. The human keeps the final verdict: the irreversible safety calls, like lifting an evacuation or declaring an incident resolved. The model never owns that decision. Three mechanisms hold the boundary, and the third one is the honest part.

## 1. A safe signal requires corroboration the model can't fabricate

The most dangerous output is a fabricated all-clear: the model emitting `evacuation_lifted: true` or a resolved timestamp from a single source, a hallucination, or an injected page. The system structurally refuses it. The corroboration gate (P0-1) forces a safe default unless at least two sources agree and an official source is present (`test_lifted_requires_corroboration`, `test_resolved_requires_two_sources`). A model that "concludes" the danger is over cannot make that conclusion stick on its own. The verdict is gated, not trusted.

## 2. The human is never shown a confident lie

A person can only hold the verdict if the screen tells the truth about what is known. So the system separates data age from write age, a check the project calls freshness honesty (P0-3): a failed or empty fetch cannot refresh-stamp stale facts as current (`test_empty_facts_do_not_advance_data_as_of`). Every statement carries the source actually retrieved on that run, and fabricated source links are dropped by the provenance check (P0-2). Future-dated and malformed timestamps are cleared out by the timestamp-validity check (P1-1). These gates all serve one goal: the reviewer sees staleness and uncertainty for what they are, not as a clean, confident, wrong answer.

## 3. The human review step is the control for what tests can't catch

The automated tests are strongest where failure is all-or-nothing and dangerous: all-clear vs. not, fabricated vs. real, stale vs. fresh. Six of the twelve ways the system could be deliberately broken are fully caught by automated tests. They are weakest where failure is gradual and subtle, and the method does not pretend otherwise. Three classes rely on the human, not the automated tests:

- **Plausible-but-wrong numerics.** "48,000 evacuees" when the truth is 50,000 passes every test. A check that flags any number dropping by half or more catches gross errors, not subtle ones.
- **Coordinated prompt injection.** An attacker who controls two or more of the sources the pipeline fetches, one faking an official domain, can pass the corroboration gate. Low probability, but the architecture does not structurally prevent it.
- **Gradual tone drift.** A slow shift toward more alarming or more reassuring framing trips no pass/fail test.

For all three, the control is a person reading the output, not a green test suite. Naming them is the method. A system that claimed full automated coverage here would be lying, and a reviewer who trusted that claim would be unguarded exactly where the danger is subtle.

## Why this is the load-bearing choice

The automated test suite confirms the system behaves as designed: 210 of 210 tests pass ([eval summary](eval-summary.json), [red-team analysis](failure-analysis.md)). It does not, and cannot, own the safety verdict. Keeping the human as the final authority is what makes the remaining risks manageable. Every failure the automated suite cannot catch is one a person is positioned to catch, because the system surfaces uncertainty to that person instead of papering over it. The AI makes the reviewer faster and better informed. It does not get the last word.
