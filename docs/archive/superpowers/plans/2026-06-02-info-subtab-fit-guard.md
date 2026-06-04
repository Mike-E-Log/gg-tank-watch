# Info Sub-tab Fit Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic eval guard that fails if the Info-tab sub-tab bar could overflow its single row (the #108 regression class), and harden the CSS so equal-width flex is provably overflow-proof — no browser, no new dependency.

**Architecture:** The #108 failure was a *specific anti-pattern* — a 6-tab `overflow-x:auto` scrollable bar that clipped "Recovery"/hid "About" at 375px. The #109 fix made the bar `flex: 1 1 0` (equal-width), which partitions the row and cannot wrap. Equal-width flex still needs `min-width: 0` to be overflow-proof for any label length (flex items default to `min-width:auto`). We add `min-width: 0` and assert the full invariant (no scroll/wrap pattern; `flex:1 1 0` + `min-width:0`; ≤4 tabs) as a static-text Python test in the existing harness. This is causally sufficient to prevent the regression, runs in `run_all.py --skip integration`, and is fully deterministic.

**Tech Stack:** Python (stdlib `re`, `pathlib`) in the existing `eval/` harness; CSS in `dashboard.html`; `sw.js` cache version.

---

### Task 1: Add the fit-invariant guard (TDD) + CSS hardening

**Files:**
- Create: `eval/test_info_subtab_fit.py`
- Modify: `dashboard.html:905-911` (the `.info-subtab` CSS rule)
- Modify: `sw.js:1` (CACHE_NAME bump)
- Modify: `CHANGELOG.md` (one line)

- [ ] **Step 1: Write the failing test**

Create `eval/test_info_subtab_fit.py`:

```python
"""Guard: the Info-tab sub-tab bar must be structurally incapable of overflowing
its single row. The #108 regression was a 6-tab `overflow-x:auto` scrollable bar
that clipped "Recovery" and hid "About" at 375px; #109 fixed it with equal-width
`flex:1 1 0`. Equal-width flex partitions the row and cannot wrap, and `min-width:0`
makes it overflow-proof for ANY label length. This asserts that invariant in static
CSS — deterministic, no browser, no new dependency (catches the failure a text-only
string match cannot, by checking the causal layout property rather than pixel values).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "dashboard.html"


def _css_block(selector: str, text: str) -> str:
    """Body of the FIRST `selector { ... }` rule. The trailing `\\s*\\{` guard means
    `.info-subtab` does NOT match `.info-subtabs {`, `.info-subtab:hover {`, or
    `.info-subtab.active {` — only the bare rule."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", text)
    return m.group(1) if m else ""


def test_info_subtabs_bar_not_scrollable():
    """`.info-subtabs` must not use the scrollable/wrapping bar anti-pattern (#108)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _css_block(".info-subtabs", text)
    assert block, ".info-subtabs CSS rule not found"
    banned = ["overflow-x: auto", "overflow-x:auto", "overflow-x: scroll", "overflow-x:scroll",
              "overflow: auto", "overflow:auto", "overflow: scroll", "overflow:scroll",
              "scroll-snap", "flex-wrap: wrap", "flex-wrap:wrap"]
    hit = [b for b in banned if b in block]
    assert not hit, f".info-subtabs uses a scrollable/wrapping bar anti-pattern: {hit}"


def test_info_subtab_is_overflow_proof_equal_width():
    """`.info-subtab` must be equal-width (`flex:1 1 0`) AND `min-width:0` so the bar
    cannot overflow one row regardless of label length."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _css_block(".info-subtab", text)
    assert block, ".info-subtab CSS rule not found"
    assert re.search(r"flex:\s*1\s+1\s+0", block), ".info-subtab must use `flex: 1 1 0` (equal-width)"
    assert re.search(r"min-width:\s*0", block), ".info-subtab must set `min-width: 0` (overflow-proof)"


def test_info_subtab_count_at_most_four():
    """Legibility guard: keep the Info sub-tab bar at <=4 tabs (the 6-tab build #108
    was too cramped at 320-375px). Counts entries in the renderInfoTab TABS array
    (anchored on the `id:"summary"` first entry)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    arr = re.search(r"\[\s*\{\s*id:\s*[\"']summary[\"'].*?\}\s*\]", text, re.S)
    assert arr, "Info TABS array (starting with id:'summary') not found"
    count = len(re.findall(r"\bid:\s*[\"']", arr.group(0)))
    assert 0 < count <= 4, f"Info sub-tabs should be 1..4, found {count}"
```

- [ ] **Step 2: Run the test to verify the right one fails**

Run: `python eval/run_all.py --only test_info_subtab_fit`
Expected: `test_info_subtab_is_overflow_proof_equal_width` **FAILS** ("must set `min-width: 0`"); the other two **PASS**. This proves the guard is not a tautology — it catches the missing hardening on current code.

- [ ] **Step 3: Add the CSS hardening (minimal)**

In `dashboard.html`, the `.info-subtab` rule (line ~905-911) currently begins:
`flex: 1 1 0; text-align: center; white-space: nowrap;`
Add `min-width: 0;` right after `flex: 1 1 0;`:

```css
    .info-subtab {
      flex: 1 1 0; min-width: 0; text-align: center; white-space: nowrap;
      padding: 10px 6px; border: none; background: transparent;
      color: var(--sa-text-2); font-family: inherit; font-size: 13px; font-weight: 600;
      cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
      min-height: 44px; transition: color 0.15s, border-color 0.15s;
    }
```

No visual change for the current four short labels (they already fit equally); the change only affects hypothetical over-long labels.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python eval/run_all.py --only test_info_subtab_fit`
Expected: all 3 PASS.

- [ ] **Step 5: Bump the service-worker cache (dashboard.html changed)**

In `sw.js:1`: `var CACHE_NAME = "gg-tank-v60";` → `var CACHE_NAME = "gg-tank-v61";`

- [ ] **Step 6: Add a CHANGELOG line**

Add under the latest/unreleased section of `CHANGELOG.md`:
`- test(info): guard the sub-tab bar against one-row overflow (flex:1 1 0 + min-width:0 invariant); SW v60->v61`

- [ ] **Step 7: Run the full eval to confirm green**

Run: `python eval/run_all.py --skip integration`
Expected: scorecard shows TOTAL with 0 failed (prior 171 + 3 new = 174 behavioral, exact total may differ). NEVER use `--quiet`. If any pre-existing test pins an exact eval count, update it to the new total.

- [ ] **Step 8: Commit**

```bash
git -C "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-watch" add eval/test_info_subtab_fit.py dashboard.html sw.js CHANGELOG.md
git -C "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-watch" commit -m "test(info): guard sub-tab bar against one-row overflow + min-width:0 hardening"
```

---

## Self-Review

- **Spec coverage:** invariant assertions (#1 no-scroll, #2 flex+min-width, #3 ≤4 tabs) ✓; CSS hardening ✓; SW bump ✓; CHANGELOG ✓; verify-green ✓.
- **Placeholder scan:** none — all code is concrete.
- **Type consistency:** `_css_block` used consistently; regex anchors verified against `dashboard.html:900-911` and `:1994-1999`.

## NOT in scope
- Restyling the Info tab (frozen archive); only a no-visual-change hardening.
- A live-browser pixel test (Playwright) — deliberately rejected to avoid a new dependency + flake; the invariant is causally sufficient for this regression class.
- Browser-in-CI / visual-regression infrastructure.

## Risks
- If a pre-existing test asserts an exact total eval count, Step 7 will flag it — update that count.
- The `min-width: 0` regex also matches `min-width: 0px`/`min-width:0` — intended (any zero form is fine).
