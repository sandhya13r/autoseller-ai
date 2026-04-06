# utils/explain.py
from utils.logger import log

# ──────────────────────────────────────────
# EXPLAIN AGENT DECISIONS
# trust layer — tells user WHY agent did what
# ──────────────────────────────────────────
def explain_decision(
    action: str,
    value: float = None,
    reference: float = None
) -> str:
    """
    Generate human-readable explanation
    for every agent decision.
    """
    explanations = {
        "auto_accept": (
            f"✅ Auto-accepted because offer "
            f"₹{int(value):,} is {round(value/reference*100)}% "
            f"of asking price — above our 95% threshold."
        ),
        "auto_reject": (
            f"❌ Auto-rejected because offer "
            f"₹{int(value):,} is below our minimum "
            f"acceptable threshold of 60%."
        ),
        "counter": (
            f"💬 Counter-offered at ₹{int(value):,} — "
            f"calculated to find middle ground while "
            f"protecting seller's minimum margin."
        ),
        "platform_selected": (
            f"📱 Platform selected based on category "
            f"performance data and historical sell rates."
        ),
        "price_set": (
            f"💰 Asking price ₹{int(value):,} set at 10% above "
            f"estimated resale value to allow negotiation room."
        ),
        "risk_blocked": (
            f"⛔ Interaction blocked due to suspicious "
            f"patterns detected in buyer message."
        ),
        "deal_confirmed": (
            f"🤝 Deal confirmed at ₹{int(value):,} — "
            f"{round(value/reference*100)}% of asking price. "
            f"Within acceptable range."
        ),
        "escalated": (
            f"⏫ Escalated to seller — maximum negotiation "
            f"rounds reached without agreement."
        )
    }

    explanation = explanations.get(
        action,
        f"Agent took action: {action}"
    )

    log("explain", explanation)
    return explanation

# ──────────────────────────────────────────
# EXPLAIN STATE TRANSITION
# ──────────────────────────────────────────
def explain_state(
    old_state: str,
    new_state: str,
    context: dict = None
) -> str:
    """Explain why agent moved to a new state."""
    explanation = (
        f"Agent moved from [{old_state}] to [{new_state}]"
    )
    if context:
        reason = context.get("reason", "")
        if reason:
            explanation += f" — {reason}"

    log("explain", explanation)
    return explanation

# ──────────────────────────────────────────
# EXPLAIN FULL PIPELINE
# shown on dashboard
# ──────────────────────────────────────────
def explain_pipeline(item_id: str, mem: dict) -> list:
    """
    Generate a full explanation timeline
    of all agent decisions for dashboard.
    """
    steps = []

    if mem.get("item_data"):
        item = mem["item_data"]
        steps.append({
            "icon":    "🔍",
            "title":   "Item Analyzed",
            "detail":  f"Identified as {item.get('brand')} {item.get('model')} in {item.get('condition')} condition"
        })

    if mem.get("asking_price"):
        steps.append({
            "icon":   "💰",
            "title":  "Price Set",
            "detail": f"Asking price ₹{int(mem['asking_price']):,} based on market analysis"
        })

    if mem.get("platform"):
        platform = mem["platform"]
        steps.append({
            "icon":   "📱",
            "title":  "Platform Selected",
            "detail": f"{platform.get('name')} recommended for this category"
        })

    if mem.get("final_price"):
        steps.append({
            "icon":   "🤝",
            "title":  "Deal Confirmed",
            "detail": f"Final price ₹{int(mem['final_price']):,} agreed after negotiation"
        })

    if mem.get("payment_status") == "confirmed":
        steps.append({
            "icon":   "✅",
            "title":  "Payment Confirmed",
            "detail": "Full payment received securely via Razorpay"
        })

    if mem.get("awb"):
        steps.append({
            "icon":   "🚚",
            "title":  "Shipment Booked",
            "detail": f"AWB {mem['awb']} via {mem.get('courier', 'courier')}"
        })

    from agent.state_manager import get_state
    from constants import AgentState
    if get_state(item_id) == AgentState.DELIVERED:
       steps.append({
        "icon":   "🎉",
        "title":  "Delivered",
        "detail": "Item delivered to buyer successfully"
    })

    return steps