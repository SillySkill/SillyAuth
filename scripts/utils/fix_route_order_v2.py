#!/usr/bin/env python3
"""
Move WeChat route to before the generic webhook route (line 320)
"""
from pathlib import Path

MAIN_FILE = Path("/opt/webhook-hub/main.py")

# Read file
with open(MAIN_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# WeChat route starts at line 766 (0-indexed: 765)
# Find the end of WeChat route (before "# 健康检查" or "@app.post(\"/api/v1/wechat/push/test\"")
wechat_start = None
wechat_end = None

for i, line in enumerate(lines):
    if '# ========== 企业微信应用回调端点 ==========' in line:
        wechat_start = i
    if wechat_start is not None and wechat_end is None:
        if '# 健康检查' in line or '@app.post("/api/v1/wechat/push/test")' in line:
            wechat_end = i
            break

if wechat_start is None or wechat_end is None:
    print(f"ERROR: Could not find WeChat route boundaries! start={wechat_start}, end={wechat_end}")
    exit(1)

print(f"Found WeChat route from line {wechat_start + 1} to {wechat_end}")

# Extract WeChat route
wechat_route = lines[wechat_start:wechat_end]

# Remove WeChat route from current location
new_lines = lines[:wechat_start] + lines[wechat_end:]

# Find insertion point (before line 320, which is @app.post("/webhook/{tenant_path:path}"))
insert_pos = None
for i, line in enumerate(new_lines):
    if '@app.post("/webhook/{tenant_path:path}", response_model=WebhookResponse)' in line:
        insert_pos = i
        break

if insert_pos is None:
    print("ERROR: Could not find insertion point!")
    exit(1)

print(f"Inserting before line {insert_pos + 1}")

# Insert WeChat route at the new position
final_lines = new_lines[:insert_pos] + wechat_route + new_lines[insert_pos:]

# Write back
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

print(f"✅ Successfully moved WeChat route from line {wechat_start + 1} to before line {insert_pos + 1}")
print(f"📍 Total lines: {len(lines)} -> {len(final_lines)}")
