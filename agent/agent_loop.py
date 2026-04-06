# agent/agent_loop.py
from agent import state_manager, memory, decision_engine
from agent.risk_checker import analyze_message, validate_transaction
from constants import AgentState
from utils.logger import log

# ──────────────────────────────────────────
# OBSERVE
# reads current context and state
# ──────────────────────────────────────────
def observe(item_id: str) -> dict:
    """
    Observe current state and memory context.
    Returns a snapshot for decision making.
    """
    current_state = state_manager.get_state(item_id)
    mem           = memory.get(item_id)

    observation = {
        "item_id":       item_id,
        "state":         current_state,
        "item_data":     mem.get("item_data"),
        "listing_data":  mem.get("listing_data"),
        "asking_price":  mem.get("asking_price"),
        "min_price":     mem.get("min_price"),
        "buyer_info":    mem.get("buyer_info"),
        "buyer_profile": mem.get("buyer_profile"),
        "current_offer": mem.get("current_offer"),
        "counter_rounds":mem.get("counter_rounds", 0),
        "final_price":   mem.get("final_price"),
        "chat_history":  memory.get_chat_history(item_id),
    }

    log("agent_loop",
        f"[{item_id}] Observed state: {current_state}")
    return observation

# ──────────────────────────────────────────
# DECIDE
# decides what action to take
# ──────────────────────────────────────────
def decide(observation: dict) -> dict:
    """
    Based on observation, decide next action.
    Returns action dict.
    """
    state     = observation["state"]
    item_id   = observation["item_id"]
    item_data = observation.get("item_data", {})

    log("agent_loop", f"[{item_id}] Deciding for state: {state}")

    if state == AgentState.IDLE:
        return {"action": "wait", "reason": "Waiting for item upload"}

    if state == AgentState.ANALYZING:
        return {
            "action": "analyze_item",
            "reason": "Item uploaded, starting analysis"
        }

    if state == AgentState.LISTING:
        return {
            "action": "create_listing",
            "reason": "Analysis complete, creating listing"
        }

    if state == AgentState.WAITING_FOR_BUYER:
        return {
            "action": "wait_for_buyer",
            "reason": "Listing live, monitoring for buyer interest"
        }

    if state == AgentState.NEGOTIATING:
        offer    = observation.get("current_offer")
        asking   = observation.get("asking_price", 0)
        min_p    = observation.get("min_price", 0)
        rounds   = observation.get("counter_rounds", 0)
        profile  = observation.get("buyer_profile")

        if offer:
            action = decision_engine.decide_negotiation_action(
                offer, asking, min_p, rounds, profile
            )
            return action
        return {"action": "wait_for_offer", "reason": "Waiting for buyer offer"}

    if state == AgentState.DEAL_CONFIRMED:
        return {
            "action": "initiate_payment",
            "reason": "Deal confirmed, sending payment link"
        }

    if state == AgentState.AWAITING_PAYMENT:
        return {
            "action": "wait_for_payment",
            "reason": "Payment link sent, waiting for confirmation"
        }

    if state == AgentState.PAYMENT_CONFIRMED:
        return {
            "action": "schedule_pickup",
            "reason": "Payment received, scheduling pickup"
        }

    if state == AgentState.SCHEDULING:
        return {
            "action": "book_courier",
            "reason": "Availability collected, booking Shiprocket"
        }

    if state == AgentState.SHIPPING:
        return {
            "action": "track_shipment",
            "reason": "Item in transit, monitoring delivery"
        }

    if state == AgentState.DELIVERED:
        return {
            "action": "complete",
            "reason": "Item delivered, recording outcome"
        }

    return {"action": "wait", "reason": "Unknown state"}

# ──────────────────────────────────────────
# ACT
# executes the decided action
# ──────────────────────────────────────────
def act(item_id: str, action: dict) -> dict:
    """
    Execute the decided action.
    Returns result of the action.
    """
    action_type = action.get("action")
    log("agent_loop",
        f"[{item_id}] Acting: {action_type} — {action.get('reason')}")

    if action_type == "wait":
        return {"status": "waiting", "message": action.get("reason")}

    if action_type == "analyze_item":
        # trigger analysis pipeline
        return {
            "status":  "triggered",
            "message": "Analysis pipeline started",
            "next":    AgentState.LISTING
        }

    if action_type == "create_listing":
        return {
            "status":  "triggered",
            "message": "Listing creation started",
            "next":    AgentState.WAITING_FOR_BUYER
        }

    if action_type == "auto_accept":
        memory.set(item_id, "final_price",
                   memory.get(item_id, "current_offer"))
        state_manager.transition(item_id, AgentState.DEAL_CONFIRMED)
        return {
            "status":  "deal_confirmed",
            "message": "Offer accepted automatically",
            "next":    AgentState.DEAL_CONFIRMED
        }

    if action_type == "auto_reject":
        return {
            "status":       "rejected",
            "message":      action.get("reason"),
            "counter_price": action.get("counter_price"),
            "next":         AgentState.NEGOTIATING
        }

    if action_type == "counter":
        rounds = memory.get(item_id, "counter_rounds") or 0
        memory.set(item_id, "counter_rounds", rounds + 1)
        return {
            "status":        "counter",
            "message":       action.get("reason"),
            "counter_price": action.get("counter_price"),
            "next":          AgentState.NEGOTIATING
        }

    if action_type == "escalate_to_seller":
        return {
            "status":  "escalated",
            "message": "Waiting for seller decision",
            "offer":   action.get("offer"),
            "next":    AgentState.NEGOTIATING
        }

    if action_type == "initiate_payment":
        state_manager.transition(item_id, AgentState.AWAITING_PAYMENT)
        return {
            "status":  "payment_initiated",
            "message": "Payment link sent to buyer",
            "next":    AgentState.AWAITING_PAYMENT
        }

    if action_type == "schedule_pickup":
        state_manager.transition(item_id, AgentState.SCHEDULING)
        return {
            "status":  "scheduling",
            "message": "Collecting seller availability",
            "next":    AgentState.SCHEDULING
        }

    if action_type == "complete":
        return {
            "status":  "completed",
            "message": "Transaction complete 🎉",
            "next":    AgentState.DELIVERED
        }

    return {"status": "unknown", "message": "Unknown action"}

# ──────────────────────────────────────────
# FULL LOOP TICK
# one complete observe → decide → act cycle
# ──────────────────────────────────────────
def tick(item_id: str) -> dict:
    """
    Run one full agent loop cycle.
    Returns result of the action taken.
    """
    log("agent_loop", f"[{item_id}] ── Tick start ──")

    observation = observe(item_id)
    action      = decide(observation)
    result      = act(item_id, action)

    log("agent_loop",
        f"[{item_id}] ── Tick end: {result.get('status')} ──")
    return result