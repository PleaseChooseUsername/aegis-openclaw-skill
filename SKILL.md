---
name: aegis
description: "Automated Emergency Geopolitical Intelligence System — real-time threat monitoring and safety alerts for civilians in conflict zones. Use when: (1) setting up warzone/crisis safety monitoring for a location, (2) user asks about security situation or threat level, (3) configuring emergency alert delivery, (4) generating security briefings, (5) emergency preparedness planning."
homepage: "https://github.com/PleaseChooseUsername/aegis-openclaw-skill"
source: "https://github.com/PleaseChooseUsername/aegis-openclaw-skill"
requires:
  binaries:
    - curl
    - python3
  env: []
  optional_env:
    - AEGIS_DATA_DIR
    - AEGIS_BOT_TOKEN
    - AEGIS_CHANNEL_ID
  optional_config:
    - "api_keys.newsapi"
---

# AEGIS — Automated Emergency Geopolitical Intelligence System

Provides location-aware threat intelligence and safety alerts for civilians in conflict zones. Monitors 23+ sources (RSS, web scraping, JSON APIs) every 15 minutes. Official sources first, reputable media second. Anti-hoax verified. Multi-language (EN + AR keywords).

**Not a panic tool.** Realistic, honest, follows official government guidance.

## Requirements

- **curl** — used for all HTTP fetching (RSS, web, APIs). Pre-installed on most systems.
- **python3** (3.8+) — runs all scripts. No extra pip packages needed (stdlib only).
- **No API keys required** for baseline 23 sources. Optional: NewsAPI free tier for expanded coverage.

## Quick Start

### First-time setup (interactive)
```bash
python3 scripts/aegis_onboard.py
```
Creates `~/.openclaw/aegis-config.json` with location, language, and alert preferences.

### Manual config
Create `~/.openclaw/aegis-config.json`:
```json
{
  "location": {
    "country": "AE",
    "country_code": "AE",
    "city": "Dubai",
    "timezone": "Asia/Dubai"
  },
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

### Optional: Telegram channel delivery
Set environment variables for direct channel posting:
- `AEGIS_BOT_TOKEN` — Telegram bot token (from BotFather)
- `AEGIS_CHANNEL_ID` — Telegram channel ID

Or add to config:
```json
{
  "telegram": {
    "bot_token": "your-token",
    "channel_id": "-100xxxxxxxxxx"
  }
}
```

## Data Storage

AEGIS stores scan state in `~/.openclaw/aegis-data/` (or `$AEGIS_DATA_DIR` if set):
- `seen_hashes.json` — SHA-256 dedup hashes (48h rolling window)
- `pending_alerts.json` — alerts awaiting batch delivery
- `scan_log.json` — recent scan results
- `last_scan.json` — most recent scan output (used by briefings)

All files are local JSON. No data is sent to external servers beyond the listed sources in `source-registry.json`.

## Sources (23+)

All sources are defined in `references/source-registry.json`. The scanner **only** contacts URLs listed there.

| Tier | Type | Count | Examples |
|------|------|-------|----------|
| 0 🏛️ | Government & Emergency | 6 | GDACS, NCEMA, US/UK embassies, MOFAIC |
| 1 📰 | Major News Agencies | 8 | Al Jazeera, Reuters, BBC, France24, The National |
| 2 🔍 | OSINT & Conflict Mapping | 4 | World Monitor API, LiveUAMap (3 regions) |
| 2 ✈️ | Aviation | 2 | FAA NOTAMs (DXB, AUH) |
| 3 📋 | Analysis | 2 | Crisis Group, War on the Rocks |
| 4 🔑 | API-Enhanced (optional) | 1+ | NewsAPI (free tier), GDELT |

### Outbound connections

The scanner contacts **only**:
1. URLs listed in `references/source-registry.json` (RSS feeds, news sites, government pages)
2. `https://world-monitor.com/api/signal-markers` (World Monitor public API)
3. LiveUAMap regional pages (e.g., `https://iran.liveuamap.com`)
4. Telegram Bot API (`https://api.telegram.org/bot.../sendMessage`) — only if channel delivery is configured

No telemetry. No analytics. No phone-home.

## Alert Classification

| Level | Meaning | Trigger |
|-------|---------|---------|
| 🔴 CRITICAL | Immediate physical danger **in user's country** | Missiles inbound, sirens, shelter orders, airport shutdown, CBRN |
| 🟠 HIGH | Significant regional threat | Attacks on neighbors, strait disrupted, flights cancelled |
| ℹ️ MEDIUM | Situational awareness | Regional strikes, diplomacy, oil prices, sanctions |

CRITICAL is reserved for "act now, your life may be in danger." Regional developments are HIGH.

### Anti-Hoax Protocol
- Tier 0-1 sources: can trigger alerts directly
- Tier 2+: require corroboration from ≥1 Tier 0-1 source
- Social media: excluded entirely
- Extraordinary claims: require ≥3 independent sources

## Briefings

Morning and evening briefings include:
- Threat level with trend indicator
- Key developments since last briefing
- Source attribution and verification status
- Standing preparedness guidance

## Country Profiles

Each supported country has a profile in `references/country-profiles/`. Profiles contain:
- Emergency contacts and hotlines
- Neighboring countries and regions of interest (for source filtering)
- Local threat keyword patterns
- Shelter and evacuation info

Currently available: **UAE** (`uae.json`). To add a country: copy `_template.json`, fill in details, submit PR.

## Preparedness Resources

See `references/preparedness/` for:
- `go-bag-checklist.md` — What to pack for emergency evacuation
- `communication-plan.md` — Family communication plan
- `shelter-guidance.md` — Shelter-in-place protocol
- `evacuation-guidance.md` — Routes, transport, embassy registration

## Configuration Reference

See `references/config-reference.md` for all configuration options.

## Cost

- **Baseline (no API keys):** FREE with Copilot or local models; ~$0.03-0.05/day with commercial LLMs
- **All 23 sources:** Free (RSS + web scraping + public APIs)
- **Optional NewsAPI:** Free tier (100 req/day) is sufficient
