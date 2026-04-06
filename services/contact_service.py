# services/contact_service.py
from agent import memory
from utils.logger import log

# ──────────────────────────────────────────
# STORE BUYER CONTACT
# ──────────────────────────────────────────
def store_buyer_contact(
    item_id: str,
    name: str,
    phone: str,
    email: str = None
):
    """Store buyer contact details in memory."""
    memory.set(item_id, "buyer_info", {
        "name":  name,
        "phone": phone,
        "email": email
    })
    log("contact_service",
        f"Buyer contact stored for item: {item_id}")

# ──────────────────────────────────────────
# RELEASE CONTACTS POST PAYMENT
# only after payment confirmed
# ──────────────────────────────────────────
def release_contacts(item_id: str) -> dict:
    """
    Release buyer and seller contact details
    to each other after payment is confirmed.
    """
    mem        = memory.get(item_id)
    buyer_info = mem.get("buyer_info") or {}
    state      = mem.get("payment_status")

    if state != "confirmed":
        log("contact_service",
            "⚠️ Contacts not released — payment not confirmed",
            "WARN")
        return {
            "success": False,
            "message": "Contacts will be shared after payment confirmation"
        }

    log("contact_service",
        f"✅ Contacts released for item: {item_id}",
        "SUCCESS")

    return {
        "success": True,
        "buyer": {
            "name":  buyer_info.get("name"),
            "phone": buyer_info.get("phone"),
            "email": buyer_info.get("email")
        },
        "message": "Contact details shared securely after payment confirmation"
    }

# ──────────────────────────────────────────
# GET CONTACT EXCHANGE MESSAGE
# sent in chat after payment
# ──────────────────────────────────────────
def get_contact_message(item_id: str) -> str:
    """
    Generate contact exchange message
    for chat after payment confirmed.
    """
    mem        = memory.get(item_id)
    buyer_info = mem.get("buyer_info") or {}
    awb        = mem.get("awb", "Pending")
    courier    = mem.get("courier", "Our courier partner")
    delivery   = mem.get("estimated_delivery", "2-3 business days")

    return (
        f"✅ *Payment Confirmed!*\n\n"
        f"📦 Your order has been placed successfully!\n"
        f"🚚 Courier: {courier}\n"
        f"📋 AWB: {awb}\n"
        f"📅 Estimated Delivery: {delivery}\n\n"
        f"The seller has been notified and will keep "
        f"your item ready for pickup.\n"
        f"You'll receive live tracking updates here! 🎯"
    )

# ──────────────────────────────────────────
# VALIDATE CONTACT INFO
# ──────────────────────────────────────────
def validate_contact(phone: str, name: str) -> dict:
    """Validate buyer contact details."""
    import re
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters")

    phone_clean = re.sub(r'[\s\-\+]', '', phone)
    if not re.match(r'^[6-9]\d{9}$', phone_clean):
        errors.append("Please enter a valid 10-digit Indian mobile number")

    return {
        "valid":  len(errors) == 0,
        "errors": errors,
        "phone":  phone_clean
    }