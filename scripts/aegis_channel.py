#!/usr/bin/env python3
"""
AEGIS Channel Publisher — Formats and posts alerts to Telegram channel.
Called by the scanner or briefing scripts. Handles all channel formatting.

Usage:
  python3 aegis_channel.py critical <json_file>   # Post critical alert
  python3 aegis_channel.py briefing <json_file>    # Post formatted briefing
  python3 aegis_channel.py status                  # Post quiet status line (for debugging)

Environment:
  AEGIS_BOT_TOKEN    — Telegram bot token
  AEGIS_CHANNEL_ID   — Telegram channel ID
"""

import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

def load_env():
    """Load bot token and channel from aegis-config or environment."""
    token = os.environ.get("AEGIS_BOT_TOKEN", "")
    channel = os.environ.get("AEGIS_CHANNEL_ID", "")
    
    # Try config file
    config_paths = [
        os.path.expanduser("~/.openclaw/aegis-config.json"),
        os.path.join(os.path.dirname(__file__), "..", "aegis-config.json"),
    ]
    for p in config_paths:
        if os.path.exists(p):
            with open(p) as f:
                cfg = json.load(f)
            if not token:
                token = cfg.get("telegram", {}).get("bot_token", "")
            if not channel:
                channel = cfg.get("telegram", {}).get("channel_id", "")
            break
    
    return token, channel

