import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv:
    root_env = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(root_env)
    load_dotenv()


TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")

DB_URL = os.getenv("BOT_DATABASE_URL") or os.getenv("DATABASE_URL")
if DB_URL and "@db_upprpo:5432/" in DB_URL:
    DB_URL = DB_URL.replace("@db_upprpo:5432/", "@localhost:5433/")

if not TOKEN:
    raise RuntimeError("Set BOT_TOKEN or TOKEN for the Telegram bot")

if not DB_URL:
    raise RuntimeError("Set BOT_DATABASE_URL or DATABASE_URL for the Telegram bot database")
