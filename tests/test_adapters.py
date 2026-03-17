import pytest
from src.satya.adapters.otlp import OTLPAdapter

def test_otlp_adapter_export(capsys):
    adapter = OTLPAdapter(endpoint="http://dummy:4318")
    adapter.on_task_created({"id": "123", "title": "Test Task"})

    captured = capsys.readouterr()
    assert "[OTLP Adapter]" in captured.out
    assert "otlp_mock" in captured.out
    assert "dummy:4318" in captured.out
    assert "123" in captured.out
    assert "Test Task" in captured.out
