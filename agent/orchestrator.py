# agent/orchestrator.py
from agent import memory, state_manager, agent_loop
from agent.decision_engine import decide_platform, decide_asking_price
from agent.feedback_engine import get_pricing_adjustment
from services import ai_service, listing_service, pricing_service
from constants import AgentState
from utils.logger import log

# ──────────────────────────────────────────
# START SELLING PIPELINE
# entry point when user uploads an item
# ──────────────────────────────────────────
def start_pipeline(item_id: str, image_path: str) -> dict:
    import config as cfg  # fresh import so IS_SIMULATION reflects live toggle
    import traceback

    log("orchestrator", f"🚀 Pipeline started for item: {item_id}")
    log("orchestrator", f"Mode: {'SIMULATION' if cfg.IS_SIMULATION else 'REAL'}")

    # 1. initialize memory and state
    memory.init(item_id)
    state_manager.create_session(item_id)
    state_manager.transition(item_id, AgentState.ANALYZING)

    try:
        # 2. analyze item with AI
        log("orchestrator", "Step 1: Analyzing item image")
        if cfg.IS_SIMULATION:
            from simulations.sim_router import fake_analysis
            item_data = fake_analysis(image_path)
            log("orchestrator", f"✅ Sim analysis: {item_data.get('title')}")
        else:
            item_data = ai_service.analyze_item(image_path)
            log("orchestrator", f"✅ Real analysis: {item_data.get('title')}")

        memory.set(item_id, "item_data", item_data)

        # 3. decide platform
        log("orchestrator", "Step 2: Deciding platform")
        category = item_data.get("category", "other")
        platform = decide_platform(category)

        # 4. decide pricing with feedback adjustment
        log("orchestrator", "Step 3: Calculating optimal price")
        base_price = item_data.get("estimated_resale_price", 0)

        # fallback price if analysis returned 0
        if base_price == 0:
            base_price = 42000 if cfg.IS_SIMULATION else 5000
            log("orchestrator", f"⚠️ Price was 0, using fallback: ₹{base_price}", "WARN")

        pricing    = decide_asking_price(base_price, category, platform["name"])
        adjustment = get_pricing_adjustment(category, platform["name"], pricing["asking_price"])

        asking_price = adjustment["adjusted_price"]
        min_price    = pricing["min_price"]

        # safety: never allow 0 prices
        if asking_price == 0:
            asking_price = base_price
        if min_price == 0:
            min_price = round(base_price * 0.75)

        memory.update(item_id, {
            "platform":     platform,
            "asking_price": asking_price,
            "min_price":    min_price
        })

        # 5. generate listing
        log("orchestrator", "Step 4: Generating listing")
        state_manager.transition(item_id, AgentState.LISTING)

        if cfg.IS_SIMULATION:
            from simulations.sim_router import fake_listing
            listing_data = fake_listing(item_data, platform, asking_price,item_id)
        else:
            listing_data = listing_service.generate_listing(
                item_data, platform, asking_price, item_id
            )

        memory.set(item_id, "listing_data", listing_data)

        # 6. move to waiting for buyer
        state_manager.transition(item_id, AgentState.WAITING_FOR_BUYER)

        log("orchestrator",
            f"✅ Pipeline complete — {platform['name']} @ ₹{asking_price}",
            "SUCCESS")

        return {
            "success":      True,
            "item_id":      item_id,
            "item_data":    item_data,
            "listing_data": listing_data,
            "platform":     platform,
            "asking_price": asking_price,
            "min_price":    min_price,
            "state":        AgentState.WAITING_FOR_BUYER
        }

    except Exception as e:
        log("orchestrator", f"❌ Pipeline failed: {e}", "ERROR")
        traceback.print_exc()
        state_manager.transition(item_id, AgentState.IDLE)
        return {
            "success": False,
            "error":   str(e),
            "item_id": item_id
        }


# ──────────────────────────────────────────
# HANDLE BUYER MESSAGE
# ──────────────────────────────────────────
def handle_buyer_message(item_id: str, message: str) -> dict:
    import config as cfg  # fresh import

    log("orchestrator", f"[{item_id}] Buyer message: {message[:50]}...")

    memory.add_chat_message(item_id, "buyer", message)

    current = state_manager.get_state(item_id)
    if current == AgentState.WAITING_FOR_BUYER:
        state_manager.transition(item_id, AgentState.NEGOTIATING)

    if cfg.IS_SIMULATION:
        from simulations.sim_router import fake_negotiation_reply
        reply = fake_negotiation_reply(item_id, message)
    else:
        from services.negotiation_service import get_reply
        reply = get_reply(item_id, message)

    memory.add_chat_message(item_id, "agent", reply["message"])
    return reply


# ──────────────────────────────────────────
# CONFIRM DEAL
# ──────────────────────────────────────────
def confirm_deal(item_id: str, final_price: float) -> dict:
    log("orchestrator", f"[{item_id}] Deal confirmed at ₹{final_price}")

    memory.set(item_id, "final_price", final_price)
    memory.set(item_id, "payment_status", "pending")
    state_manager.transition(item_id, AgentState.DEAL_CONFIRMED)
    state_manager.transition(item_id, AgentState.AWAITING_PAYMENT)
    memory.update(item_id, {
    "final_price":    final_price,
    "payment_status": "pending"
})
    return {
        "success":     True,
        "final_price": final_price,
        "state":       AgentState.AWAITING_PAYMENT,
        "message":     "Deal confirmed! Payment link will be sent."
    }


# ──────────────────────────────────────────
# CONFIRM PAYMENT
# ──────────────────────────────────────────
def confirm_payment(item_id: str, payment_id: str) -> dict:
    log("orchestrator", f"[{item_id}] Payment confirmed: {payment_id}", "SUCCESS")

    memory.update(item_id, {
        "payment_id":     payment_id,
        "payment_status": "confirmed"
    })

    # correct sequence through state machine
    state_manager.transition(item_id, AgentState.AWAITING_PAYMENT)
    state_manager.transition(item_id, AgentState.PAYMENT_CONFIRMED)
    state_manager.transition(item_id, AgentState.SCHEDULING)

    return {
        "success":    True,
        "payment_id": payment_id,
        "state":      AgentState.SCHEDULING,
        "message":    "Payment confirmed! Please share your availability."
    }

# ──────────────────────────────────────────
# CONFIRM DELIVERY
# ──────────────────────────────────────────
def confirm_delivery(item_id: str) -> dict:
    log("orchestrator", f"[{item_id}] Delivery confirmed 🎉", "SUCCESS")

    state_manager.transition(item_id, AgentState.DELIVERED)

    mem = memory.get(item_id)
    from agent.feedback_engine import process_outcome
    from datetime import datetime

    try:
        process_outcome(
            item_id      = item_id,
            category     = mem.get("item_data", {}).get("category", "other"),
            platform     = mem.get("platform", {}).get("name", "OLX"),
            asking_price = mem.get("asking_price", 0),
            final_price  = mem.get("final_price", 0),
            created_at   = datetime.fromisoformat(mem.get("created_at")),
            delivered_at = datetime.now(),
            success      = True
        )
    except Exception as e:
        log("orchestrator", f"⚠️ Feedback recording failed: {e}", "WARN")

    return {
        "success": True,
        "state":   AgentState.DELIVERED,
        "message": "🎉 Item delivered successfully!"
    }