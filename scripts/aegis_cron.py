#!/usr/bin/env python3
"""
AEGIS Cron Runner — Silent 15-min scan that only alerts on CRITICAL.
Saves scan results for briefings to use. Posts nothing unless lives are at risk.

Usage:
  python3 aegis_cron.py          # Normal silent scan
  python3 aegis_cron.py --force  # Force output even if no threats

Environment:
  AEGIS_BOT_TOKEN    — Telegram bot token (for critical alerts)
  AEGIS_CHANNEL_ID   — Telegram channel ID
"""

import json, os, sys, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
DATA_DIR = Path(os.environ.get("AEGIS_DATA_DIR", os.path.expanduser("~/.openclaw/aegis-data")))

def main():
    force = "--force" in sys.argv
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run the scanner
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "aegis_scanner.py"), "--cron"],
        capture_output=True, text=True, timeout=120
    )
    
    if result.returncode != 0:
        print(f"[AEGIS] Scanner error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        scan_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[AEGIS] Invalid scanner output", file=sys.stderr)
        sys.exit(1)
    
    # Save scan results for briefings
    (DATA_DIR / "last_scan.json").write_text(json.dumps(scan_data, indent=2))
    
    counts = scan_data.get("threat_counts", {})
    critical = counts.get("critical", 0)
    high = counts.get("high", 0)
    medium = counts.get("medium", 0)
    
    now = datetime.now(timezone(timedelta(hours=4)))
    timestamp = now.strftime("%H:%M Dubai")
    
    # Log to scan history
    log_line = f"[{timestamp}] Items: {scan_data.get('total_items', 0)} | 🔴{critical} 🟠{high} ℹ️{medium}"
    
    history_file = DATA_DIR / "scan_history.log"
    with open(history_file, "a") as f:
        f.write(log_line + "\n")
    
    # Keep history file manageable (last 500 lines)
    try:
        lines = history_file.read_text().strip().split("\n")
        if len(lines) > 500:
            history_file.write_text("\n".join(lines[-500:]) + "\n")
    except:
        pass
    
    # CRITICAL: Post immediately to channel
    if critical > 0:
        print(f"[AEGIS] 🔴 {critical} CRITICAL threats detected! Posting to channel.", file=sys.stderr)
        
        token = os.environ.get("AEGIS_BOT_TOKEN", "")
        channel = os.environ.get("AEGIS_CHANNEL_ID", "")
        
        if token and channel:
            subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "aegis_channel.py"), "critical"],
                input=json.dumps(scan_data),
                text=True, timeout=30,
                env={**os.environ, "AEGIS_BOT_TOKEN": token, "AEGIS_CHANNEL_ID": channel}
            )
        
        # Also output for OpenClaw to deliver to user DM
        print(json.dumps({
            "alert": "critical",
            "message": f"🚨 AEGIS CRITICAL: {critical} critical threat(s) detected. Check AEGIS channel.",
            "threats": scan_data.get("threats", {}).get("critical", [])
        }))
    elif force:
        print(json.dumps({"status": "ok", "counts": counts}))
    else:
        # Silent — no output means no channel spam
        # Just print to stderr for logs
        print(f"[AEGIS] {log_line}", file=sys.stderr)
        # Return HEARTBEAT_OK equivalent so OpenClaw doesn't announce
        print("HEARTBEAT_OK")

if __name__ == "__main__":
    main()
