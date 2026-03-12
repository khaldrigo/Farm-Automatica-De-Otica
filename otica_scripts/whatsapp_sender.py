import os
import time
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from otica_scripts.config import MAX_MESSAGE_LENGTH, MESSAGE_DELAY_SECONDS, WHATSAPP_SESSION_FILE
from otica_scripts.store import Store


class WhatsAppSender:
    def __init__(self, session_file: str = WHATSAPP_SESSION_FILE) -> None:
        self.session_file = Path(session_file)
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self.use_existing_browser = True

    def _get_chrome_user_data_dir(self) -> str | None:
        possible_paths = [
            os.path.expanduser("~/.config/google-chrome"),
            os.path.expanduser("~/.config/chromium"),
            os.path.expanduser("~/.chrome"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _ensure_browser(self) -> None:
        if self.browser is None:
            self.playwright = sync_playwright().start()

            user_data_dir = self._get_chrome_user_data_dir()

            if user_data_dir and self.use_existing_browser:
                print(f"Using existing Chrome profile: {user_data_dir}")
                try:
                    self.context = self.playwright.chromium.launch_persistent_context(
                        user_data_dir,
                        headless=False,
                        args=["--no-sandbox", "--disable-setuid-sandbox"]
                    )
                    if self.context.pages:
                        self.page = self.context.pages[0]
                    return
                except Exception as e:
                    print(f"Could not use existing browser: {e}")
                    print("Falling back to new browser...")

            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )

    def _save_session(self, context: BrowserContext) -> None:
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(self.session_file))

    def _load_session(self) -> dict | None:
        if self.session_file.exists():
            return {"storage_state": str(self.session_file)}
        return None

    def open_whatsapp(self) -> bool:
        self._ensure_browser()

        if self.context is None and self.browser is None:
            print("ERROR: No browser context available")
            return False

        if self.context and self.context.pages:
            for p in self.context.pages:
                if p.url and "web.whatsapp.com" in p.url:
                    self.page = p
                    print("Using existing WhatsApp Web tab...")
                    return True

        current_context = self.context
        if current_context is None:
            if self.browser is not None:
                current_context = self.browser.new_context()
            else:
                return False

        self.page = current_context.new_page()

        print("Opening WhatsApp Web...")
        print("NOTE: If QR code appears, please scan it within 60 seconds")
        self.page.goto("https://web.whatsapp.com/")

        time.sleep(5)

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            print("Page loaded, checking for WhatsApp...")
        except Exception as e:
            print(f"Warning: {e}")

        try:
            self.page.wait_for_selector('[data-tab]', timeout=30000)
            print("WhatsApp is ready!")
            return True
        except Exception:
            pass

        try:
            self.page.wait_for_selector('div[contenteditable="true"]', timeout=30000)
            print("WhatsApp input detected - ready to send!")
            return True
        except Exception:
            pass

        if self.page.url and "whatsapp.com" in self.page.url:
            print("WhatsApp page opened - continuing anyway")
            return True

        print("ERROR: Could not connect to WhatsApp Web")
        return False

    def _open_chat(self, phone: str) -> None:
        assert self.page is not None
        url = f"https://web.whatsapp.com/send?phone={phone}"
        self.page.goto(url)
        time.sleep(3)

    def _send_message(self, message: str) -> bool:
        assert self.page is not None
        try:
            time.sleep(1)

            selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]'
            ]

            input_box = None
            for sel in selectors:
                try:
                    input_box = self.page.wait_for_selector(sel, timeout=3000)
                    if input_box:
                        break
                except Exception:
                    continue

            if not input_box:
                print("ERROR: Could not find message input box - WhatsApp not loaded properly")
                return False

            input_box.fill(message)
            time.sleep(0.5)

            send_button = self.page.locator('button[aria-label="Enviar"]')
            if send_button.count() == 0:
                send_button = self.page.locator('span[data-icon="send"]')

            if send_button.count() == 0:
                print("Pressing Enter to send...")
                input_box.press("Enter")
            else:
                print("Clicking send button...")
                send_button.click()

            time.sleep(1)

            print("Message sent successfully!")
            return True
        except Exception as e:
            print(f"ERROR sending message: {e}")
            return False

    def send_to_store(self, store: Store, message: str) -> bool:
        if len(message) > MAX_MESSAGE_LENGTH:
            print(f"Warning: Message exceeds {MAX_MESSAGE_LENGTH} characters")
        print(f"Opening chat for {store.name} ({store.phone})...")
        self._open_chat(store.phone)
        return self._send_message(message)

    def send_to_all(self, stores: list[Store], message: str) -> dict[str, bool]:
        if len(message) > MAX_MESSAGE_LENGTH:
            print(f"Warning: Message exceeds {MAX_MESSAGE_LENGTH} characters")
        results = {}
        for store in stores:
            print(f"\nSending to {store.name} ({store.phone})...")
            success = self.send_to_store(store, message)
            results[store.name] = success
            if success and store != stores[-1]:
                print(f"Waiting {MESSAGE_DELAY_SECONDS}s before next message...")
                time.sleep(MESSAGE_DELAY_SECONDS)
        return results

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
