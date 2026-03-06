# AEGIS — Automated Emergency Geopolitical Intelligence System

<div align="center">

**Real-time threat intelligence for civilians in conflict zones.**

*Know what's happening. Know what to do. Stay safe.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-aegis@1.4.0-orange.svg)](https://clawhub.com)

</div>

---

## What is AEGIS?

AEGIS is an open-source [OpenClaw](https://openclaw.ai) skill that monitors 23+ news and intelligence sources every 15 minutes and delivers actionable threat assessments to your preferred messaging channel.

**Built during the 2026 Iran-US conflict** by a civilian in Dubai who needed better situational awareness than news apps could provide.

### What It Does

- 🔴 **Instant critical alerts** — only for immediate physical danger (missiles inbound, shelter orders, airport shutdowns)
- 📊 **Twice-daily briefings** — morning & evening situation reports with threat level and trend analysis
- 🌍 **Location-aware** — filters 23+ sources for YOUR country and neighboring region
- 🛡️ **Anti-hoax protocol** — official government sources first, verified media second, social media excluded
- 🌐 **Multi-language** — keyword detection in English and Arabic; briefings in your language
- 📱 **Channel-agnostic** — Telegram, WhatsApp, Discord, Signal, or any OpenClaw channel
- 💰 **Free baseline** — zero API keys needed for all 23 core sources

### What It Is NOT

- Not a panic tool — factual, follows official government guidance
- Not social media aggregation — no Twitter/X, no unverified rumors
- Not a replacement for official emergency systems — it's the intelligence layer above them

---

## Sources (23+)

AEGIS aggregates from multiple source tiers:

| Tier | Type | Sources | Examples |
|------|------|---------|----------|
| 0 🏛️ | Government & Emergency | 6 | GDACS, NCEMA, US/UK embassies, MOFAIC |
| 1 📰 | Major News Agencies | 8 | Al Jazeera, Reuters, BBC, France24, The National |
| 2 🔍 | OSINT & Conflict Mapping | 4 | World Monitor (168 geolocated zones), LiveUAMap (3 regions) |
| 2 ✈️ | Aviation | 2 | FAA NOTAMs (DXB, AUH) |
| 3 📋 | Analysis | 2 | Crisis Group, War on the Rocks |
| 4 🔑 | API-Enhanced (optional) | 1+ | NewsAPI (free tier), GDELT |

**All sources are free.** No API keys required for the baseline 23 sources. The scanner uses `curl` — no extra Python packages needed.

### Source Verification

| Source Tier | Trust Level | Alert Behavior |
|-------------|-------------|----------------|
| Tier 0-1 | Verified | Can trigger alerts directly |
| Tier 2 | Domain-trusted | Trusted within their domain; requires context |
| Tier 3+ | Corroboration needed | Must be confirmed by Tier 0-1 source |
| Social media | Excluded | Not included. Period. |

---

## Alert Classification

| Level | Meaning | Channel Behavior |
|-------|---------|-----------------|
| 🔴 CRITICAL | Immediate physical danger **in your country** — missiles inbound, sirens, shelter/evacuation orders, airport shutdown, CBRN | **Instant push + pin** |
| 🟠 HIGH | Significant regional threat — attacks on neighbors, strait disrupted, flights cancelled, military buildup | **Included in briefings** |
| ℹ️ MEDIUM | Situational awareness — regional strikes, diplomacy, oil prices, sanctions, cyber | **Included in briefings** |

CRITICAL is reserved for "act now" situations. Regional developments (neighboring countries under attack, Hormuz disruptions, economic impacts) are HIGH — important context, but not "run to shelter."

---

## Quick Start

### 1. Install

```bash
# Via ClawHub:
clawhub install aegis

# Or manually:
git clone https://github.com/PleaseChooseUsername/aegis-openclaw-skill.git
cp -r aegis-openclaw-skill/ ~/.openclaw/skills/aegis/
```

### 2. Configure

Tell your OpenClaw agent:
> "Set up AEGIS for my location"

Or run directly:
```bash
python3 ~/.openclaw/skills/aegis/scripts/aegis_onboard.py
```

Creates `~/.openclaw/aegis-config.json` with your location, language, and preferences.

### 3. First Scan

```bash
python3 ~/.openclaw/skills/aegis/scripts/aegis_scanner.py
```

### 4. Automated Monitoring

Tell your agent:
> "Set up AEGIS cron jobs — scan every 15 minutes, morning and evening briefings"

This creates three cron jobs:
- **Every 15 min**: silent background scan, posts only on CRITICAL
- **Morning**: situation report with overnight developments
- **Evening**: end-of-day summary with threat trend

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    AEGIS                         │
│                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  23+      │    │ CLASSIFY │    │ DELIVER  │  │
│  │  SOURCES  │───▶│ + DEDUP  │───▶│ + BRIEF  │  │
│  └──────────┘    └──────────┘    └──────────┘  │
│       │                │               │        │
│  RSS + Web +      SHA-256 dedup    Telegram     │
│  JSON APIs       Keyword match     or any       │
│  Zero cost       Anti-hoax tier    channel      │
└─────────────────────────────────────────────────┘
```

**Deduplication**: SHA-256 content hashing with 48-hour sliding window prevents repeat alerts.

**Keyword matching**: Regex patterns in English and Arabic, tiered by severity. Location-specific patterns ensure "attack on Kuwait" ≠ CRITICAL for a UAE user (it's HIGH).

---

## Supported Countries

AEGIS works for **any country** — global sources (GDACS, BBC, Al Jazeera, World Monitor) cover everywhere.

### Countries with Dedicated Profiles

| Country | Code | Emergency Contacts | Evacuation Routes | Shelter Guidance |
|---------|------|-------------------|-------------------|-----------------|
| 🇦🇪 UAE | `AE` | ✅ | ✅ | ✅ |

**Want your country added?** Copy `references/country-profiles/_template.json`, fill in your country's details, and submit a PR.

---

## Preparedness Resources

Included in the skill (available to your agent during briefings):

- **[Go-Bag Checklist](references/preparedness/go-bag-checklist.md)** — leave in 2 minutes
- **[Communication Plan](references/preparedness/communication-plan.md)** — stay connected when networks fail
- **[Shelter Guidance](references/preparedness/shelter-guidance.md)** — where to go, what to do
- **[Evacuation Guidance](references/preparedness/evacuation-guidance.md)** — routes, transport, embassy registration

---

## Requirements

- **OpenClaw** (any recent version)
- **Python 3.8+**
- **curl** (pre-installed on virtually all systems)
- No additional Python packages

**LLM cost**: With GitHub Copilot (included in dev subscriptions), effectively free. With OpenRouter or other providers, ~$0.03-0.05/day.

---

## Configuration

Minimal config (`~/.openclaw/aegis-config.json`):
```json
{
  "location": {
    "country": "AE",
    "country_code": "AE",
    "city": "Dubai",
    "timezone": "Asia/Dubai"
  },
  "language": "en",
  "scan_interval_minutes": 15
}
```

See [config-reference.md](references/config-reference.md) for full schema.

---

## Skill Structure

```
aegis/
├── SKILL.md                              # OpenClaw skill definition
├── scripts/
│   ├── aegis_scanner.py                  # Core scanner (23+ sources)
│   ├── aegis_onboard.py                  # Interactive setup wizard
│   ├── aegis_briefing.py                 # Briefing generator
│   ├── aegis_cron.py                     # Silent cron runner
│   └── aegis_channel.py                  # Channel publisher (Telegram)
└── references/
    ├── source-registry.json              # 23 verified sources
    ├── threat-keywords.json              # EN + AR patterns (v2.0)
    ├── config-reference.md               # Full config docs
    ├── country-profiles/
    │   ├── uae.json                      # UAE emergency profile
    │   └── _template.json                # Template for contributions
    ├── preparedness/
    │   ├── go-bag-checklist.md
    │   ├── communication-plan.md
    │   ├── shelter-guidance.md
    │   └── evacuation-guidance.md
    └── prompts/
        └── analysis-system.md            # LLM analysis system prompt
```

---

## Contributing

1. **Country profiles** — Add your country's emergency info
2. **Language keywords** — Add threat detection patterns in your language
3. **Sources** — Know a reliable government RSS feed or OSINT API? Add it
4. **Translations** — Help make preparedness guides accessible
5. **Bug reports** — False positive? Missing alert? Report it

---

## License

MIT — use it, modify it, share it. See [LICENSE](LICENSE).

---

<div align="center">

*Built with [OpenClaw](https://openclaw.ai) • Published on [ClawHub](https://clawhub.com)*

**Stay informed. Stay prepared. Stay safe.**

</div>
