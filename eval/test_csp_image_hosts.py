"""Guard: every external image host the dashboard requests must be allowed by the CSP
img-src in vercel.json, or prod silently blocks the image (2026-06-01).

The video-thumbnail code builds https://i.ytimg.com/vi/<id>/hqdefault.jpg, but the CSP
img-src only listed img.youtube.com — so all 8 YouTube thumbnails were blocked in
production (the local http.server enforces no CSP headers, so local QA couldn't catch it,
same local-vs-prod blind spot as the .vercelignore footgun). This pins i.ytimg.com into
the policy whenever the code uses it.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"
VERCEL = REPO_ROOT / "vercel.json"


def _img_src():
    m = re.search(r"img-src([^;\"]*)", VERCEL.read_text(encoding="utf-8"))
    return (m.group(1) if m else "").strip()


def test_youtube_thumbnail_host_allowed_by_csp():
    uses_ytimg = "i.ytimg.com" in DASHBOARD.read_text(encoding="utf-8")
    imgsrc = _img_src()
    allowed = "i.ytimg.com" in imgsrc
    return {"passed": (not uses_ytimg) or allowed,
            "details": f"code_uses_ytimg={uses_ytimg} csp_allows_ytimg={allowed} | img-src=[{imgsrc}]"}
