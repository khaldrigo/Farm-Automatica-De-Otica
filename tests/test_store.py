import tempfile
from pathlib import Path

import pytest

from otica_scripts.store import Store, StoreManager


@pytest.fixture
def temp_data_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


class TestStore:
    def test_create_store(self):
        store = Store(name="Test Store", phone="+5511999999999")
        assert store.name == "Test Store"
        assert store.phone == "+5511999999999"

    def test_phone_normalization_with_55(self):
        store = Store(name="Test", phone="11999999999")
        assert store.phone == "+5511999999999"

    def test_phone_normalization_without_country_code(self):
        store = Store(name="Test", phone="+5511999999999")
        assert store.phone == "+5511999999999"

    def test_phone_with_special_chars(self):
        store = Store(name="Test", phone="(11) 99999-9999")
        assert store.phone == "+5511999999999"

    def test_to_dict(self):
        store = Store(name="Test", phone="+5511999999999", address="Rua X", instagram="@test")
        data = store.to_dict()
        assert data == {"name": "Test", "phone": "+5511999999999", "address": "Rua X", "instagram": "@test"}

    def test_from_dict(self):
        data = {"name": "Test", "phone": "+5511999999999", "address": "Rua X", "instagram": "@test"}
        store = Store.from_dict(data)
        assert store.name == "Test"
        assert store.phone == "+5511999999999"
        assert store.instagram == "@test"

    def test_instagram_normalization(self):
        store = Store(name="Test", phone="+5511999999999", instagram="test")
        assert store.instagram == "@test"
        store2 = Store(name="Test2", phone="+5511888888888", instagram="@test2")
        assert store2.instagram == "@test2"


class TestStoreManager:
    def test_add_store(self, temp_data_file):
        manager = StoreManager(temp_data_file)
        store = manager.add_store("Ótica Central", "+5511888888888")
        assert store.name == "Ótica Central"
        assert store.phone == "+5511888888888"

    def test_get_all_stores(self, temp_data_file):
        manager = StoreManager(temp_data_file)
        manager.add_store("Store 1", "+5511999999999")
        manager.add_store("Store 2", "+5511888888888")
        stores = manager.get_all_stores()
        assert len(stores) == 2

    def test_remove_store(self, temp_data_file):
        manager = StoreManager(temp_data_file)
        manager.add_store("Test Store", "+5511999999999")
        result = manager.remove_store("Test Store")
        assert result is True
        assert len(manager.get_all_stores()) == 0

    def test_remove_nonexistent_store(self, temp_data_file):
        manager = StoreManager(temp_data_file)
        result = manager.remove_store("Nonexistent")
        assert result is False

    def test_get_store(self, temp_data_file):
        manager = StoreManager(temp_data_file)
        manager.add_store("Test Store", "+5511999999999", "Address 123")
        store = manager.get_store("Test Store")
        assert store is not None
        assert store.name == "Test Store"
        assert store.address == "Address 123"

    def test_get_store_case_insensitive(self, temp_data_file):
        manager = StoreManager(temp_data_file)
        manager.add_store("Test Store", "+5511999999999")
        store = manager.get_store("test store")
        assert store is not None
