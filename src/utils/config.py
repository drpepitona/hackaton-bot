"""
Configuración del proyecto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

# Crear directorios si no existen
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EIA_API_KEY = os.getenv("EIA_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trading_bot.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Model Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MODEL_PATH = MODELS_DIR

# Trading Parameters
INITIAL_CAPITAL = 10000.0
RISK_PER_TRADE = 0.02  # 2% riesgo por operación
STOP_LOSS = 0.02  # 2% stop loss
TAKE_PROFIT = 0.04  # 4% take profit

# Data Collection
DEFAULT_TICKERS = ["SPY", "QQQ", "DIA", "IWM"]
FRED_INDICATORS = [
    "UNRATE",  # Unemployment Rate
    "GDP",     # GDP
    "CPIAUCSL",  # CPI
    "DFF",     # Federal Funds Rate
    "VIXCLS",  # VIX
]


