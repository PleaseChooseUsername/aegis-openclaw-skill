#!/usr/bin/env python3
"""
AEGIS Briefing Generator — Generates morning/evening security briefings.
Reads scan history, aggregates intelligence, outputs structured briefing.

Usage:
  python3 aegis_briefing.py morning    # Generate morning briefing
  python3 aegis_briefing.py evening    # Generate evening briefing
  python3 aegis_briefing.py status     # Quick threat level check

Output: JSON structure for OpenClaw agent to format and deliver.
The OpenClaw agent will translate to user's language and deliver via their channel.
"""

import json, os, sys, argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = Path(os.environ.get("AEGIS_DATA_DIR", os.path.expanduser("~/.openclaw/aegis-data")))
SCAN_LOG = DATA_DIR / "scan_log.json"
SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"

DEFAULT_CONFIG_PATHS = [
    os.path.expanduser("~/.openclaw/aegis-config.json"),
    os.path.join(os.path.dirname(__file__), "..", "aegis-config.json"),
]

def load_config():
    for p in DEFAULT_CONFIG_PATHS:
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    return {}

def load_scan_history(hours=12):
    """Load scan results from the last N hours."""
    if not SCAN_LOG.exists():
        return []
    try:
        entries = json.loads(SCAN_LOG.read_text())
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        return [e for e in entries if e.get("time", "") >= cutoff]
    except:
        return []

def load_country_profile(country_code):
    """Load country profile for emergency info."""
    profile_file = REFERENCES_DIR / "country-profiles" / f"{country_code.lower()}.json"
    if profile_file.exists():
        with open(profile_file) as f:
            return json.load(f)
    return None

def assess_threat_level(scans):
    """Determine overall threat level from recent scans."""
    if not scans:
        return {"level": "unknown", "emoji": "❓", "description": "No recent scans available"}
    
    total_critical = sum(s.get("threats", {}).get("critical", 0) for s in scans)
    total_high = sum(s.get("threats", {}).get("high", 0) for s in scans)
    total_medium = sum(s.get("threats", {}).get("medium", 0) for s in scans)
    
    if total_critical > 0:
        return {"level": "critical", "emoji": "🔴", "description": "Active threat — follow official guidance immediately"}
    elif total_high > 5:
        return {"level": "high", "emoji": "🟠", "description": "Elevated threat — heightened preparedness recommended"}
    elif total_high > 0:
        return {"level": "elevated", "emoji": "🟡", "description": "Elevated — monitor closely, review preparedness"}
    elif total_medium > 0:
        return {"level": "guarded", "emoji": "🔵", "description": "Guarded — situational awareness, normal precautions"}
    else:
        return {"level": "low", "emoji": "🟢", "description": "Low — no significant threats detected"}

def trend_indicator(scans):
    """Calculate threat trend (increasing/decreasing/stable)."""
    if len(scans) < 4:
        return "→", "Insufficient data"
    
    mid = len(scans) // 2
    first_half = scans[:mid]
    second_half = scans[mid:]
    
    score_first = sum(
        s.get("threats", {}).get("critical", 0) * 10 +
        s.get("threats", {}).get("high", 0) * 3 +
        s.get("threats", {}).get("medium", 0)
        for s in first_half
    )
    score_second = sum(
        s.get("threats", {}).get("critical", 0) * 10 +
        s.get("threats", {}).get("high", 0) * 3 +
        s.get("threats", {}).get("medium", 0)
        for s in second_half
    )
    
    diff = score_second - score_first
    if diff > 5:
        return "⬆️", "Increasing"
    elif diff > 2:
        return "↗️", "Slightly increasing"
    elif diff < -5:
        return "⬇️", "Decreasing"
    elif diff < -2:
        return "↘️", "Slightly decreasing"
    else:
        return "➡️", "Stable"

def generate_briefing(briefing_type="morning"):
    """Generate a briefing structure for OpenClaw to format and deliver."""
    config = load_config()
    location = config.get("location", {})
    country = location.get("country", "")
    city = location.get("city", "Unknown")
    
    hours = 12 if briefing_type == "morning" else 12
    scans = load_scan_history(hours)
    
    threat_assessment = assess_threat_level(scans)
    trend_emoji, trend_text = trend_indicator(scans)
    
    profile = load_country_profile(country)
    
    briefing = {
        "type": briefing_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "location": {
            "city": city,
            "country": location.get("country_name", country)
        },
        "threat_assessment": {
            "level": threat_assessment["level"],
            "emoji": threat_assessment["emoji"],
            "description": threat_assessment["description"],
            "trend": trend_emoji,
            "trend_text": trend_text
        },
        "scan_summary": {
            "scans_analyzed": len(scans),
            "period_hours": hours,
            "total_critical": sum(s.get("threats", {}).get("critical", 0) for s in scans),
            "total_high": sum(s.get("threats", {}).get("high", 0) for s in scans),
            "total_medium": sum(s.get("threats", {}).get("medium", 0) for s in scans)
        },
        "preparedness_checklist": [
            "Phone charged, emergency alerts ON",
            "Go-bag accessible and packed",
            "Family communication plan confirmed",
            "Know your nearest shelter location",
            "Vehicle fuel above half tank",
            "3-day water supply (4L/person/day)",
            "Cash reserve accessible",
            "Passport and travel documents ready"
        ],
        "emergency_contacts": {}
    }
    
    if profile:
        briefing["emergency_contacts"] = {
            "emergency": profile.get("emergency", {}).get("number", ""),
            "agency": profile.get("emergency", {}).get("agency", ""),
            "website": profile.get("emergency", {}).get("website", "")
        }
        briefing["infrastructure_notes"] = profile.get("infrastructure", {})
    
    # Output for OpenClaw agent
    print(json.dumps(briefing, indent=2))
    return briefing

def quick_status():
    """Quick threat level check."""
    scans = load_scan_history(6)
    assessment = assess_threat_level(scans)
    trend_emoji, trend_text = trend_indicator(scans)
    
    print(f"{assessment['emoji']} Threat Level: {assessment['level'].upper()}")
    print(f"{trend_emoji} Trend: {trend_text}")
    print(f"Based on {len(scans)} scans in last 6 hours")

def main():
    parser = argparse.ArgumentParser(description="AEGIS Briefing Generator")
    parser.add_argument("type", nargs="?", choices=["morning", "evening", "status"], default="status")
    args = parser.parse_args()
    
    if args.type == "status":
        quick_status()
    else:
        generate_briefing(args.type)

if __name__ == "__main__":
    main()
