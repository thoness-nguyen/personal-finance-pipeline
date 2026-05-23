from pathlib import Path
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator import run_pipeline


def _mock_response(payload: dict) -> Mock:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


def test_resolve_base_url_ignores_empty_values(monkeypatch):
    monkeypatch.setenv("A_URL", "   ")
    monkeypatch.setenv("B_URL", "")

    result = run_pipeline._resolve_base_url("A_URL", "B_URL", default="http://default")

    assert result == "http://default"


def test_run_python_api_falls_back_to_default_when_env_is_empty(monkeypatch):
    monkeypatch.setenv("PYTHON_API_URL", "")

    with patch("orchestrator.run_pipeline.httpx.post", return_value=_mock_response({"ok": True})) as post:
        result = run_pipeline.run_python_api()

    assert result == {"ok": True}
    post.assert_called_once_with("http://localhost:8000/api/v1/ingest", timeout=60)


def test_run_nodejs_fallback_prefers_node_api_url_when_nodejs_api_url_empty(monkeypatch):
    monkeypatch.setenv("NODEJS_API_URL", "")
    monkeypatch.setenv("NODE_API_URL", "https://node.example.com/")

    with patch("orchestrator.run_pipeline.httpx.post", return_value=_mock_response({"ok": True})) as post:
        result = run_pipeline.run_nodejs_fallback()

    assert result == {"ok": True}
    post.assert_called_once_with("https://node.example.com/api/v1/ingest", timeout=60)
