import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY mancante nel file .env")

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
HTTPS_ONLY = os.getenv("HTTPS_ONLY", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./portale.db")

ROBLOX_CLIENT_ID = os.getenv("ROBLOX_CLIENT_ID", "")
ROBLOX_CLIENT_SECRET = os.getenv("ROBLOX_CLIENT_SECRET", "")
ROBLOX_REDIRECT_URI = os.getenv("ROBLOX_REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")

# ID Roblox (separati da virgola) che diventano admin al primo login
ADMIN_ROBLOX_IDS = {x.strip() for x in os.getenv("ADMIN_ROBLOX_IDS", "").split(",") if x.strip()}
# Codice comune per l'accesso (fornito dai comandi)
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "XyTkmPrVz")