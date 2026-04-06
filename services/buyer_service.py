# services/buyer_service.py
from utils.logger import log

# ──────────────────────────────────────────
# BUYER TYPES
# ──────────────────────────────────────────
class BuyerType:
    SERIOUS    = "serious"      # ready to buy, minimal negotiation
    NEGOTIATOR = "negotiator"   # wants a deal, multiple rounds
    LOWBALLER  = "lowballer"    # unrealistic offers
    BROWSER    = "browser"      # just looking, unlikely to buy
    UNKNOWN    = "unknown"

# ──────────────────────────────────────────
# PROFILE BUYER FROM MESSAGES
# ──────────────────────────────────────────
def profile_buyer(chat_history: list) -> dict:
    """
    Analyze chat history to profile buyer type
    and calculate trust score.
    """
    if not chat_history:
        return _default_profile()

    buyer_messages = [
        m["message"].lower()
        for m in chat_history
        if m["role"] == "buyer"
    ]

    if not buyer_messages:
        return _default_profile()

    trust_score  = 100
    buyer_type   = BuyerType.UNKNOWN
    signals      = []

    # ── serious buyer signals
    serious_keywords = [
        "interested", "i'll take it", "deal",
        "when can i", "available", "condition okay",
        "can we meet", "i want to buy", "confirmed"
    ]

    # ── negotiator signals
    negotiator_keywords = [
        "can you do", "how about", "what's your best",
        "little lower", "discount", "negotiate",
        "final price", "any flexibility"
    ]

    # ── lowballer signals
    lowballer_keywords = [
        "too expensive", "very high", "not worth",
        "half price", "way too much", "overpriced"
    ]

    # ── browser signals
    browser_keywords = [
        "just looking", "checking", "maybe",
        "not sure", "will think", "let me know"
    ]

    serious_count    = 0
    negotiator_count = 0
    lowballer_count  = 0
    browser_count    = 0

    full_text = " ".join(buyer_messages)

    for kw in serious_keywords:
        if kw in full_text:
            serious_count += 1

    for kw in negotiator_keywords:
        if kw in full_text:
            negotiator_count += 1

    for kw in lowballer_keywords:
        if kw in full_text:
            lowballer_count += 1
            trust_score -= 10

    for kw in browser_keywords:
        if kw in full_text:
            browser_count += 1
            trust_score -= 5

    # determine type
    counts = {
        BuyerType.SERIOUS:    serious_count,
        BuyerType.NEGOTIATOR: negotiator_count,
        BuyerType.LOWBALLER:  lowballer_count,
        BuyerType.BROWSER:    browser_count,
    }
    buyer_type = max(counts, key=counts.get)

    # response speed bonus
    if len(buyer_messages) >= 3:
        trust_score += 10
        signals.append("Active conversation — likely serious")

    # clamp trust score
    trust_score = max(0, min(100, trust_score))

    profile = {
        "buyer_type":   buyer_type,
        "trust_score":  trust_score,
        "signals":      signals,
        "message_count": len(buyer_messages),
        "is_serious":   buyer_type in [
            BuyerType.SERIOUS, BuyerType.NEGOTIATOR
        ]
    }

    log("buyer_service",
        f"Buyer profiled: {buyer_type} "
        f"(trust: {trust_score})")
    return profile

# ──────────────────────────────────────────
# EXTRACT OFFER FROM MESSAGE
# ──────────────────────────────────────────
def extract_offer(message: str) -> float | None:
    """
    Extract a price offer from buyer message.
    Returns float or None if no price found.
    """
    import re

    # patterns like ₹5000, Rs 5000, 5000 rupees, 5k
    patterns = [
        r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'(\d+(?:,\d+)*)\s*(?:rupees|rs|inr)',
        r'(\d+)k\b',
        r'\b(\d{4,6})\b'
    ]

    message_lower = message.lower()

    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            value = match.group(1).replace(",", "")
            price = float(value)

            # handle "k" suffix
            if "k" in message_lower[match.start():match.end()]:
                price *= 1000

            # sanity check — between ₹100 and ₹10,00,000
            if 100 <= price <= 1_000_000:
                log("buyer_service",
                    f"Offer extracted: ₹{price}")
                return price

    return None

# ──────────────────────────────────────────
# GET BUYER GREETING
# ──────────────────────────────────────────
def get_greeting(item_data: dict) -> str:
    """Generate personalized buyer greeting."""
    title = item_data.get("title", "this item")
    price = item_data.get("estimated_resale_price", 0)
    condition = item_data.get("condition", "good")

    return (
        f"Hi! 👋 I'm the AI assistant for this listing.\n\n"
        f"📦 *{title}*\n"
        f"💰 Asking price: ₹55,902\n"
        f"✅ Condition: {condition.replace('_', ' ').title()}\n\n"
        f"I can answer your questions, negotiate the price, "
        f"and help you complete the purchase securely. "
        f"What would you like to know?"
    )

# ──────────────────────────────────────────
# DEFAULT PROFILE
# ──────────────────────────────────────────
def _default_profile() -> dict:
    return {
        "buyer_type":    BuyerType.UNKNOWN,
        "trust_score":   70,
        "signals":       [],
        "message_count": 0,
        "is_serious":    False
    }