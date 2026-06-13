# The Conduit Pattern

How GG Tank Watch differs from existing emergency information tools, and why the information-conduit pattern is the right safety posture for a volunteer tool with AI in the loop.

## Landscape

### Official channels

**Ready.gov / FEMA / state emergency portals.** Authoritative, comprehensive, slow to update for a localized incident. During the Garden Grove tank emergency, ggcity.org/emergency was the canonical source but updated in bulk (PDF-style statements), not in the real-time feed format residents were checking for. A resident refreshing the page at 2 AM got the same statement from 6 PM.

**Genasys / Zonehaven.** Official evacuation zone lookup. Authoritative for "am I in the zone?" but offers no context (why, what's happening now, what changed). A resident can confirm they're inside the zone but can't learn that the BLEVE threat was eliminated this morning.

**AlertOC / WEA.** Push alerts for major events. Coverage is binary (alert or no alert), not graduated. A resident who received the initial evacuation alert gets no follow-up about changing conditions unless a new WEA fires.

### Volunteer / community tools

**Watch Duty.** Wildfire-focused, crowdsourced from scanner feeds and CAL FIRE data. Best-in-class for California wildfires. Not designed for chemical incidents; no evacuation-zone polygon overlay; no structured provenance tracking. Watch Duty's editorial policy (scanner-sourced, not AI-summarized) makes different tradeoffs than ours.

**Citizen / Neighbors.** Crowdsourced incident reports. High volume, low signal-to-noise. No provenance validation, no corroboration gates, no structured severity model. Reports are user-submitted, not source-verified.

**PulsePoint / Scanner feeds.** Real-time first-responder dispatch data. Useful for firefighters and scanner enthusiasts, not for a resident asking "should I worry?" Information is raw (unit numbers, codes), not contextualized.

### News outlets

**ABC7 / KTLA / NBC LA live blogs.** Closest to what residents actually want: a reverse-chronological feed of verified updates with source attribution. But: (1) buried under ads and autoplay video, (2) mixed with editorial/opinion, (3) no structured data (no machine-readable severity, no polygon overlay, no address checker), (4) no bilingual support for Little Saigon's Vietnamese-speaking residents.

## What GG Tank Watch does differently

| Dimension | Official channels | News outlets | Volunteer tools | GG Tank Watch |
|-----------|-------------------|--------------|-----------------|---------------|
| Update cadence | Bulk statements | Live blog (manual) | Real-time (crowdsourced) | Every 30 min (AI-compiled, human-checked) |
| Source verification | Authoritative by definition | Editorial standards | Crowdsourced, unverified | Automated provenance validation (P0-2) |
| All-clear relay safety | N/A (they are the authority) | Editorial judgment | None | Corroboration gate (P0-1): ≥2 sources, ≥1 official |
| Freshness honesty | Timestamp on statement | Timestamp on post | None | Two-timestamp system (write age vs. data age, P0-3) |
| Address-level context | Zonehaven zone lookup | None | None | Geocode → official-zone router (defers to officials) |
| Bilingual | Varies by agency | English only | English only | English now; Vietnamese drafted but held pending fluent-native verification (G1) |
| AI transparency | N/A | N/A | N/A | Persistent disclosure on every page |
| Structured severity | N/A | None | Crowdsourced estimate | Derived from facts (computed, not extracted from LLM) |

## Why the conduit pattern

The critical design question: when you put an LLM between official emergency sources and scared residents, what role should it play?

**Option A: Authority.** The tool authors its own safety verdicts. "You are in the blast zone. Evacuate immediately." This is what GG Tank Watch did initially (v0.1-v0.7): geocode → blast-radius computation → personal hazard verdict (ELEVATED / DOWNWIND / safe).

**Problems with Option A:**
- **Liability.** Authoring a safety directive creates §552 "intended reliance," if the verdict is wrong, the tool is liable for the harm. No volunteer immunity statute covers this.
- **Authority creep.** A confident AI verdict competes with the official source. A resident who sees "SAFE" on the dashboard may not check ggcity.org/emergency.
- **LLM failure mode.** The model hallucinates an all-clear → the dashboard says "safe" → a family stops evacuating. This is F1, the catastrophic failure mode.

**Option B: Conduit.** The tool amplifies, translates, and routes official information. It never says "you should": it says "officials say X; confirm at the official source." The LLM summarizes; the controls ensure it can't fabricate or downgrade without corroboration; the UI always points to the official channel.

**Why Option B is correct:**
- **Helping the most people and minimizing liability are the same lane.** The conduit pattern makes the tool more trustworthy (every statement is sourced), more useful (residents can check their address against the official zone), and less dangerous (a hallucination can't produce a false all-clear).
- **The alignment tax is zero.** Safety constraints didn't make the product worse, they made it better. Removing the authored verdict and adding source attribution improved both user trust and legal standing.
- **The safety properties are testable.** "No authored directives" is grep-checkable. "No fabricated sources" has 3 automated tests. "No single-source all-clear" has 2. You can't write an automated test for "the verdict is correct." You can write one for "the system never exceeds its authority."

## Connection to Anthropic's approach

Anthropic's core insight is that AI systems should be helpful, harmless, and honest, and that these properties are complementary, not competing.

GG Tank Watch is a worked example of this insight applied to a real deployment:

- **Helpful:** Residents get a single-page dashboard with structured severity, source-attributed statements, bilingual access, and an address checker, answering "should I worry?" without making them parse 8 news tabs.
- **Harmless:** The system cannot exceed its authority. Corroboration gates, provenance validation, and the conduit pattern ensure that even when the LLM hallucinates, the hallucination cannot reach users as a safety directive.
- **Honest:** AI involvement is disclosed. Source attribution is mandatory. Freshness is honest (data age, not write age). The dashboard says "this address appears to fall within the area officials have described as evacuated," not "you are in danger."

The three are complementary: the safety constraints (harmless) made the product more trustworthy (honest), which made it more useful (helpful). No tradeoff was required.
