# simulations/fake_market.py
from utils.logger import log
from datetime import datetime, timedelta
import random

# ──────────────────────────────────────────
# FAKE COMPETING LISTINGS
# ──────────────────────────────────────────
COMPETING_LISTINGS = [
    {
        "title":    "iPhone 13 128GB — Excellent Condition",
        "price":    45000,
        "platform": "OLX",
        "days_ago": 2,
        "views":    47
    },
    {
        "title":    "Apple iPhone 13 — With Box",
        "price":    43500,
        "platform": "OLX",
        "days_ago": 5,
        "views":    32
    },
    {
        "title":    "iPhone 13 128GB Blue",
        "price":    41000,
        "platform": "Facebook",
        "days_ago": 1,
        "views":    28
    },
    {
        "title":    "iPhone 13 — Urgent Sale",
        "price":    39000,
        "platform": "OLX",
        "days_ago": 7,
        "views":    89
    }
]

# ──────────────────────────────────────────
# FAKE BUYER ARRIVALS
# ──────────────────────────────────────────
FAKE_BUYERS = [
    {
        "name":        "Rahul M.",
        "type":        "serious",
        "trust_score": 85,
        "arrives_in":  3    # seconds
    },
    {
        "name":        "Priya S.",
        "type":        "negotiator",
        "trust_score": 72,
        "arrives_in":  8
    },
    {
        "name":        "Vikram K.",
        "type":        "serious",
        "trust_score": 91,
        "arrives_in":  15
    }
]

# ──────────────────────────────────────────
# GET MARKET DATA
# ──────────────────────────────────────────
def get_market_data(category: str, item_title: str) -> dict:
    """
    Return fake market data for demo display.
    Shows competing listings and demand signals.
    """
    log("fake_market",
        f"🎬 Generating market data for {item_title}")

    return {
        "competing_listings": COMPETING_LISTINGS,
        "demand_level":       "High",
        "avg_selling_price":  42000,
        "avg_days_to_sell":   4,
        "total_similar":      len(COMPETING_LISTINGS),
        "price_trend":        "stable",
        "recommendation":     (
            "Priced competitively. "
            "High demand — likely to sell within 3-5 days."
        )
    }

# ──────────────────────────────────────────
# GET NEXT FAKE BUYER
# ──────────────────────────────────────────
def get_next_buyer() -> dict:
    """Get next simulated buyer for demo."""
    buyer = random.choice(FAKE_BUYERS)
    log("fake_market",
        f"🎬 Next buyer: {buyer['name']} ({buyer['type']})")
    return buyer

# ──────────────────────────────────────────
# GET LISTING STATS (for marketplace page)
# ──────────────────────────────────────────
def get_listing_stats(item_id: str) -> dict:
    """Return fake listing performance stats."""
    return {
        "views":       random.randint(12, 48),
        "interested":  random.randint(2, 8),
        "saved":       random.randint(1, 5),
        "listed_at":   datetime.now().strftime("%B %d, %Y"),
        "expires_at":  (
            datetime.now() + timedelta(days=30)
        ).strftime("%B %d, %Y")
    }
