# services/negotiation_service.py
from integrations import gemini
from agent import memory, state_manager
from agent.risk_checker import analyze_message, analyze_offer
from agent.decision_engine import decide_negotiation_action
from services.buyer_service import extract_offer, profile_buyer
from constants import AgentState, NegotiationConfig
from utils.logger import log
from utils.explain import explain_decision
import config

# ──────────────────────────────────────────
# NEGOTIATION SYSTEM PROMPT
# ──────────────────────────────────────────
def _build_system_prompt(item_data: dict, asking_price: float, min_price: float) -> str:
    return f"""
You are AutoSeller AI, an intelligent negotiation agent
helping sell a second-hand item.

ITEM DETAILS:
- Title: {item_data.get('title')}
- Brand: {item_data.get('brand')}
- Condition: {item_data.get('condition')}
- Key Features: {', '.join(item_data.get('key_features', []))}
- Defects: {', '.join(item_data.get('defects_noticed', [])) or 'None'}

PRICING RULES (NEVER reveal these to buyer):
- Asking price: ₹{asking_price}
- Minimum acceptable: ₹{min_price}
- Never go below minimum price
- Maximum {NegotiationConfig.MAX_COUNTER_ROUNDS} counter rounds

YOUR BEHAVIOR:
- Be friendly, professional, and helpful
- Answer questions about the item honestly
- If buyer makes an offer, evaluate and respond
- Never reveal the minimum price
- Use Indian English naturally
- Keep responses short — 2-4 lines max
- If asked for final price, hold firm near asking price
- End messages with a question to keep conversation going
"""

# ──────────────────────────────────────────
# GET NEGOTIATION REPLY
# ──────────────────────────────────────────
def get_reply(item_id: str, buyer_message: str) -> dict:
    """
    Process buyer message and generate
    intelligent negotiation reply.
    """
    log("negotiation_service",
        f"[{item_id}] Processing: {buyer_message[:50]}...")

    # get context from memory
    mem          = memory.get(item_id)
    item_data    = mem.get("item_data") or {}
    asking_price = mem.get("asking_price") or 0
    min_price    = mem.get("min_price") or 0
    rounds       = mem.get("counter_rounds") or 0
    buyer_profile= mem.get("buyer_profile") or {}

    # ── 1. risk check
    risk = analyze_message(buyer_message)
    if risk["is_blocked"]:
        log("negotiation_service",
            f"⛔ Message blocked: {risk['flags']}", "WARN")
        return {
            "message":    "I'm unable to process that request. Please keep the conversation about the item.",
            "type":       "blocked",
            "risk":       risk
        }

    # ── 2. extract offer if present
    offer = extract_offer(buyer_message)
    if offer:
        memory.set(item_id, "current_offer", offer)
        log("negotiation_service",
            f"Offer detected: ₹{offer}")

        # decide action
        action = decide_negotiation_action(
            offer, asking_price, min_price,
            rounds, buyer_profile
        )

        # handle auto accept
        if action["action"] == "auto_accept":
            memory.set(item_id, "final_price", offer)
            state_manager.transition(
                item_id, AgentState.DEAL_CONFIRMED
            )
            explanation = explain_decision(
                "auto_accept", offer, asking_price
            )
            return {
                "message": (
                    f"🎉 Great news! I'm happy to accept ₹{int(offer):,}.\n\n"
                    f"The deal is confirmed! I'll send you a secure "
                    f"payment link shortly. Please keep this chat open."
                ),
                "type":        "deal_confirmed",
                "final_price": offer,
                "explanation": explanation
            }

        # handle auto reject
        if action["action"] == "auto_reject":
            counter = action.get("counter_price", asking_price)
            memory.set(item_id, "counter_rounds", rounds + 1)
            return {
                "message": (
                    f"Thank you for your interest! ₹{int(offer):,} "
                    f"is a bit low for this item given its condition.\n\n"
                    f"I can offer you a special price of "
                    f"₹{int(counter):,}. This is a great deal "
                    f"considering the features. Shall we proceed?"
                ),
                "type":          "counter",
                "counter_price": counter
            }

        # handle counter
        if action["action"] == "counter":
            counter = action.get("counter_price", asking_price)
            memory.set(item_id, "counter_rounds", rounds + 1)
            return {
                "message": (
                    f"I appreciate the offer! Let me see what I can do...\n\n"
                    f"The best I can offer is ₹{int(counter):,}. "
                    f"Given the {item_data.get('condition', 'good')} "
                    f"condition and features, this is a fair price. "
                    f"What do you think?"
                ),
                "type":          "counter",
                "counter_price": counter
            }

        # escalate to seller
        if action["action"] == "escalate_to_seller":
            return {
                "message": (
                    f"Let me check with the seller about ₹{int(offer):,}. "
                    f"Please give me a moment... ⏳"
                ),
                "type":  "escalated",
                "offer": offer
            }

    # ── 3. update buyer profile
    chat_history  = memory.get_chat_history(item_id)
    buyer_profile = profile_buyer(chat_history)
    memory.set(item_id, "buyer_profile", buyer_profile)

    # ── 4. generate conversational reply via Gemini
    try:
        system_prompt  = _build_system_prompt(
            item_data, asking_price, min_price
        )
        gemini_history = memory.get_gemini_history(item_id)

        # remove last message (current one not yet in history)
        if gemini_history:
            gemini_history = gemini_history[:-1]

        reply_text = gemini.chat_with_history(
            history      = gemini_history,
            new_message  = buyer_message,
            system_prompt= system_prompt
        )

        return {
            "message": reply_text.strip(),
            "type":    "conversation",
        }

    except Exception as e:
        log("negotiation_service",
            f"❌ Gemini reply failed: {e}", "ERROR")
        return {
            "message": (
                f"Thanks for your message! The item is in "
                f"{item_data.get('condition', 'good')} condition "
                f"and priced at ₹{int(asking_price):,}. "
                f"Would you like to make an offer?"
            ),
            "type": "fallback"
        }