# utils/helpers.py
import uuid
import re
from datetime import datetime

def generate_id() -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4())[:8].upper()

def format_price(amount: float) -> str:
    """Format price in Indian style ₹1,00,000"""
    return f"₹{int(amount):,}"

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def time_ago(dt: datetime) -> str:
    """Return human readable time difference."""
    diff = datetime.now() - dt
    if diff.seconds < 60:
        return "just now"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60}m ago"
    elif diff.days < 1:
        return f"{diff.seconds // 3600}h ago"
    else:
        return f"{diff.days}d ago"

def is_valid_phone(phone: str) -> bool:
    """Validate Indian phone number."""
    clean = re.sub(r'[\s\-\+]', '', phone)
    return bool(re.match(r'^[6-9]\d{9}$', clean))

def is_valid_email(email: str) -> bool:
    """Validate email address."""
    return bool(re.match(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        email
    ))

def truncate(text: str, length: int = 100) -> str:
    """Truncate text to length."""
    if len(text) <= length:
        return text
    return text[:length - 3] + "..."

def price_to_paise(price: float) -> int:
    """Convert rupees to paise for Razorpay."""
    return int(price * 100)

def paise_to_price(paise: int) -> float:
    """Convert paise to rupees."""
    return paise / 100
