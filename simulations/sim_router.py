# simulations/sim_router.py
from utils.logger import log
from datetime import datetime

# ──────────────────────────────────────────
# FAKE ANALYSIS
# ──────────────────────────────────────────
def fake_analysis(image_path: str) -> dict:
    """
    Return a realistic fake item analysis
    for simulation mode.
    """
    log("sim_router", "🎬 Returning fake item analysis")
    return {
        "title":                  "Apple iPhone 13 128GB",
        "brand":                  "Apple",
        "model":                  "iPhone 13",
        "category":               "mobiles",
        "condition":              "good",
        "condition_reason":       "Minor scratches on back, screen in perfect condition",
        "key_features":           [
            "128GB Storage",
            "A15 Bionic Chip",
            "Dual Camera 12MP",
            "5G Enabled",
            "Battery health 89%"
        ],
        "estimated_original_price": 79900,
        "estimated_resale_price":   50820,
        "min_acceptable_price":     48000,
        "max_asking_price":         50820,
        "currency":                 "INR",
        "selling_points":           [
            "Original box included",
            "All accessories present",
            "Face ID working perfectly"
        ],
        "defects_noticed":          ["Minor scratch on back panel"],
        "confidence_score":         0.95
    }

# ──────────────────────────────────────────
# FAKE LISTING
# ──────────────────────────────────────────
def fake_listing(item_data, platform, asking_price, item_id="SIM001"):
    import config
    log("sim_router", "🎬 Returning fake listing")
    agent_link = f"{config.BASE_URL}/marketplace/{item_id}"
    title = item_data.get('title', 'Apple iPhone 13 128GB')
    condition = item_data.get('condition', 'good')
    return {
        "title":       f"{title} — {condition.title()} Condition",
        "description": (
            f"Selling my {title} in {condition} condition. "
            f"All accessories included, original box present. "
            f"Battery health 89%. Minor scratch on back panel. "
            f"Serious buyers only. "
            f"Chat with our AI agent: {agent_link}"
        ),
        "tags":           ["iPhone", "Apple", "Mobile", "Smartphone", "5G"],
        "highlights":     item_data.get("selling_points", []),
        "platform":       platform.get("name", "OLX"),
        "platform_url":   platform.get("url", ""),
        "agent_chat_url": agent_link,
        "asking_price":   asking_price,
        "item_id":        item_id
    }
# ──────────────────────────────────────────
# FAKE NEGOTIATION REPLY
# ──────────────────────────────────────────
def fake_negotiation_reply(
    item_id: str,
    buyer_message: str
) -> dict:
    """
    Route to fake_chat for scripted replies
    in simulation mode.
    """
    from simulations.fake_chat import get_scripted_reply
    return get_scripted_reply(item_id, buyer_message)

# ──────────────────────────────────────────
# FAKE TRACKING STATUS
# ──────────────────────────────────────────
def fake_tracking_status(item_id: str) -> dict:
    """
    Route to fake_tracking for status updates
    in simulation mode.
    """
    from simulations.fake_tracking import get_status
    return get_status(item_id)

# ──────────────────────────────────────────
# FAKE PAYMENT CONFIRM
# ──────────────────────────────────────────
def fake_payment_confirm(item_id: str) -> dict:
    """Instantly confirm payment in sim mode."""
    log("sim_router",
        f"🎬 Fake payment confirmed for {item_id}")
    return {
        "success":    True,
        "payment_id": f"sim_pay_{item_id[:8]}",
        "message":    "Payment confirmed! 🎉"
    }

# ──────────────────────────────────────────
# FAKE SHIPMENT
# ──────────────────────────────────────────
def fake_shipment(item_id: str) -> dict:
    """Return fake shipment details."""
    log("sim_router",
        f"🎬 Fake shipment created for {item_id}")
    from datetime import timedelta
    return {
        "success":            True,
        "order_id":           f"sim_ship_{item_id[:8]}",
        "awb":                f"AWB{item_id[:8].upper()}",
        "courier":            "Delhivery",
        "tracking_url":       f"https://shiprocket.co/tracking/AWB{item_id[:8].upper()}",
        "estimated_delivery": (
            datetime.now() + timedelta(days=3)
        ).strftime("%B %d, %Y")
    }