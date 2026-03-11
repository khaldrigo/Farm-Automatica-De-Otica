import pytest


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    monkeypatch.setenv("STORES_DATA_FILE", "data/test_stores.json")
    monkeypatch.setenv("WHATSAPP_SESSION_FILE", "session.json")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
