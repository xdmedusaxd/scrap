import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# API Credentials
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Admin Settings
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "50"))
ADMIN_LIMIT = int(os.getenv("ADMIN_LIMIT", "500"))

# User Info
USERNAME = os.getenv("USERNAME", "username")
NAME = os.getenv("NAME", "Bot Owner")
