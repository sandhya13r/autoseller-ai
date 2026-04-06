# agent/risk_checker.py
from constants import RiskFlag, NegotiationConfig
from utils.logger import log

# ──────────────────────────────────────────
# RISK SIGNALS
# ──────────────────────────────────────────
SUSPICIOUS_PATTERNS = [
    "western union", "wire transfer", "gift card",
    "outside app", "my shipper", "already paid",
    "send first", "trust me", "urgent", "emergency",
    "bank transfer", "crypto", "bitcoin", "advance",
    "token amount", "whatsapp only", "call me now"
]

LOW_OFFER_SIGNALS = [
    "last price", "final price", "best price",
    "not a single rupee more", "take it or leave"
]

# ──────────────────────────────────────────
# ANALYZE MESSAGE RISK
# ──────────────────────────────────────────
def analyze_message(message: str) -> dict:
    """
    Analyze a buyer message for risk signals.
    Returns risk assessment dict.
    """
    message_lower = message.lower()
    flags = []
    score = 0  # 0 = safe, 100 = blocked

    # check suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern in message_lower:
            flags.append(f"Suspicious keyword: '{pattern}'")
            score += 30

    # check pressure tactics
    for signal in LOW_OFFER_SIGNALS:
        if signal in message_lower:
            flags.append(f"Pressure tactic: '{signal}'")
            score += 10

    # check for external contact attempts
    import re
    phone_pattern = r'\b[6-9]\d{9}\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.search(phone_pattern, message):
        flags.append("Attempted phone number exchange")
        score += 20

    if re.search(email_pattern, message):
        flags.append("Attempted email exchange")
        score += 15

    # determine risk level
    if score >= 60:
        risk_level = RiskFlag.BLOCKED
    elif score >= 40:
        risk_level = RiskFlag.HIGH
    elif score >= 20:
        risk_level = RiskFlag.MEDIUM
    else:
        risk_level = RiskFlag.LOW

    result = {
        "risk_level":  risk_level,
        "score":       min(score, 100),
        "flags":       flags,
        "is_blocked":  risk_level == RiskFlag.BLOCKED,
        "message":     _get_risk_message(risk_level, flags)
    }

    if score > 0:
        log("risk_checker",
            f"Risk detected: {risk_level} (score:{score}) | {flags}",
            "WARN")

    return result

# ──────────────────────────────────────────
# ANALYZE OFFER RISK
# ──────────────────────────────────────────
def analyze_offer(
    offer_price: float,
    asking_price: float,
    min_price: float
) -> dict:
    """
    Analyze if a price offer is risky or acceptable.
    """
    if asking_price <= 0:
        return {"risk_level": RiskFlag.LOW, "is_blocked": False}

    ratio = offer_price / asking_price

    if offer_price < min_price * 0.5:
        # extremely low offer — likely not serious
        return {
            "risk_level":   RiskFlag.HIGH,
            "score":        70,
            "flags":        ["Offer below 50% of minimum acceptable price"],
            "is_blocked":   False,
            "auto_reject":  True,
            "message":      "Offer is too low to consider."
        }
    elif ratio < NegotiationConfig.AUTO_REJECT_BELOW:
        return {
            "risk_level":   RiskFlag.MEDIUM,
            "score":        40,
            "flags":        [f"Offer at {round(ratio*100)}% of asking price"],
            "is_blocked":   False,
            "auto_reject":  True,
            "message":      "Offer below minimum threshold."
        }
    elif ratio >= NegotiationConfig.AUTO_ACCEPT_ABOVE:
        return {
            "risk_level":   RiskFlag.LOW,
            "score":        0,
            "flags":        [],
            "is_blocked":   False,
            "auto_accept":  True,
            "message":      "Offer accepted automatically."
        }
    else:
        return {
            "risk_level":   RiskFlag.LOW,
            "score":        0,
            "flags":        [],
            "is_blocked":   False,
            "auto_reject":  False,
            "auto_accept":  False,
            "message":      "Offer in negotiation range."
        }

# ──────────────────────────────────────────
# VALIDATE TRANSACTION
# ──────────────────────────────────────────
def validate_transaction(
    final_price: float,
    asking_price: float,
    buyer_profile: dict
) -> dict:
    """
    Final safety check before confirming deal.
    """
    issues = []

    # price check
    if final_price <= 0:
        issues.append("Invalid final price")

    ratio = final_price / asking_price if asking_price else 0
    if ratio < NegotiationConfig.MIN_PROFIT_MARGIN:
        issues.append(
            f"Final price {round(ratio*100)}% of asking — "
            f"below {round(NegotiationConfig.MIN_PROFIT_MARGIN*100)}% minimum"
        )

    # buyer trust check
    trust_score = buyer_profile.get("trust_score", 100) if buyer_profile else 100
    if trust_score < 30:
        issues.append(f"Low buyer trust score: {trust_score}")

    is_safe = len(issues) == 0

    log("risk_checker",
        f"Transaction validation: {'✅ SAFE' if is_safe else '⚠️ ISSUES: ' + str(issues)}")

    return {
        "is_safe":  is_safe,
        "issues":   issues,
        "requires_seller_approval": not is_safe
    }

# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────
def _get_risk_message(risk_level: str, flags: list) -> str:
    if risk_level == RiskFlag.BLOCKED:
        return "⛔ This interaction has been blocked for your safety."
    elif risk_level == RiskFlag.HIGH:
        return "⚠️ High risk detected. Seller approval required."
    elif risk_level == RiskFlag.MEDIUM:
        return "⚠️ Some suspicious signals detected. Proceed with caution."
    else:
        return "✅ Interaction looks safe."