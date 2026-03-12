from otica_scripts.scraper import GoogleSearchScraper


def test_extract_phone_from_text():
    scraper = GoogleSearchScraper()

    # Test cases: (input_text, expected_output)
    test_cases = [
        ("+5511999999999", "+5511999999999"),
        ("11 99999-9999", "+5511999999999"),
        ("(11) 9999-8888", "+551199998888"),
        ("91 98888 7777", "+5591988887777"),
        ("Phone: 5511999999999", "+5511999999999"),
        ("No phone here", None),
        ("123", None), # Too short
        ("0800 123 4567", None), # Doesn't match current patterns well or we might not want it
    ]

    for input_text, expected in test_cases:
        result = scraper._extract_phone_from_text(input_text)
        assert result == expected, f"Failed for input: {input_text}. Expected {expected}, got {result}"

def test_extract_phone_with_noise():
    scraper = GoogleSearchScraper()
    text = "Entre em contato pelo WhatsApp (91) 91234-5678 ou venha nos visitar."
    assert scraper._extract_phone_from_text(text) == "+5591912345678"

def test_extract_phone_multiple_spaces():
    scraper = GoogleSearchScraper()
    text = "Tel: 11   9  8888  7777"
    assert scraper._extract_phone_from_text(text) == "+5511988887777"
