#!/usr/bin/env python3
"""
Fix WeChat endpoint to use main module's redis_conn instead of ws_server's
"""
from pathlib import Path

MAIN_FILE = Path("/opt/webhook-hub/main.py")

# Read file
with open(MAIN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the redis import from WeChat endpoint and use main module's redis_conn
# Find and replace the import line in the WeChat endpoint
old_import = "    from ws_server import redis_conn, WS_CHANNEL"
new_import = "    from ws_server import WS_CHANNEL"

if old_import in content:
    content = content.replace(old_import, new_import)
    print("✅ Updated Redis import in WeChat endpoint")
else:
    print("⚠️ Import line not found or already fixed")
    print("Looking for:", old_import)
    # Check what's actually there
    if "from ws_server import" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'from ws_server import' in line and 'wechat' in content[max(0, content.find(line)-500):content.find(line)+500]:
                print(f"Found at line {i+1}: {line.strip()}")

# Write back
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Successfully updated {MAIN_FILE}")
