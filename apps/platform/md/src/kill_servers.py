"""Kill all Python processes listening on port 8080."""
import subprocess
import os
import signal
import time

# Find processes on port 8080
result = subprocess.run(
    'netstat -ano', capture_output=True, text=True, shell=True
)
pids = set()
for line in result.stdout.split('\n'):
    if ':8080' in line and 'LISTENING' in line:
        parts = line.strip().split()
        if parts:
            pids.add(parts[-1])

print(f"Found PIDs on 8080: {pids}")

# Try to kill each
for pid in pids:
    try:
        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        print(f"Killed PID {pid}")
    except Exception as e:
        print(f"Failed to kill {pid}: {e}")

time.sleep(3)

# Verify
result2 = subprocess.run(
    'netstat -ano', capture_output=True, text=True, shell=True
)
remaining = []
for line in result2.stdout.split('\n'):
    if ':8080' in line and 'LISTENING' in line:
        remaining.append(line.strip())

if remaining:
    print(f"Still listening ({len(remaining)}):")
    for r in remaining:
        print(f"  {r}")
else:
    print("Port 8080 is free!")
