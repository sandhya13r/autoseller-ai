# integrations/razorpay.py
import razorpay
import hmac
import hashlib
import config
from utils.logger import log

# ──────────────────────────────────────────
# CLIENT
# ──────────────────────────────────────────
def get_client():
    return razorpay.Client(
        auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET)
    )

# ──────────────────────────────────────────
# CREATE ORDER
# ──────────────────────────────────────────
def create_order(
    amount: int,
    currency: str = "INR",
    notes: dict = None
) -> dict:
    """
    Create Razorpay order.
    Amount must be in paise (multiply by 100).
    """
    client = get_client()
    try:
        order = client.order.create({
            "amount":   amount,
            "currency": currency,
            "notes":    notes or {},
            "payment_capture": 1
        })
        log("razorpay",
            f"✅ Order created: {order['id']} "
            f"₹{amount/100}", "SUCCESS")
        return order

    except Exception as e:
        log("razorpay",
            f"❌ Order creation failed: {e}", "ERROR")
        raise e

# ──────────────────────────────────────────
# VERIFY PAYMENT
# ──────────────────────────────────────────
def verify_payment(
    order_id: str,
    payment_id: str,
    signature: str
) -> bool:
    """
    Verify Razorpay payment signature.
    Returns True if valid.
    """
    try:
        msg = f"{order_id}|{payment_id}"
        generated = hmac.new(
            config.RAZORPAY_KEY_SECRET.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()

        verified = hmac.compare_digest(generated, signature)
        log("razorpay",
            f"Payment verification: {'✅' if verified else '❌'}")
        return verified

    except Exception as e:
        log("razorpay",
            f"❌ Verification error: {e}", "ERROR")
        return False

# ──────────────────────────────────────────
# FETCH PAYMENT
# ──────────────────────────────────────────
def fetch_payment(payment_id: str) -> dict:
    """Fetch payment details from Razorpay."""
    client = get_client()
    try:
        payment = client.payment.fetch(payment_id)
        log("razorpay", f"Payment fetched: {payment_id}")
        return payment
    except Exception as e:
        log("razorpay",
            f"❌ Fetch failed: {e}", "ERROR")
        raise e