"""Safety guard: the dashboard must not link to an air-quality tool.

EPA AirNow / airnowapi.org report particulate-matter and ozone AQI, NOT the
methyl methacrylate (MMA) vapor from this tank leak. Surfacing an air-quality
"official source" link creates false reassurance that the air is safe when the
specific vapor hazard is unmonitored. The link was removed 2026-05-30; this
guard prevents it silently returning (e.g. if the writer's dormant
fetch_air_quality path or the i18n key is re-wired).

Scope note: this bans the air-quality LINK/key remnants, not the phrase
"air quality" — an official statement routed through the conduit may legitimately
mention air-quality readings, and that descriptive routing is allowed.
"""

CATEGORY = "behavioral"


def test_no_air_quality_link():
    html = open("public/dashboard.html", encoding="utf-8").read().lower()
    banned = ["airnow.gov", "airnowapi.org", "info.official.airnow"]
    found = [b for b in banned if b in html]
    assert not found, f"air-quality link/remnant still in dashboard.html: {found}"
