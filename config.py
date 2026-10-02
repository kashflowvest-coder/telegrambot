import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN_USER_IDS = [
    int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()
]
# Monitor channel — set MONITOR_CHANNEL_ID in .env to a private channel chat ID
# The bot must be added as admin to that channel for this to work.
MONITOR_CHANNEL_ID_RAW = os.getenv("MONITOR_CHANNEL_ID", "").strip()
MONITOR_CHANNEL_ID = int(MONITOR_CHANNEL_ID_RAW) if MONITOR_CHANNEL_ID_RAW.lstrip("-").isdigit() else (MONITOR_CHANNEL_ID_RAW if MONITOR_CHANNEL_ID_RAW else None)

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "builtin").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Trading Defaults
DEFAULT_TRADING_MODE = os.getenv("DEFAULT_TRADING_MODE", "paper").lower()  # 'paper' or 'live'
DEFAULT_EXCHANGE = os.getenv("DEFAULT_EXCHANGE", "binance").lower()
DEFAULT_PAPER_BALANCE = float(os.getenv("DEFAULT_PAPER_BALANCE", "10000.0"))
DEFAULT_RISK_PERCENT = float(os.getenv("DEFAULT_RISK_PERCENT", "2.0"))  # % balance per trade
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", "1"))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "15"))

# Database Path
DB_PATH = BASE_DIR / "trading_bot.db"

# Supported Trading Pairs (Major liquid crypto pairs)
SUPPORTED_PAIRS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "NEAR/USDT"
]

# Supported Timeframes
SUPPORTED_TIMEFRAMES = ["5m", "15m", "1h", "4h", "1d"]
DEFAULT_TIMEFRAME = "1h"
