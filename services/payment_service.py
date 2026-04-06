# services/payment_service.py
from integrations import razorpay as rzp
from agent import memory, state_manager
from constants import AgentState
from utils.logger import log
import config

# ──────────────────────────────────────────
# CREATE PAYMENT ORDER
# ──────────────────────────────────────────
def create_payment(item_id: str) -> dict:
    """
    Create Razorpay payment order for confirmed deal.
    Returns payment details with checkout URL.
    """
    log("payment_service",
        f"Creating payment for item: {item_id}")

    final_price = memory.get(item_id, "final_price")
    if not final_price:
        log("payment_service",
            "❌ No final price in memory", "ERROR")
        return {"success": False, "error": "No final price found"}

    try:
        if config.IS_SIMULATION:
            # simulation mode — fake payment
            order = {
                "id":       f"sim_order_{item_id[:8]}",
                "amount":   int(final_price * 100),
                "currency": "INR",
                "status":   "created"
            }
        else:
            order = rzp.create_order(
                amount   = int(final_price * 100),  # paise
                currency = "INR",
                notes    = {"item_id": item_id}
            )

        memory.set(item_id, "payment_order_id", order["id"])
        state_manager.transition(
            item_id, AgentState.AWAITING_PAYMENT
        )

        log("payment_service",
            f"✅ Payment order created: {order['id']}",
            "SUCCESS")

        return {
            "success":    True,
            "order_id":   order["id"],
            "amount":     final_price,
            "currency":   "INR",
            "key_id":     config.RAZORPAY_KEY_ID,
            "item_id":    item_id
        }

    except Exception as e:
        log("payment_service",
            f"❌ Payment creation failed: {e}", "ERROR")
        return {"success": False, "error": str(e)}

# ──────────────────────────────────────────
# CONFIRM PAYMENT
# ──────────────────────────────────────────
def confirm_payment(
    item_id: str,
    payment_id: str,
    order_id: str,
    signature: str = None
) -> dict:
    """
    Verify and confirm payment.
    Called by Razorpay webhook or frontend.
    """
    log("payment_service",
        f"Confirming payment: {payment_id}")

    try:
        if config.IS_SIMULATION:
            verified = True
        else:
            verified = rzp.verify_payment(
                order_id   = order_id,
                payment_id = payment_id,
                signature  = signature
            )

        if verified:
            memory.update(item_id, {
                "payment_id":     payment_id,
                "payment_status": "confirmed"
            })
            state_manager.transition(
                item_id, AgentState.PAYMENT_CONFIRMED
            )
            state_manager.transition(
                item_id, AgentState.SCHEDULING
            )

            log("payment_service",
                f"✅ Payment confirmed: {payment_id}",
                "SUCCESS")

            return {
                "success":    True,
                "payment_id": payment_id,
                "message":    "Payment confirmed! 🎉"
            }
        else:
            log("payment_service",
                "❌ Payment verification failed", "ERROR")
            return {
                "success": False,
                "error":   "Payment verification failed"
            }

    except Exception as e:
        log("payment_service",
            f"❌ Confirmation error: {e}", "ERROR")
        return {"success": False, "error": str(e)}