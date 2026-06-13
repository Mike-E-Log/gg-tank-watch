"""Static guard: dashboard.html ships English-only (STRINGS + CSS, not just LANGS).

test_language_access::test_english_only already asserts the LANGS array is
English-only, but unverified Vietnamese STRINGS values and `lang="vi"` CSS
lingered behind a dead `ready:false` gate. English-only is the project's safety
posture (G1) — enforce it for the STRINGS dict and CSS too, so dead VI copy can't
silently creep back. Pure text grep; no JS execution needed.
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"

# Vietnamese-specific diacritics. Kept narrow (these do not occur in the English
# copy or place names used here) to avoid false positives.
VI_DIACRITICS = "ạảấầẩẫậắằẳẵặẹẻẽếềểễệịỉọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹđ"


def test_no_vietnamese_residue():
    text = DASHBOARD.read_text(encoding="utf-8")
    bad = []
    for i, line in enumerate(text.splitlines(), 1):
        ll = line.lower()
        if "vi:" in ll and ("'" in line or '"' in line):
            bad.append((i, "vi: key"))
        elif 'lang="vi"' in ll or "lang='vi'" in ll:
            bad.append((i, "lang=vi"))
        elif any(ch in line for ch in VI_DIACRITICS):
            bad.append((i, "vi diacritics"))
    return {
        "passed": len(bad) == 0,
        "details": "no Vietnamese residue in dashboard.html" if not bad
                   else f"{len(bad)} residue line(s): " + ", ".join(f"L{n}({why})" for n, why in bad[:12]),
        "metrics": {"residue_lines": len(bad)},
    }
