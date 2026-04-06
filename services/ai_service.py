# services/ai_service.py
import json
from integrations import gemini
from constants import Category, Condition, CONDITION_MULTIPLIER
from utils.logger import log  # type: ignore

# ──────────────────────────────────────────
# ITEM ANALYSIS PROMPT
# ──────────────────────────────────────────
ITEM_ANALYSIS_PROMPT = """
You are an expert product analyst for a second-hand marketplace.
Analyze this item image and return a detailed JSON response.

Return ONLY this JSON structure:
{
    "title": "Short compelling product title (max 60 chars)",
    "brand": "Brand name or 'Unknown'",
    "model": "Model name/number or 'Unknown'",
    "category": "One of: electronics, mobiles, furniture, clothing, books, vehicles, appliances, sports, toys, other",
    "condition": "One of: brand_new, like_new, good, fair, poor",
    "condition_reason": "One sentence explaining condition assessment",
    "key_features": ["feature1", "feature2", "feature3"],
    "estimated_original_price": 0,
    "estimated_resale_price": 0,
    "min_acceptable_price": 0,
    "max_asking_price": 0,
    "currency": "INR",
    "selling_points": ["point1", "point2", "point3"],
    "defects_noticed": ["defect1"] or [],
    "confidence_score": 0.0
}

Be realistic with Indian market prices in INR.
confidence_score is 0.0 to 1.0 based on how clearly you can see the item.
"""

# ──────────────────────────────────────────
# ANALYZE ITEM FROM IMAGE
# ──────────────────────────────────────────
def analyze_item(image_path: str) -> dict:
    """
    Analyze uploaded item image using Gemini vision.
    Returns structured item data.
    """
    log("ai_service", f"Analyzing image: {image_path}")

    try:
        raw_json = gemini.analyze_image(image_path, ITEM_ANALYSIS_PROMPT)
        # clean and parse
        raw_json = raw_json.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
        raw_json = raw_json.strip()

        data = json.loads(raw_json)

        # apply condition multiplier to validate price
        condition = data.get("condition", Condition.GOOD)
        original  = data.get("estimated_original_price", 0)
        multiplier = CONDITION_MULTIPLIER.get(condition, 0.60)

        # recalculate if Gemini missed it
        if not data.get("estimated_resale_price"):
            data["estimated_resale_price"] = round(original * multiplier)
        if not data.get("min_acceptable_price"):
            data["min_acceptable_price"] = round(original * multiplier * 0.80)
        if not data.get("max_asking_price"):
            data["max_asking_price"] = round(original * multiplier * 1.10)

        log("ai_service", f"✅ Analysis complete: {data.get('title')} | ₹{data.get('estimated_resale_price')}")
        return data

    except json.JSONDecodeError as e:
        log("ai_service", f"❌ JSON parse error: {e}")
        return _fallback_analysis()
    except Exception as e:
        log("ai_service", f"❌ Analysis failed: {e}")
        return _fallback_analysis()

# ──────────────────────────────────────────
# ENHANCE DESCRIPTION
# ──────────────────────────────────────────
def enhance_description(item_data: dict, raw_description: str = "") -> str:
    """
    Generate a compelling marketplace description
    from item analysis data.
    """
    log("ai_service", "Enhancing item description")

    prompt = f"""
You are a marketplace listing expert. Write a compelling product description.

Item Details:
- Title: {item_data.get('title')}
- Brand: {item_data.get('brand')}
- Model: {item_data.get('model')}
- Condition: {item_data.get('condition')}
- Key Features: {', '.join(item_data.get('key_features', []))}
- Selling Points: {', '.join(item_data.get('selling_points', []))}
- Defects: {', '.join(item_data.get('defects_noticed', [])) or 'None'}
- Seller's notes: {raw_description or 'None provided'}

Write a 3-4 line description that:
1. Highlights the best features
2. Is honest about condition
3. Creates urgency to buy
4. Ends with the agent chat link placeholder: [AGENT_LINK]

Keep it under 150 words. Natural, not salesy.
    """
    try:
        description = gemini.generate_text(prompt)
        log("ai_service", "✅ Description enhanced")
        return description
    except Exception as e:
        log("ai_service", f"❌ Description enhancement failed: {e}")
        return f"{item_data.get('title')} - {item_data.get('condition')} condition. [AGENT_LINK]"

# ──────────────────────────────────────────
# ANSWER BUYER QUESTION ABOUT ITEM
# ──────────────────────────────────────────
def answer_item_question(item_data: dict, question: str) -> str:
    """
    Answer a buyer's question about the item using Gemini.
    """
    prompt = f"""
You are a helpful selling assistant. Answer this buyer question about the item.

Item: {item_data.get('title')}
Brand: {item_data.get('brand')}
Condition: {item_data.get('condition')} — {item_data.get('condition_reason')}
Features: {', '.join(item_data.get('key_features', []))}
Defects: {', '.join(item_data.get('defects_noticed', [])) or 'None'}

Buyer Question: {question}

Answer honestly and helpfully in 1-2 sentences.
If you don't know something specific, say so honestly.
    """
    try:
        answer = gemini.generate_text(prompt)
        return answer.strip()
    except Exception as e:
        log("ai_service", f"❌ Question answering failed: {e}")
        return "I'll need to check with the seller on that. Please ask via chat."

# ──────────────────────────────────────────
# FALLBACK
# ──────────────────────────────────────────
def _fallback_analysis() -> dict:
    """Returns a safe fallback if AI analysis fails."""
    return {
        "title": "Second-hand Item",
        "brand": "Unknown",
        "model": "Unknown",
        "category": Category.OTHER,
        "condition": Condition.GOOD,
        "condition_reason": "Unable to analyze image",
        "key_features": [],
        "estimated_original_price": 0,
        "estimated_resale_price": 0,
        "min_acceptable_price": 0,
        "max_asking_price": 0,
        "currency": "INR",
        "selling_points": [],
        "defects_noticed": [],
        "confidence_score": 0.0
    }