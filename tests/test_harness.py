import os
import pytest
from importlib import reload
import src.satya.auth as auth

def test_simulation(monkeypatch):
    monkeypatch.setenv('SATYA_AGENT_KEY', 'test-run')
    monkeypatch.setenv('SATYA_AGENT_KEYS', 'test-run,DEMO_KEY')
    monkeypatch.setenv('AUDIT_SECRET', 'dummy_secret')

    reload(auth)

    import run_sim
    # Overwrite what run_sim might have set to ensure consistency
    monkeypatch.setenv('SATYA_AGENT_KEY', 'test-run')
    monkeypatch.setenv('SATYA_AGENT_KEYS', 'test-run,DEMO_KEY')
    monkeypatch.setenv('AUDIT_SECRET', 'dummy_secret')
    reload(auth)

    lats = run_sim.run()

    assert len(lats) > 0, "Simulation failed to produce any latencies."
    assert any(x[0] == "create" for x in lats), "No task create latencies recorded."
    assert any(x[0] == "complete" for x in lats), "No task complete latencies recorded."
