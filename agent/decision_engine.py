# agent/decision_engine.py
from constants import (
    NegotiationConfig, Platform,
    Category, AgentState
)
from agent import long_term_memory
from agent.risk_checker import analyze_offer
from utils.logger import log

# ──────────────────────────────────────────
# DECIDE PLATFORM
# ──────────────────────────────────────────
def decide_platform(category: str) -> dict:
    """
    Decide best platform for selling based on
    category + long term memory data.
    """
    # first check long term memory
    learned_platform = long_term_memory.get_best_platform(category)

    if learned_platform:
        # find full platform data
        for p in Platform.ALL:
            if p["name"] == learned_platform:
                log("decision_engine",
                    f"Platform from memory: {p['name']} for {category}")
                return p

    # fallback to rule-based logic
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
    log("decision_engine",
        f"Platform by rule: {platform['name']} for {category}")
    return platform

# ──────────────────────────────────────────
# DECIDE ASKING PRICE
# ──────────────────────────────────────────
def decide_asking_price(
    estimated_price: float,
    category: str,
    platform_name: str
) -> dict:
    """
    Decide optimal asking price and min acceptable price.
    Uses long term memory ratio if available.
    """
    # get historical ratio for this category+platform
    expected_ratio = long_term_memory.get_expected_price_ratio(
        category, platform_name
    )

    # set asking price slightly above estimated
    # to leave room for negotiation
    asking_price = round(estimated_price * 1.10)

    # min price based on negotiation config
    min_price = round(
        estimated_price * NegotiationConfig.MIN_PROFIT_MARGIN
    )

    # expected final based on history
    expected_final = round(asking_price * expected_ratio)

    log("decision_engine",
        f"Pricing: asking=₹{asking_price} | "
        f"min=₹{min_price} | expected=₹{expected_final}")

    return {
        "asking_price":   asking_price,
        "min_price":      min_price,
        "expected_final": expected_final,
        "price_ratio":    expected_ratio
    }

# ──────────────────────────────────────────
# DECIDE NEGOTIATION ACTION
# ──────────────────────────────────────────
def decide_negotiation_action(
    offer: float,
    asking_price: float,
    min_price: float,
    counter_rounds: int,
    buyer_profile: dict = None
) -> dict:
    """
    Decide what to do with a buyer's offer.
    Returns action: auto_accept / auto_reject /
                    counter / escalate_to_seller
    """
    risk = analyze_offer(offer, asking_price, min_price)

    # auto reject — too low
    if risk.get("auto_reject"):
        log("decision_engine", f"Auto-reject offer ₹{offer}")
        return {
            "action":        "auto_reject",
            "reason":        risk["message"],
            "counter_price": round(asking_price * 0.90)
        }

    # auto accept — great offer
    if risk.get("auto_accept"):
        log("decision_engine", f"Auto-accept offer ₹{offer}")
        return {
            "action": "auto_accept",
            "reason": "Offer meets asking price criteria"
        }

    # max rounds reached — escalate to seller
    if counter_rounds >= NegotiationConfig.MAX_COUNTER_ROUNDS:
        log("decision_engine",
            f"Max rounds reached, escalating to seller")
        return {
            "action":  "escalate_to_seller",
            "reason":  "Maximum negotiation rounds reached",
            "offer":   offer
        }

    # calculate smart counter offer
    ratio = offer / asking_price
    if ratio >= 0.85:
        # close to asking — small counter
        counter = round(asking_price * 0.95)
    elif ratio >= 0.75:
        # mid range — moderate counter
        counter = round(asking_price * 0.90)
    else:
        # low offer — firm counter
        counter = round(asking_price * 0.95)

    # never counter below min price
    counter = max(counter, min_price)

    log("decision_engine",
        f"Counter offer: ₹{offer} → ₹{counter} "
        f"(round {counter_rounds + 1})")

    return {
        "action":        "counter",
        "counter_price": counter,
        "reason":        f"Counter offer at ₹{counter}"
    }

# ──────────────────────────────────────────
# DECIDE NEXT AGENT STATE
# ──────────────────────────────────────────
def decide_next_state(
    current_state: str,
    context: dict
) -> str:
    """
    Given current state and context,
    decide what the next state should be.
    """
    if current_state == AgentState.IDLE:
        return AgentState.ANALYZING

    if current_state == AgentState.ANALYZING:
        if context.get("analysis_success"):
            return AgentState.LISTING
        return AgentState.IDLE

    if current_state == AgentState.LISTING:
        if context.get("listing_created"):
            return AgentState.WAITING_FOR_BUYER
        return AgentState.IDLE

    if current_state == AgentState.WAITING_FOR_BUYER:
        if context.get("buyer_arrived"):
            return AgentState.NEGOTIATING
        return AgentState.WAITING_FOR_BUYER

    if current_state == AgentState.NEGOTIATING:
        if context.get("deal_confirmed"):
            return AgentState.DEAL_CONFIRMED
        if context.get("negotiation_failed"):
            return AgentState.WAITING_FOR_BUYER
        return AgentState.NEGOTIATING

    if current_state == AgentState.DEAL_CONFIRMED:
        return AgentState.AWAITING_PAYMENT

    if current_state == AgentState.AWAITING_PAYMENT:
        if context.get("payment_confirmed"):
            return AgentState.PAYMENT_CONFIRMED
        return AgentState.AWAITING_PAYMENT

    if current_state == AgentState.PAYMENT_CONFIRMED:
        return AgentState.SCHEDULING

    if current_state == AgentState.SCHEDULING:
        if context.get("pickup_scheduled"):
            return AgentState.SHIPPING
        return AgentState.SCHEDULING

    if current_state == AgentState.SHIPPING:
        if context.get("delivered"):
            return AgentState.DELIVERED
        return AgentState.SHIPPING

    return current_state


