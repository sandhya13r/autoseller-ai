# services/listing_service.py
from integrations import gemini
from constants import Platform
from utils.logger import log
import config
import json

# ──────────────────────────────────────────
# LISTING GENERATION PROMPT
# ──────────────────────────────────────────
LISTING_PROMPT = """
You are an expert marketplace listing writer.
Create a compelling listing for this second-hand item.

Item Details:
- Title: {title}
- Brand: {brand}
- Model: {model}
- Category: {category}
- Condition: {condition}
- Key Features: {features}
- Selling Points: {selling_points}
- Defects: {defects}
- Price: ₹{price}

Return ONLY this JSON:
{{
    "title": "Compelling listing title (max 60 chars)",
    "description": "3-4 line description highlighting best features, honest about condition, ends with agent link placeholder [AGENT_LINK]",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "highlights": ["highlight1", "highlight2", "highlight3"]
}}
"""

# ──────────────────────────────────────────
# GENERATE LISTING
# ──────────────────────────────────────────
def generate_listing(
    item_data: dict,
    platform: dict,
    asking_price: float,
    item_id: str
) -> dict:
    """
    Generate complete listing for an item.
    Returns listing dict with title, description,
    tags, platform URL.
    """
    log("listing_service",
        f"Generating listing for: {item_data.get('title')}")

    try:
        prompt = LISTING_PROMPT.format(
            title         = item_data.get("title", ""),
            brand         = item_data.get("brand", ""),
            model         = item_data.get("model", ""),
            category      = item_data.get("category", ""),
            condition     = item_data.get("condition", ""),
            features      = ", ".join(item_data.get("key_features", [])),
            selling_points= ", ".join(item_data.get("selling_points", [])),
            defects       = ", ".join(item_data.get("defects_noticed", [])) or "None",
            price         = asking_price
        )

        raw = gemini.generate_json(prompt)
        listing = json.loads(raw)

        # inject agent chat link
        agent_link = f"{config.BASE_URL}/marketplace/{item_id}"
        description = listing.get("description", "")
        description = description.replace(
            "[AGENT_LINK]",
            f"Chat with our AI agent: {agent_link}"
        )
        listing["description"] = description

        # build platform prefilled URL
        listing["platform"]      = platform["name"]
        listing["platform_url"]  = build_platform_url(
            platform, listing, asking_price
        )
        listing["agent_chat_url"] = agent_link
        listing["asking_price"]   = asking_price
        listing["item_id"]        = item_id

        log("listing_service",
            f"✅ Listing generated: {listing.get('title')}",
            "SUCCESS")
        return listing

    except Exception as e:
        log("listing_service",
            f"❌ Listing generation failed: {e}", "ERROR")
        return _fallback_listing(item_data, asking_price, item_id, platform)

# ──────────────────────────────────────────
# BUILD PLATFORM URL
# ──────────────────────────────────────────
def build_platform_url(
    platform: dict,
    listing: dict,
    price: float
) -> str:
    """
    Build prefilled URL for the selected platform.
    """
    base_url = platform.get("url", "")
    title    = listing.get("title", "").replace(" ", "+")
    desc     = listing.get("description", "")[:200].replace(" ", "+")

    if platform["name"] == "OLX":
        return (
            f"{base_url}?"
            f"title={title}&"
            f"description={desc}&"
            f"price={int(price)}"
        )
    elif platform["name"] == "Facebook Marketplace":
        return (
            f"{base_url}?"
            f"title={title}&"
            f"price={int(price)}&"
            f"description={desc}"
        )
    elif platform["name"] == "Quikr":
        return (
            f"{base_url}?"
            f"title={title}&"
            f"price={int(price)}"
        )
    else:
        return base_url

# ──────────────────────────────────────────
# FALLBACK LISTING
# ──────────────────────────────────────────
def _fallback_listing(
    item_data: dict,
    asking_price: float,
    item_id: str,
    platform: dict
) -> dict:
    title = item_data.get("title", "Second-hand Item")
    agent_link = f"{config.BASE_URL}/marketplace/{item_id}"
    return {
        "title":          title,
        "description":    f"{title} in {item_data.get('condition', 'good')} condition. Chat with our AI agent: {agent_link}",
        "tags":           [item_data.get("category", "other")],
        "highlights":     [],
        "platform":       platform.get("name", "OLX"),
        "platform_url":   platform.get("url", ""),
        "agent_chat_url": agent_link,
        "asking_price":   asking_price,
        "item_id":        item_id
    }