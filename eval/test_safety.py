"""Conduit-principle tests for dashboard.html.

Verifies the dashboard does not contain authored hazard verdicts
and routes users to official sources.
"""

CATEGORY = "behavioral"


def test_no_authored_hazard_verdict():
    html = open("dashboard.html", encoding="utf-8").read()
    banned = ["within injury radius or plume", "blast_zones_mi", "layers.plume", "ELEVATED — within injury radius"]
    found = [b for b in banned if b in html]
    assert not found, f"authored-hazard remnants still present: {found}"


def test_checker_routes_to_official():
    html = open("dashboard.html", encoding="utf-8").read()
    assert "ggcity.org/emergency" in html, "dashboard must route to official source"
