# Contributing to GG Tank Watch

GG Tank Watch is a volunteer-built information conduit for residents affected by the Garden Grove chemical-tank emergency. We amplify, translate, and route official information — we never author safety directives or substitute for official channels.

Before contributing, read the [Information Conduit Code of Conduct](CODE_OF_CONDUCT.md).

## Core constraint: conduit, not authority

Every piece of content must trace to a named, verifiable source. Contributors must never:

- Tell anyone to evacuate, shelter in place, or take any specific safety action
- Add commentary, speculation, or opinion about what might happen
- Publish unattributed claims or social-media rumors
- Downgrade danger levels without corroboration from at least two sources including one official agency

The distinction between "you should leave" and "officials say the evacuation zone includes your area — confirm at ggcity.org/emergency" is load-bearing.

## Branch workflow

1. Create a feature branch from `main`
2. Make your changes
3. Open a pull request
4. Merge after review

Never push directly to `main`.

## Eval harness

The project maintains a behavioral eval harness in `eval/`. Before any PR can merge:

```
python eval/run_all.py --skip integration
```

All tests must pass (currently 210/210 via `python eval/run_all.py --skip integration`). The harness checks safety-critical properties: no fabricated sources, no authored directives, no stale data presented as fresh, provenance on every claim.

## Translation constraint (G1)

Safety-critical copy must never be machine-translated. English is the fallback until a native speaker verifies each translation. Translations link to the original English source and are marked unofficial.

## Data pipeline

The refresh pipeline lives in `scripts/`. `refresh_local.py` pulls from official and news sources, applies the AI summarization pipeline (with human review), and writes `status.json`. The dashboard reads this file client-side.

AI-generated summaries carry a persistent disclosure: "compiled with AI assistance, checked by a person."

## What to work on

- **Dashboard UI** — `dashboard.html` (single-file static app)
- **Data pipeline** — `scripts/` (Python)
- **Eval tests** — `eval/` (pytest-style)
- **Documentation** — `docs/`

## Questions

Open an issue in the repository's issue tracker.
