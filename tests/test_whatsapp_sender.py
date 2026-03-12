import time
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
        # Force fresh browser (no persistent profile in test)
        sender.use_existing_browser = False
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
    def test_full_send_flow(self, temp_session_file):
        sender = WhatsAppSender(temp_session_file)
        sender.use_existing_browser = False

        # Mock HTML content - must match selectors in whatsapp_sender.py
        html = """
        <!DOCTYPE html>
        <html>
            <body>
                <div data-tab="10" contenteditable="true" role="textbox"></div>
                <button aria-label="Enviar">Enviar</button>
            </body>
        </html>
        """

        with patch("otica_scripts.whatsapp_sender.sync_playwright"):
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                # Use a real browser but mock the network
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()

                # Mock routing
                import re
                page.route(re.compile(r".*whatsapp\.com.*"), lambda route: route.fulfill(
                    status=200,
                    body=html,
                    content_type="text/html"
                ))

                sender.playwright = pw
                sender.browser = browser
                sender.page = page

                store = Store(name="Mock Store", phone="123456789")

                # Use a small sleep but enough for Playwright
                real_sleep = time.sleep
                with patch("time.sleep", side_effect=lambda x: real_sleep(0.1)):
                    # Test open_whatsapp
                    assert sender.open_whatsapp() is True

                    # DIRECT VERIFICATION: Ensure mock DOM is visible to Playwright
                    page.goto("https://web.whatsapp.com/")
                    assert page.wait_for_selector('div[contenteditable="true"]') is not None

                    # Test send_to_store
                    result = sender.send_to_store(store, "Hello Integration Test")
                    assert result is True

                browser.close()
