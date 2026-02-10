import os
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_env(monkeypatch):
    """Set mockup environment variables."""
    monkeypatch.setenv("MOONSHOT_API_KEY", "test_mock_moonshot_key")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "test_mock_stripe_key")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "https://test.n8n.cloud/webhook/test")
    monkeypatch.setenv("OFFLINE_MODE", "true")

@pytest.fixture
def mock_ollama():
    """Mock the OllamaEngine."""
    mock = MagicMock()
    mock.generate.return_value = "Mocked LLM Response"
    return mock

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession."""
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json.return_value = {"status": "ok"}
    mock_resp.text.return_value = "<html>Mock Content</html>"
    mock_session.post.return_value.__aenter__.return_value = mock_resp
    mock_session.get.return_value.__aenter__.return_value = mock_resp
    return mock_session
