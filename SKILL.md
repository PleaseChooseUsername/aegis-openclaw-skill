---
name: aegis
description: "Automated Emergency Geopolitical Intelligence System — real-time threat monitoring and safety alerts for civilians in conflict zones. Use when: (1) setting up warzone/crisis safety monitoring for a location, (2) user asks about security situation or threat level, (3) configuring emergency alert delivery, (4) generating security briefings, (5) emergency preparedness planning. Requires: curl, python3. Optional: NewsAPI key for enhanced coverage."
---

# AEGIS — Automated Emergency Geopolitical Intelligence System

Provides location-aware threat intelligence and safety alerts for civilians in conflict zones. Official sources first, reputable media second. Anti-hoax verified. Multi-language.

**Not a panic tool.** Realistic, honest, follows official government guidance.

## Quick Start

### First-time setup (interactive)
```bash
python3 scripts/aegis_onboard.py
```
This creates `~/.openclaw/aegis-config.json` with location, language, alert preferences.

### Manual config
Create `~/.openclaw/aegis-config.json`:
```json
{
  "location": { "country": "AE", "city": "Dubai", "timezone": "Asia/Dubai" },
  "language": "en",
  "alerts": { "critical_instant": true, "high_batch_minutes": 30, "medium_digest_hours": 6 },
  "briefings": { "morning": "07:00", "evening": "22:00" },
  "scan_interval_minutes": 15,
  "api_keys": {}
}
```

### Run a scan
```bash
python3 scripts/aegis_scanner.py
```

### Set up cron monitoring
```
openclaw cron add --expr "*/15 * * * *" --message "Run AEGIS scan: python3 <skill-dir>/scripts/aegis_scanner.py --cron"
openclaw cron add --expr "0 3 * * *" --message "Generate AEGIS morning briefing: python3 <skill-dir>/scripts/aegis_briefing.py morning"
openclaw cron add --expr "0 18 * * *" --message "Generate AEGIS evening briefing: python3 <skill-dir>/scripts/aegis_briefing.py evening"
```
Adjust cron times to match user's timezone (times above are UTC examples).

## How It Works

### Source Hierarchy (Trust Tiers)
0. **Government emergency systems** — NCEMA, FEMA, civil defense (highest trust)
1. **Primary news RSS** — Reuters, Al Jazeera, BBC, AP (high trust, free RSS)
2. **Aviation/infrastructure** — NOTAMs, airport status (specialized)
3. **Analysis/OSINT** — Crisis Group, ACLED, War on the Rocks (medium trust)
4. **Enhanced (optional API)** — NewsAPI, GDELT (requires key)

### Scan Cycle
1. Fetch all sources for user's location → RSS parse + web scrape
2. Deduplicate against 48h rolling hash window
3. Pattern-match threat keywords (multi-language)
4. LLM analysis: cross-reference, verify credibility, classify, generate action items
5. Route through tiered delivery (🔴 instant / 🟠 batched / ℹ️ digest)

### Anti-Hoax Protocol
- Tier 0-1 sources: alert directly
- Tier 2+: require corroboration from ≥1 Tier 0-1 source
- Social media/unverified: DO NOT alert, log for review
- Extraordinary claims: require ≥3 independent sources
- Contradicts official statements: flag discrepancy, defer to official

## Alert Tiers

🔴 **CRITICAL** — Immediate threat to life. Instant push. Includes official guidance + actions.
🟠 **HIGH** — Significant development. Batched every 30min. Includes impact assessment.
ℹ️ **MEDIUM** — Situational awareness. Hourly/daily digest. Background context.

## Briefings

Morning and evening briefings include:
- Overall threat level with trend (↑↗→↘↓)
- Key developments since last briefing
- Official government status (airports, schools, gov services)
- Preparedness checklist
- Source links

## Country Profiles

Each supported country has a profile in `references/country-profiles/`. Profiles contain:
- Emergency agency info and hotlines
- Embassy contacts (US, UK, general)
- Location-specific news sources
- Shelter and evacuation info
- Local threat keyword patterns

To add a new country: copy `references/country-profiles/_template.json`, fill in details, submit PR.

## Preparedness Resources

See `references/preparedness/` for:
- `go-bag-checklist.md` — What to pack
- `communication-plan.md` — Family communication plan
- `shelter-guidance.md` — Shelter-in-place guidance
- `evacuation-guidance.md` — When and how to evacuate

## Configuration Reference

See `references/config-reference.md` for all configuration options.

## Cost

- **Baseline (no API keys):** ~$0.03-0.05/day in LLM tokens (or FREE with Copilot/local models)
- **With NewsAPI:** Free tier (100 req/day) is sufficient
- **RSS/web scraping:** Always free

## Adding Sources

Edit `references/source-registry.json` to add/remove sources. Each source needs:
- `name`, `url`, `type` (rss|web|api), `tier` (0-4), `countries` (ISO codes or "global")
- `parser` specification for extraction
