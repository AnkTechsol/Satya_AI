import sys
import os
import json

# Ensure we're authorized before importing SDK
os.environ['SATYA_AGENT_KEY'] = 'DEMO_KEY'
os.environ['SATYA_AGENT_KEYS'] = 'DEMO_KEY'
os.environ['AUDIT_SECRET'] = 'dummy_secret'

import run_sim

def test_simulation():
    # Patch the environment inside run_sim to avoid it overriding DEMO_KEY with test-run
    run_sim.os.environ['SATYA_AGENT_KEY'] = 'DEMO_KEY'
    run_sim.os.environ['SATYA_AGENT_KEYS'] = 'DEMO_KEY'
    run_sim.os.environ['AUDIT_SECRET'] = 'dummy_secret'

    lats = run_sim.run()
    assert len(lats) > 0, "Simulation failed to produce any latencies."
    assert any(x[0] == "create" for x in lats), "No task create latencies recorded."
    assert any(x[0] == "complete" for x in lats), "No task complete latencies recorded."

if __name__ == '__main__':
    test_simulation()
    print("Simulation tests passed.")