def send_telegram(token, channel_id, text, parse_mode="MarkdownV2"):
    """Send message to Telegram channel."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": channel_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        print(f"[AEGIS] Telegram send error: {e}", file=sys.stderr)
        # Try HTML fallback
        try:
            payload2 = json.dumps({
                "chat_id": channel_id,
                "text": text.replace("\\", ""),
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }).encode()
            req2 = urllib.request.Request(url, data=payload2, headers={"Content-Type": "application/json"})
            resp2 = urllib.request.urlopen(req2, timeout=15)
            return json.loads(resp2.read())
        except Exception as e2:
            # Final fallback: plain text
            payload3 = json.dumps({
                "chat_id": channel_id,
                "text": text.replace("\\", ""),
                "disable_web_page_preview": True
            }).encode()
            req3 = urllib.request.Request(url, data=payload3, headers={"Content-Type": "application/json"})
            resp3 = urllib.request.urlopen(req3, timeout=15)
            return json.loads(resp3.read())

def escape_md2(text):
    """Escape text for Telegram MarkdownV2."""
    chars = '_*[]()~`>#+-=|{}.!'
    for c in chars:
        text = text.replace(c, f'\\{c}')
    return text

def format_critical_alert(scan_data):
    """Format a critical alert for channel posting."""
    threats = scan_data.get("threats", {}).get("critical", [])
    if not threats:
        return None
    
    now = datetime.now(timezone(timedelta(hours=4)))
    
    lines = []
    lines.append("🚨 *AEGIS CRITICAL ALERT* 🚨")
    lines.append(f"🕐 {now.strftime('%d %b %Y | %H:%M')} Dubai")
    lines.append("")
    
    for t in threats[:5]:
        title = t.get("title", "Unknown threat")
        source = t.get("source_name", "Unknown")
        tier = t.get("source_tier", "?")
        url = t.get("url", "")
        
        lines.append(f"🔴 *{escape_md2(title)}*")
        lines.append(f"   📰 {escape_md2(source)} \\| Tier {tier}")
        if url:
            lines.append(f"   🔗 {escape_md2(url)}")
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("✅ Follow NCEMA official guidance")
    lines.append("✅ Check official emergency channels")
    lines.append("")
    lines.append("🤖 _AEGIS v1\\.0 — Automated Emergency Intelligence_")
    
    return "\n".join(lines)

def format_briefing(briefing_data, scan_data=None):
    """Format a morning/evening briefing for channel posting. Uses plain text for reliability."""
    btype = briefing_data.get("type", "status")
    location = briefing_data.get("location", {})
    threat = briefing_data.get("threat_assessment", {})
    summary = briefing_data.get("scan_summary", {})
    
    now = datetime.now(timezone(timedelta(hours=4)))
    
    is_morning = btype == "morning"
    header = "☀️ AEGIS MORNING BRIEFING" if is_morning else "🌙 AEGIS EVENING BRIEFING"
    
    lines = []
    lines.append(f"⚡ {header}")
    lines.append(f"🕐 {now.strftime('%d %b %Y | %H:%M')} Dubai (UTC+4)")
    lines.append(f"📍 {location.get('city', '?')}, {location.get('country', '?')}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    # Threat level
    level = threat.get("level", "unknown").upper()
    emoji = threat.get("emoji", "❓")
    desc = threat.get("description", "")
    trend = threat.get("trend", "➡️")
    trend_text = threat.get("trend_text", "Stable")
    
    lines.append(f"{emoji} Threat Level: {level} {trend} {trend_text}")
    lines.append(f"   {desc}")
    lines.append("")
    
    # Scan stats
    lines.append(f"📊 Last {summary.get('period_hours', 12)}h Summary")
    lines.append(f"   • Sources monitored: {summary.get('scans_analyzed', 0)} scans")
    lines.append(f"   • 🔴 Critical: {summary.get('total_critical', 0)}")
    lines.append(f"   • 🟠 High: {summary.get('total_high', 0)}")
    lines.append(f"   • ℹ️ Medium: {summary.get('total_medium', 0)}")
    lines.append("")
    
    # Top threats from recent scan data
    if scan_data:
        all_threats = []
        for level_name in ["critical", "high", "medium"]:
            for t in scan_data.get("threats", {}).get(level_name, []):
                t["_level"] = level_name
                all_threats.append(t)
        
        if all_threats:
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("📰 Key Developments")
            lines.append("")
            
            level_emoji = {"critical": "🔴", "high": "🟠", "medium": "ℹ️"}
            shown = 0
            for t in all_threats[:8]:
                le = level_emoji.get(t["_level"], "•")
                title = t.get("title", "")[:100]
                source = t.get("source_name", "")
                tier = t.get("source_tier", "")
                
                verify = "✅ VERIFIED" if int(tier) <= 1 else "📋 Reported"
                
                lines.append(f"{le} {title}")
                lines.append(f"   📰 {source} (Tier {tier}) | {verify}")
                lines.append("")
                shown += 1
            
            if not shown:
                lines.append("   No significant developments in this period.")
                lines.append("")
    
    # Preparedness
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("📋 Preparedness Check")
    lines.append("✅ Follow NCEMA / official guidance")
    lines.append("✅ Phone charged, emergency alerts ON")
    lines.append("✅ Go-bag accessible & packed")
    lines.append("✅ Know your nearest shelter")
    lines.append("✅ Vehicle fuel above half tank")
    
    # Emergency contacts
    contacts = briefing_data.get("emergency_contacts", {})
    if contacts.get("emergency"):
        lines.append("")
        lines.append(f"📞 Emergency: {contacts['emergency']}")
        if contacts.get("agency"):
            lines.append(f"🏛️ {contacts['agency']}")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 AEGIS v1.0 — Open Source Emergency Intelligence")
    lines.append("📡 19 sources | Anti-hoax protocol | Updated every 15 min")
    lines.append("🔗 github.com/PleaseChooseUsername/aegis-openclaw-skill")
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: aegis_channel.py <critical|briefing|status> [json_file]", file=sys.stderr)
        sys.exit(1)
    
    action = sys.argv[1]
    token, channel = load_env()
    
    if not token or not channel:
        print("[AEGIS] Missing AEGIS_BOT_TOKEN or AEGIS_CHANNEL_ID", file=sys.stderr)
        sys.exit(1)
    
    if action == "critical":
        if len(sys.argv) < 3:
            data = json.load(sys.stdin)
        else:
            with open(sys.argv[2]) as f:
                data = json.load(f)
        
        msg = format_critical_alert(data)
        if msg:
            result = send_telegram(token, channel, msg)
            print(json.dumps(result, indent=2))
        else:
            print("[AEGIS] No critical threats to post", file=sys.stderr)
    
    elif action == "briefing":
        if len(sys.argv) < 3:
            data = json.load(sys.stdin)
        else:
            with open(sys.argv[2]) as f:
                data = json.load(f)
        
        # Also load latest scan if available
        scan_data = None
        data_dir = Path(os.environ.get("AEGIS_DATA_DIR", os.path.expanduser("~/.openclaw/aegis-data")))
        last_scan = data_dir / "last_scan.json"
        if last_scan.exists():
            with open(last_scan) as f:
                scan_data = json.load(f)
        
        msg = format_briefing(data, scan_data)
        result = send_telegram(token, channel, msg, parse_mode="")
        print(json.dumps(result, indent=2))
    
    elif action == "status":
        now = datetime.now(timezone(timedelta(hours=4)))
        msg = f"⚡ AEGIS Status — {now.strftime('%H:%M')} Dubai\n📡 Monitoring active | No critical alerts"
        result = send_telegram(token, channel, msg, parse_mode="")
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
