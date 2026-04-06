# services/pricing_service.py
from integrations import gemini
from constants import Condition, CONDITION_MULTIPLIER, Category
from utils.logger import log
import json

# ──────────────────────────────────────────
# ESTIMATE PRICE FROM GEMINI
# ──────────────────────────────────────────
def estimate_price(item_data: dict) -> dict:
    """
    Estimate fair resale price using
    Gemini + condition multipliers.
    """
    log("pricing_service",
        f"Estimating price for: {item_data.get('title')}")

    try:
        prompt = f"""
You are an expert in Indian second-hand market pricing.
Estimate the resale price for this item.

Item: {item_data.get('title')}
Brand: {item_data.get('brand')}
Model: {item_data.get('model')}
Category: {item_data.get('category')}
Condition: {item_data.get('condition')}
Features: {', '.join(item_data.get('key_features', []))}
Defects: {', '.join(item_data.get('defects_noticed', [])) or 'None'}

Return ONLY this JSON:
{{
    "original_price":   0,
    "resale_price":     0,
    "min_price":        0,
    "max_price":        0,
    "price_reasoning":  "one line explanation",
    "market_demand":    "high/medium/low",
    "currency":         "INR"
}}

Be realistic with Indian market prices.
"""
        raw  = gemini.generate_json(prompt)
        data = json.loads(raw)

        # apply condition multiplier as sanity check
        condition  = item_data.get("condition", Condition.GOOD)
        multiplier = CONDITION_MULTIPLIER.get(condition, 0.60)
        original   = data.get("original_price", 0)

        # if Gemini gave unrealistic prices, recalculate
        if data.get("resale_price", 0) > original:
            data["resale_price"] = round(original * multiplier)
        if data.get("min_price", 0) <= 0:
            data["min_price"] = round(original * multiplier * 0.80)
        if data.get("max_price", 0) <= 0:
            data["max_price"] = round(original * multiplier * 1.10)

        log("pricing_service",
            f"✅ Price estimated: ₹{data.get('resale_price')} "
            f"(demand: {data.get('market_demand')})",
            "SUCCESS")
        return data

    except Exception as e:
        log("pricing_service",
            f"❌ Price estimation failed: {e}", "ERROR")
        # fallback to condition-based calculation
        return _fallback_price(item_data)

# ──────────────────────────────────────────
# CALCULATE COUNTER OFFER
# ──────────────────────────────────────────
def calculate_counter(
    asking_price: float,
    buyer_offer: float,
    round_number: int
) -> float:
    """
    Calculate a smart counter offer price.
    Gets more flexible as rounds increase.
    """
    # gap between asking and offer
    gap = asking_price - buyer_offer

    # each round we concede more
    concession_rates = [0.10, 0.20, 0.30]
    rate = concession_rates[min(round_number, 2)]

    counter = asking_price - (gap * rate)
    counter = round(counter / 100) * 100  # round to nearest 100

    log("pricing_service",
        f"Counter offer: ₹{asking_price} → ₹{counter} "
        f"(round {round_number + 1})")
    return counter

# ──────────────────────────────────────────
# FALLBACK
# ──────────────────────────────────────────
def _fallback_price(item_data: dict) -> dict:
    condition  = item_data.get("condition", Condition.GOOD)
    multiplier = CONDITION_MULTIPLIER.get(condition, 0.60)
    base       = 5000  # default base if unknown

    return {
        "original_price":  base,
        "resale_price":    round(base * multiplier),
        "min_price":       round(base * multiplier * 0.80),
        "max_price":       round(base * multiplier * 1.10),
        "price_reasoning": "Estimated based on condition",
        "market_demand":   "medium",
        "currency":        "INR"
    }