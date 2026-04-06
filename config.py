# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ── App
APP_MODE = os.getenv("APP_MODE", "simulation")
IS_SIMULATION = APP_MODE == "simulation"
SECRET_KEY = os.getenv("SECRET_KEY", "autoseller_secret_2026")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./autoseller.db")

# ── AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── Payment
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ── Logistics
SHIPROCKET_EMAIL = os.getenv("SHIPROCKET_EMAIL")
SHIPROCKET_PASSWORD = os.getenv("SHIPROCKET_PASSWORD")

# ── Validation check on startup
def validate_config():
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not RAZORPAY_KEY_ID:
        missing.append("RAZORPAY_KEY_ID")
    if not RAZORPAY_KEY_SECRET:
        missing.append("RAZORPAY_KEY_SECRET")
    if missing:
        print(f"⚠️  Missing env variables: {', '.join(missing)}")
    else:
        print("✅ All config loaded successfully")
    print(f"🔧 Running in {'🎬 SIMULATION' if IS_SIMULATION else '⚡ REAL'} mode")