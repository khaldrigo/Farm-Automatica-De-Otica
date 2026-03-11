from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STORES_DATA_FILE = getenv("STORES_DATA_FILE", str(DATA_DIR / "stores.json"))
MESSAGES_DATA_FILE = getenv("MESSAGES_DATA_FILE", str(DATA_DIR / "messages.json"))
WHATSAPP_SESSION_FILE = getenv("WHATSAPP_SESSION_FILE", str(BASE_DIR / "session.json"))
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
MESSAGE_DELAY_SECONDS = 2
MAX_MESSAGE_LENGTH = 4096
