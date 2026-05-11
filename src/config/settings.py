import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
LOGS_DIR = ROOT_DIR / "logs"

APP_TITLE = "Llama Educacional"
APP_GEOMETRY = "1280x720"
DEFAULT_FONT_FAMILY = "Helvetica"
DEFAULT_FONT_SIZE = 14

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_CONTEXT = 2000

LINKEDIN_URL = "https://www.linkedin.com/in/isllantoso/"

LOGS_DIR.mkdir(exist_ok=True)
