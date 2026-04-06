# integrations/shiprocket.py
import httpx
import config
from utils.logger import log
from datetime import datetime, timedelta

BASE_URL = "https://apiv2.shiprocket.in/v1/external"
_token   = None

# ──────────────────────────────────────────
# AUTHENTICATE
# ──────────────────────────────────────────
def get_token() -> str:
    """Login and get Shiprocket auth token."""
    global _token
    if _token:
        return _token

    try:
        response = httpx.post(
            f"{BASE_URL}/auth/login",
            json={
                "email":    config.SHIPROCKET_EMAIL,
                "password": config.SHIPROCKET_PASSWORD
            }
        )
        data   = response.json()
        _token = data.get("token")
        log("shiprocket", "✅ Authenticated", "SUCCESS")
        return _token

    except Exception as e:
        log("shiprocket",
            f"❌ Auth failed: {e}", "ERROR")
        raise e

def _headers() -> dict:
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type":  "application/json"
    }

# ──────────────────────────────────────────
# CREATE SHIPMENT
# ──────────────────────────────────────────
def create_shipment(
    item_data: dict,
    buyer_info: dict,
    amount: float
) -> dict:
    """Create a Shiprocket shipment order."""
    try:
        order_data = {
            "order_id":        f"AUTO_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "order_date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pickup_location": "Primary",
            "channel_id":      "",
            "billing_customer_name":  buyer_info.get("name", "Buyer"),
            "billing_address":        buyer_info.get("address", ""),
            "billing_city":           buyer_info.get("city", ""),
            "billing_pincode":        buyer_info.get("pincode", ""),
            "billing_state":          buyer_info.get("state", ""),
            "billing_country":        "India",
            "billing_email":          buyer_info.get("email", ""),
            "billing_phone":          buyer_info.get("phone", ""),
            "shipping_is_billing":    True,
            "order_items": [{
                "name":       item_data.get("title", "Item"),
                "sku":        "SKU001",
                "units":      1,
                "selling_price": str(amount),
            }],
            "payment_method": "Prepaid",
            "sub_total":      amount,
            "length":         10,
            "breadth":        10,
            "height":         10,
            "weight":         0.5
        }

        response = httpx.post(
            f"{BASE_URL}/orders/create/adhoc",
            headers = _headers(),
            json    = order_data
        )
        data = response.json()

        log("shiprocket",
            f"✅ Shipment created: {data.get('order_id')}",
            "SUCCESS")

        return {
            "order_id":    str(data.get("order_id", "")),
            "awb":         data.get("awb_code", ""),
            "courier":     data.get("courier_name", ""),
            "tracking_url": f"https://shiprocket.co/tracking/{data.get('awb_code','')}",
            "estimated_delivery": (
                datetime.now() + timedelta(days=3)
            ).strftime("%B %d, %Y")
        }

    except Exception as e:
        log("shiprocket",
            f"❌ Shipment failed: {e}", "ERROR")
        raise e

# ──────────────────────────────────────────
# GET TRACKING
# ──────────────────────────────────────────
def get_tracking(awb: str) -> dict:
    """Get tracking status for AWB number."""
    try:
        response = httpx.get(
            f"{BASE_URL}/courier/track/awb/{awb}",
            headers = _headers()
        )
        data     = response.json()
        tracking = data.get("tracking_data", {})

        return {
            "status":   tracking.get("shipment_status", "In Transit"),
            "timeline": tracking.get("shipment_track_activities", []),
            "awb":      awb
        }

    except Exception as e:
        log("shiprocket",
            f"❌ Tracking failed: {e}", "ERROR")
        return {
            "status":   "In Transit",
            "timeline": [],
            "awb":      awb
        }