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

# Provider Configurations
WHATSAPP_PROVIDER = getenv("WHATSAPP_PROVIDER", "playwright").lower()

# Evolution API Configurations
EVOLUTION_API_URL = getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE_NAME = getenv("EVOLUTION_INSTANCE_NAME", "OticaBot")

