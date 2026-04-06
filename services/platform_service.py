# services/platform_service.py
from constants import Platform, Category
from agent import long_term_memory
from utils.logger import log

# ──────────────────────────────────────────
# RECOMMEND PLATFORM
# ──────────────────────────────────────────
def recommend_platform(
    category: str,
    item_data: dict = None
) -> dict:
    """
    Recommend best platform for selling.
    Uses long term memory if available,
    falls back to rule-based logic.
    """
    log("platform_service",
        f"Recommending platform for: {category}")

    # check long term memory first
    learned = long_term_memory.get_best_platform(category)
    if learned:
        for p in Platform.ALL:
            if p["name"] == learned:
                log("platform_service",
                    f"✅ Platform from memory: {p['name']}")
                return p

    # rule based fallback
    platform_map = {
        Category.ELECTRONICS:  Platform.OLX,
        Category.MOBILES:      Platform.OLX,
        Category.FURNITURE:    Platform.FACEBOOK,
        Category.CLOTHING:     Platform.FACEBOOK,
        Category.BOOKS:        Platform.FACEBOOK,
        Category.VEHICLES:     Platform.OLX,
        Category.APPLIANCES:   Platform.OLX,
        Category.SPORTS:       Platform.QUIKR,
        Category.TOYS:         Platform.FACEBOOK,
        Category.OTHER:        Platform.OLX,
    }

    platform = platform_map.get(category, Platform.OLX)
    log("platform_service",
        f"✅ Platform by rule: {platform['name']}")
    return platform

# ──────────────────────────────────────────
# GET ALL PLATFORM OPTIONS
# ──────────────────────────────────────────
def get_all_options(category: str) -> list:
    """
    Get all platform options with
    suitability scores for the category.
    """
    options = []
    for platform in Platform.ALL:
        suitable = category in platform.get("best_for", [])
        options.append({
            "name":          platform["name"],
            "url":           platform["url"],
            "suitable":      suitable,
            "avg_days":      platform.get("avg_days_to_sell", 7),
            "recommended":   category in platform.get("best_for", [])
        })

    # sort — recommended first
    options.sort(key=lambda x: x["recommended"], reverse=True)
    return options

# ──────────────────────────────────────────
# BUILD PREFILLED URL
# ──────────────────────────────────────────
def build_prefilled_url(
    platform: dict,
    title: str,
    description: str,
    price: float
) -> str:
    """Build a prefilled posting URL for platform."""
    import urllib.parse

    base = platform.get("url", "")
    params = urllib.parse.urlencode({
        "title":       title[:60],
        "description": description[:300],
        "price":       int(price)
    })
    return f"{base}?{params}"
