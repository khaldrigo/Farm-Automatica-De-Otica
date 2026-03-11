from unittest.mock import Mock, patch

import pytest

from otica_scripts.store import Store
from otica_scripts.whatsapp_sender import WhatsAppSender


@pytest.fixture
def temp_session_file():
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{}")
        temp_path = f.name
    yield temp_path
    import os
    os.unlink(temp_path)


class TestWhatsAppSender:
    def test_init(self, temp_session_file):
        sender = WhatsAppSender(temp_session_file)
        assert sender.session_file.name.endswith(".json")

    @patch("otica_scripts.whatsapp_sender.sync_playwright")
    def test_ensure_browser(self, mock_playwright, temp_session_file):
        mock_browser = Mock()
        mock_context = Mock()
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.start.return_value = mock_browser

        sender = WhatsAppSender(temp_session_file)
        sender._ensure_browser()

        assert sender.browser is not None
        mock_playwright.return_value.start.assert_called_once()

    def test_send_to_store_message_length_warning(self, temp_session_file, capsys):
        sender = WhatsAppSender(temp_session_file)
        store = Store(name="Test", phone="+5511999999999")
        long_message = "a" * 5000

        with patch.object(sender, "_open_chat"), \
             patch.object(sender, "_send_message", return_value=True):
            sender.send_to_store(store, long_message)

        captured = capsys.readouterr()
        assert "exceeds" in captured.out.lower()


class TestWhatsAppSenderIntegration:
    @pytest.mark.skip(reason="Requires browser automation - run manually")
    def test_full_send_flow(self):
        pass
