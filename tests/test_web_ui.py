from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from otica_scripts.web_ui import app

client = TestClient(app)

def test_read_main():
    with patch("otica_scripts.web_ui.StoreManager") as mock_sm, \
        patch("otica_scripts.web_ui.MessageManager") as mock_mm:
        mock_sm.return_value.get_all_stores.return_value = []
        mock_mm.return_value.get_latest_message_per_store.return_value = {}

        response = client.get("/")
        assert response.status_code == 200
        # Template response usually contains some HTML

def test_list_stores_api():
    with patch("otica_scripts.web_ui.StoreManager") as mock_sm:
        mock_store = MagicMock()
        mock_store.to_dict.return_value = {"name": "Test", "phone": "123"}
        mock_sm.return_value.get_all_stores.return_value = [mock_store]

        response = client.get("/stores")
        assert response.status_code == 200
        assert response.json() == {"stores": [{"name": "Test", "phone": "123"}]}

def test_add_store_api():
    with patch("otica_scripts.web_ui.StoreManager") as mock_sm:
        mock_store = MagicMock()
        mock_store.to_dict.return_value = {"name": "New", "phone": "999"}
        mock_sm.return_value.add_store.return_value = mock_store

        response = client.post("/stores", json={"name": "New", "phone": "999"})
        assert response.status_code == 200
        assert response.json()["success"] is True

def test_get_stats_api():
    with patch("otica_scripts.web_ui.MessageManager") as mock_mm:
        msg1 = MagicMock(status="sent")
        msg2 = MagicMock(status="responded")
        mock_mm.return_value.get_latest_message_per_store.return_value = {
            "p1": msg1,
            "p2": msg2
        }

        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["sent"] == 1
        assert data["responded"] == 1
        assert data["pending"] == 0
