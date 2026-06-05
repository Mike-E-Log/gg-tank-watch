# GG Tank Watch — Project Instructions

## What this is

A frozen historical archive of a resolved May 2026 methyl-methacrylate chemical-tank emergency in Garden Grove, California. During the incident it served ~50,000 evacuated residents by amplifying official information; it is a pure information conduit that routes to officials and authors no directives of its own. It is now frozen — no longer updated.

The organizing principle: responsible and helpful are the same lane. Every safety constraint here made the product more trustworthy and more useful to scared residents, not less. These principles map to widely published responsible-AI guidance (including Anthropic's).

## Safety principles (BINDING — govern all decisions)

| Principle | How this project applies it | Evidence |
|-----------|----------------------------------|----------|
| **Honesty / transparency** | Persistent disclosure: "compiled with AI assistance, checked by a person" | disclosure string, eval guards |
| **Avoiding harm** | Information conduit only — routes to officials, authors NO directives. The §552/§230 line is load-bearing | `scripts/update_status.py`, `docs/CODE_OF_CONDUCT.md` |
| **Human oversight** | A person reviews all AI summaries pre-publish. English-only; safety copy is never surfaced in a language we can't reliably verify (G1); LEP residents are routed to officials | `docs/LANGUAGE_ACCESS.md`, `eval/test_language_access.py` |
| **Scalable oversight** | A 210-test eval harness monitors behavioral properties incl. the G1 language gate, provenance (no fabricated sources), and the corroboration gate on danger downgrades | `eval/` harness, `test_provenance.py`, `test_language_access.py` |
| **Responsible deployment** | Attorney review gates public launch; entity + insurance required; `noindex` until cleared | `vercel.json`, `robots.txt` |
| **Alignment tax = zero** | Safety constraints made the product better (more trustworthy, more useful), not worse | conduit > verdict design |

## Constraints

- **G1:** No non-English safety copy. English-only by design — never surface a translation (even a link framed as ours) without reliable human verification; route LEP residents to officials.
- **No directives:** never tell anyone to evacuate or take action. Route to officials.
- **No new deps without approval.**
- **Attorney review blocks launch:** do not remove `noindex` until attorney review clears.

## Technical

- **Stack:** single-file static dashboard (`dashboard.html`), Python stdlib data pipeline (`scripts/`), pytest-style eval harness (`eval/`), Vercel static hosting.
- **Eval:** `python eval/run_all.py --skip integration` — verify by exit code/scorecard. Do not use `--quiet` to verify (it suppresses `[FAIL]` lines).
- **Data:** the pipeline is frozen/retired; the archive is no longer updated.
- **Branch workflow:** branch → PR → merge. Never push `main` directly.
