# AEGIS — Automated Emergency Geopolitical Intelligence System

<div align="center">

**Real-time threat intelligence for civilians in conflict zones.**

*Know what's happening. Know what to do. Stay safe.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-aegis-orange.svg)](https://clawhub.com)

</div>

---

## What is AEGIS?

AEGIS is an open-source [OpenClaw](https://openclaw.ai) skill that turns your AI agent into a personal security intelligence system. It monitors 19+ news sources every 15 minutes and delivers actionable threat assessments in your language, to your preferred messaging channel.

**Built during the 2026 Iran-US conflict** by a civilian in Dubai who needed better situational awareness than doom-scrolling could provide.

### What AEGIS Does

- 🔴 **Instant critical alerts** — missile strikes, airport closures, evacuations
- 📊 **Morning & evening briefings** — aggregated threat assessment with trend analysis
- 🌍 **Location-aware** — monitors sources relevant to YOUR country and city
- 🛡️ **Anti-hoax protocol** — official sources first, verified media second, social media never triggers alerts
- 🌐 **Multi-language** — briefings delivered in your language via LLM translation
- 📱 **Channel-agnostic** — Telegram, WhatsApp, Discord, Signal, SMS
- 💰 **Free baseline** — zero API keys required. All 19 sources use public RSS/web feeds

### What AEGIS Is NOT

- ❌ Not a panic tool — realistic, factual, follows official government guidance
- ❌ Not social media aggregation — no Twitter/X, no unverified rumors
- ❌ Not a replacement for official emergency systems — it's the intelligence layer *above* them
- ❌ Not military-grade — it's for civilians who want to make informed decisions

---

## Quick Start

### 1. Install

```bash
# If you have OpenClaw + ClawHub:
clawhub install aegis

# Or manually:
git clone https://github.com/PleaseChooseUsername/aegis-openclaw-skill.git
cp -r aegis-openclaw-skill/aegis ~/.openclaw/skills/
```

### 2. Onboard

Tell your OpenClaw agent:
> "Set up AEGIS for my location"

Or run directly:
```bash
python3 ~/.openclaw/skills/aegis/scripts/aegis_onboard.py
```

This creates `~/.openclaw/aegis-config.json` with your location, language, and alert preferences.

### 3. First Scan

> "Run an AEGIS scan"

Or:
```bash
python3 ~/.openclaw/skills/aegis/scripts/aegis_scanner.py
```

### 4. Set Up Monitoring

Tell your agent:
> "Set up AEGIS to scan every 15 minutes and send me critical alerts"

Your agent will create OpenClaw cron jobs for:
- Every 15 min: background scan
- Morning: daily briefing
- Evening: situation summary

---

## How It Works

```
┌─────────────────────────────────────────────────┐
│                    AEGIS                         │
│                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  SOURCE   │    │ CLASSIFY │    │ DELIVER  │  │
│  │  FETCHER  │───▶│ + DEDUP  │───▶│ + BRIEF  │  │
│  └──────────┘    └──────────┘    └──────────┘  │
│       │                │               │        │
│  19 sources       Keyword DB      OpenClaw      │
│  RSS + Web       Anti-hoax       Messaging      │
│  No API keys     Tiered alert    Any channel    │
└─────────────────────────────────────────────────┘

Source Tiers:
  Tier 0 🏛️  Government & Emergency (GDACS, NCEMA, Embassies)
  Tier 1 📰  Major News Agencies (Al Jazeera, Reuters, BBC, France24)
  Tier 2 ✈️  Aviation & Infrastructure (FAA NOTAMs)
  Tier 3 🔍  Analysis & OSINT (Crisis Group, GDELT)
  Tier 4 🔑  API-Enhanced (NewsAPI — optional, needs free key)

Alert Tiers:
  🔴 CRITICAL — Immediate threat to life → instant push
  🟠 HIGH     — Significant regional development → batched (30 min)
  ℹ️  MEDIUM   — Situational awareness → digest (6 hours)
```

### Anti-Hoax Protocol

| Source Tier | Trust Level | Alert Behavior |
|-------------|-------------|----------------|
| Tier 0-1 | HIGH | Can trigger alerts directly |
| Tier 2 | DOMAIN | Trusted within their domain only |
| Tier 3+ | REQUIRES CORROBORATION | Must be confirmed by Tier 0-1 |
| Social media | NEVER | Not included. Period. |

Single-source sensational claims are flagged as **UNVERIFIED**. Extraordinary claims require 3+ independent sources.

---

## What's Free, What's Optional

### Free (Zero API Keys)

All 19 baseline sources are free:
- **RSS feeds**: GDACS, Al Jazeera, BBC, France24, Reuters (via web)
- **Web scraping**: Government sites, embassy pages, news portals
- **GDELT Project**: Free API, no key required

The scanner uses `curl` for all fetching — no Python HTTP libraries needed beyond the standard library.

**LLM cost**: Your OpenClaw agent processes scan results. With GitHub Copilot (included in many dev subscriptions), this is effectively free. With OpenRouter or other providers, expect ~$0.03-0.05/day.

### Optional Enhancements

| Service | What It Adds | Cost |
|---------|-------------|------|
| [NewsAPI](https://newsapi.org/register) | 80,000+ news sources, better coverage | Free tier: 100 req/day |
| Perplexity (via OpenRouter) | AI-synthesized web search for context | ~$0.01/query |
| liveuamap.com | Crowd-sourced conflict mapping | Manual (no API) |

To add optional sources, put API keys in your config:
```json
{
  "api_keys": {
    "newsapi": "your-key-here"
  }
}
```

---

## Supported Countries

AEGIS works for **any country** — global sources (GDACS, BBC, Al Jazeera) cover everywhere.

### Countries with Dedicated Profiles

These have localized emergency contacts, evacuation routes, shelter locations, and infrastructure notes:

| Country | Code | Status |
|---------|------|--------|
| 🇦🇪 UAE | `AE` | ✅ Full profile |
| 🇮🇱 Israel | `IL` | 🔜 Coming soon |
| 🇺🇦 Ukraine | `UA` | 🔜 Coming soon |
| 🇱🇧 Lebanon | `LB` | 🔜 Coming soon |

### Contributing a Country Profile

Copy `references/country-profiles/_template.json`, fill in your country's details, and submit a PR. You could save lives.

---

## Skill Structure

```
aegis/
├── SKILL.md                              # OpenClaw skill definition
├── scripts/
│   ├── aegis_scanner.py                  # Core scanning engine
│   ├── aegis_onboard.py                  # Interactive setup
│   └── aegis_briefing.py                 # Briefing generator
└── references/
    ├── source-registry.json              # 19 verified sources
    ├── threat-keywords.json              # EN + AR keyword patterns
    ├── config-reference.md               # Full configuration docs
    ├── country-profiles/
    │   ├── uae.json                      # UAE emergency profile
    │   └── _template.json                # Template for contributions
    ├── preparedness/
    │   ├── go-bag-checklist.md           # Emergency go-bag
    │   ├── communication-plan.md         # Family comms plan
    │   ├── shelter-guidance.md           # Shelter-in-place
    │   └── evacuation-guidance.md        # Evacuation routes & tips
    └── prompts/
        └── analysis-system.md            # LLM analysis instructions
```

---

## Preparedness Resources

AEGIS includes practical, non-panic preparedness guides:

- **[Go-Bag Checklist](aegis/references/preparedness/go-bag-checklist.md)** — What to pack so you can leave in 2 minutes
- **[Communication Plan](aegis/references/preparedness/communication-plan.md)** — How to stay connected when networks fail
- **[Shelter Guidance](aegis/references/preparedness/shelter-guidance.md)** — Where to go, what to do, when to stay
- **[Evacuation Guidance](aegis/references/preparedness/evacuation-guidance.md)** — Routes, transport, embassy registration

These are available to your agent for reference during briefings and can be shared with family.

---

## Requirements

- **OpenClaw** (any recent version)
- **Python 3.8+** (for scripts)
- **curl** (for fetching — pre-installed on virtually all systems)
- No additional Python packages required

---

## Configuration

See [config-reference.md](aegis/references/config-reference.md) for the full schema.

Minimal config:
```json
{
  "location": { "country": "AE", "city": "Dubai", "timezone": "Asia/Dubai" },
  "language": "en",
  "scan_interval_minutes": 15
}
```

---

## Philosophy

> *"The best time to prepare was yesterday. The second best time is now."*

AEGIS was born out of necessity. When missiles are in the air, you don't want to be refreshing five news tabs trying to figure out if your airport is closed. You want a calm, factual system that tells you what's happening, what it means for you, and what to do about it.

This is not a military tool. It's not a government system. It's a civilian's right to situational awareness — automated, aggregated, and honest.

**Official sources first.** AEGIS follows government guidance. It will never tell you to ignore official emergency channels. But it will tell you what's happening between the alerts, help you understand the bigger picture, and make sure you're not caught off guard.

**No hoaxes, no panic, no drama.** Just information.

---

## Contributing

This skill can save lives. Contributions are welcome:

1. **Country profiles** — Add your country's emergency info
2. **Language keywords** — Add threat detection patterns in your language
3. **Source additions** — Know a reliable government RSS feed? Add it
4. **Translations** — Help make preparedness guides accessible
5. **Bug reports** — Found a false positive? Report it

---

## License

MIT License — use it, modify it, share it. If it helps even one person stay safe, it was worth building.

---

<div align="center">

*Built with [OpenClaw](https://openclaw.ai) • Published on [ClawHub](https://clawhub.com)*

**Stay informed. Stay prepared. Stay safe.**

</div>
