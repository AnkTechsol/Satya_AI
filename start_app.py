import sys
import os
import subprocess
import time
import urllib.request

cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "5000", "--server.headless", "true"]
proc = subprocess.Popen(cmd)
print(f"Started Streamlit on port 5000 (PID: {proc.pid})")

# Start AI Orchestrator Daemon
orchestrator_cmd = [sys.executable, "orchestrator_runner.py"]
orchestrator_proc = subprocess.Popen(orchestrator_cmd)
print(f"Started AI Orchestrator daemon (PID: {orchestrator_proc.pid})")

# Wait for it to be ready
for i in range(15):
    try:
        r = urllib.request.urlopen("http://localhost:5000")
        if r.getcode() == 200:
            print("Streamlit is up!")
            break
    except Exception as e:
        time.sleep(1)
else:
    print("Streamlit failed to start within 15 seconds")

# Create mock data
os.makedirs("satya_data/heartbeats", exist_ok=True)
import json
from datetime import datetime, timezone, timedelta

base_time = datetime.now(timezone.utc)
hb = {"status": "online", "last_seen": base_time.isoformat().replace("+00:00", "") + "Z", "agent_name": "TestAgent"}
with open("satya_data/heartbeats/TestAgent.json", "w") as f:
    json.dump(hb, f)

os.makedirs("satya_data/chat/TestAgent", exist_ok=True)
for i in range(3):
    ts = base_time + timedelta(minutes=i)
    msg = {
        "timestamp": ts.isoformat().replace("+00:00", "") + "Z",
        "sender": "Human Operator" if i % 2 == 0 else "TestAgent",
        "message": f"This is test message {i+1}",
        "status": "read"
    }
    with open(f"satya_data/chat/TestAgent/msg_{i}.json", "w") as f:
        json.dump(msg, f)
