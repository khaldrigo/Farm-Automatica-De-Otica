import re
from urllib.parse import quote_plus

from playwright.sync_api import Browser, Page, Playwright, sync_playwright


class GoogleSearchScraper:
    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def _ensure_browser(self) -> None:
        if self.browser is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)

    def open_search(self, query: str, search_engine: str = "bing") -> None:
        self._ensure_browser()
        assert self.browser is not None
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = context.new_page()

        if search_engine == "bing":
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=pt"
        else:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&hl=pt-BR"

        self.page.goto(search_url)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def _extract_phone_from_text(self, text: str) -> str | None:
        # Normalize text by removing common separators
        normalized = text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Ignore 0800 numbers
        if "0800" in normalized:
            return None

        # Look for 10 or 11 digits (with or without 55 prefix)
        patterns = [
            r'55(\d{10,11})', # With 55
            r'(\d{10,11})',   # Without 55 (assumes local)
        ]

        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                digits = match.group(0)
                if digits.startswith("55") and len(digits) >= 12:
                    return f"+{digits}"
                if len(digits) >= 10:
                    return f"+55{digits}"
        return None

    def scrape_optical_stores(self, location: str = "ótica Santarém Pará Brasil", search_engine: str = "bing") -> list[dict]:
        query = f"{location} telefone"
        self.open_search(query, search_engine)
        assert self.page is not None

        results = []
        seen_phones = set()

        try:
            if search_engine == "bing":
                result_elements = self.page.locator('li.b_algo')
            else:
                result_elements = self.page.locator('div.g')
            count = result_elements.count()
            print(f"Found {count} search results")

            for i in range(min(count, 30)):
                try:
                    element = result_elements.nth(i)
                    text = element.text_content() or ""

                    if "ótica" in text.lower() or "óculos" in text.lower() or "lentes" in text.lower():
                        name_match = re.search(r'^([^\n]+)', text)
                        name = name_match.group(1).strip() if name_match else "Unknown"

                        phone = self._extract_phone_from_text(text)

                        if phone and phone not in seen_phones:
                            seen_phones.add(phone)
                            results.append({
                                "name": name[:100],
                                "phone": phone,
                                "address": None
                            })
                            print(f"  - {name}: {phone}")
                        elif not phone:
                            phone_match = re.search(r'(\+55\d{10,11})', text)
                            if phone_match:
                                phone = phone_match.group(1)
                                if phone not in seen_phones:
                                    seen_phones.add(phone)
                                    results.append({
                                        "name": name[:100],
                                        "phone": phone,
                                        "address": None
                                    })
                                    print(f"  - {name}: {phone}")

                except Exception:
                    continue
        except Exception as e:
            print(f"Error scraping results: {e}")

        return results

    def close(self) -> None:
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
