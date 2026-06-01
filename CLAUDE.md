# GG Tank Watch — Project Instructions

## Portfolio Framing

This project is a **frozen historical archive of a resolved May 2026 emergency that demonstrates responsible AI deployment in a safety-critical domain**, built for the Anthropic Fellows Program portfolio (rolling, May/July 2026 cohorts).

The thesis: responsible AI and helpful AI are the same lane. GG Tank Watch was built to serve ~50,000 evacuated residents during a real chemical emergency by amplifying official information — and every design choice demonstrates an Anthropic safety principle in production, not in theory. It is now a frozen historical archive of that resolved incident.

## Anthropic Safety Principles (BINDING — governs all decisions)

| Principle | How this project demonstrates it | Evidence |
|-----------|----------------------------------|----------|
| **Honesty / AI transparency** | Persistent disclosure: "compiled with AI assistance, checked by a person" | T3, `disclosure.ai` string |
| **Avoiding harm** | Information conduit only — routes to officials, authors NO directives. The §552/§230 line is explicitly load-bearing | T1 router, Code of Conduct |
| **Human oversight** | Human reviews all AI summaries pre-publish. The app ships English only; safety copy is never surfaced in a language we can't reliably verify (G1) — LEP residents are routed to officials, who publish their own verified translations | Pipeline design, LANGUAGE_ACCESS.md, eval/test_language_access.py |
| **Scalable oversight** | 48-test eval harness monitors behavioral properties incl. a G1 language-access gate. Provenance tests prevent fabricated sources. Corroboration gate on danger downgrades | eval/ harness, test_provenance.py, test_language_access.py |
| **Responsible deployment** | Attorney review gates public launch. Entity + insurance required. `noindex` until cleared | Lane B, DISTRIBUTION.md |
| **Alignment tax = zero** | Safety constraints made the product better (more trustworthy, more useful to scared residents), not worse | Conduit > verdict design |

## Why this matters for the fellowship

Anthropic's research priorities include scalable oversight and AI control. This project is a worked example of:
- **Scalable oversight applied to a consumer-facing AI system** — automated behavioral tests that catch when the system drifts from its safety contract (fabricated sources, authored directives, stale data presented as fresh)
- **AI control in deployment** — the system cannot exceed its authority (route to officials only), enforced by code structure + eval, not by prompting alone
- **Empirical safety thinking** — every safety property has a test that fails before the property is violated, not after

## Technical

- **Stack:** Single-file static dashboard (`dashboard.html`), Python data pipeline (`scripts/`), pytest-style eval harness (`eval/`), Vercel static hosting.
- **Eval:** `python eval/run_all.py --skip integration` — verify by exit code/scorecard. NEVER use `--quiet` to verify (suppresses `[FAIL]` lines).
- **Data refresh:** `scripts/refresh_local.py` pushes to CURRENT branch. Verify `git branch --show-current` == main first.
- **Deploy:** Auto-deploys `main` to Vercel. `noindex` ON until Lane B3 (attorney) clears.
- **Branch workflow:** Branch → PR → merge. Never push main directly.

## Constraints

- **G1:** No non-English safety copy. English-only by design — never surface a translation (even a link framed as ours) without reliable human verification; route LEP residents to officials.
- **No directives:** Never tell anyone to evacuate or take action. Route to officials.
- **No new deps without approval.**
- **Attorney review blocks launch:** Do not remove `noindex` until B3 clears.

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool.

- Product ideas/brainstorming → /office-hours
- Strategy/scope → /plan-ceo-review
- Architecture → /plan-eng-review
- Bugs/errors → /investigate
- QA/testing → /qa or /qa-only
- Code review → /review
- Ship/deploy/PR → /ship or /land-and-deploy
- Save progress → /context-save
- Resume context → /context-restore
