import os
import tempfile

import pytest

from otica_scripts.message_tracker import MessageManager


@pytest.fixture
def temp_msg_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("[]")
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)

class TestMessageManager:
    def test_add_message(self, temp_msg_file):
        manager = MessageManager(temp_msg_file)
        msg = manager.add_message("Ótica A", "+5511999999999", "Olá!")

        assert msg.store_name == "Ótica A"
        assert msg.store_phone == "+5511999999999"
        assert msg.message == "Olá!"
        assert msg.status == "sent"

        # Verify persistence
        new_manager = MessageManager(temp_msg_file)
        messages = new_manager._load_messages()
        assert len(messages) == 1
        assert messages[0].store_name == "Ótica A"

    def test_mark_as_responded(self, temp_msg_file):
        manager = MessageManager(temp_msg_file)
        manager.add_message("Ótica B", "+5511888888888", "Oi")

        success = manager.mark_as_responded("+5511888888888", "Preço: R$ 100")
        assert success is True

        messages = manager._load_messages()
        assert messages[0].status == "responded"
        assert messages[0].response == "Preço: R$ 100"
        assert messages[0].responded_at is not None

    def test_get_latest_message_per_store(self, temp_msg_file):
        manager = MessageManager(temp_msg_file)
        manager.add_message("Store 1", "111", "M1")
        manager.add_message("Store 1", "111", "M2") # Newer
        manager.add_message("Store 2", "222", "M3")

        latest = manager.get_latest_message_per_store()
        assert len(latest) == 2
        assert latest["111"].message == "M2"
        assert latest["222"].message == "M3"

    def test_mark_as_responded_nonexistent(self, temp_msg_file):
        manager = MessageManager(temp_msg_file)
        success = manager.mark_as_responded("999", "Empty")
        assert success is False
