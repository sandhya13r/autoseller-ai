# services/logistics_service.py
from integrations import shiprocket as ship
from agent import memory, state_manager
from constants import AgentState
from utils.logger import log
import config
from datetime import datetime, timedelta

# ──────────────────────────────────────────
# BOOK SHIPMENT
# ──────────────────────────────────────────
def book_shipment(item_id: str, pickup_slot: str) -> dict:
    """
    Book Shiprocket shipment after payment confirmed.
    """
    log("logistics_service",
        f"Booking shipment for item: {item_id}")

    mem        = memory.get(item_id)
    item_data  = mem.get("item_data") or {}
    final_price= mem.get("final_price") or 0
    buyer_info = mem.get("buyer_info") or {}

    try:
        if config.IS_SIMULATION:
            shipment = {
                "order_id":    f"sim_ship_{item_id[:8]}",
                "awb":         f"AWB{item_id[:8].upper()}",
                "courier":     "Delhivery",
                "tracking_url": f"https://shiprocket.co/tracking/AWB{item_id[:8].upper()}",
                "estimated_delivery": (
                    datetime.now() + timedelta(days=3)
                ).strftime("%B %d, %Y")
            }
        else:
            shipment = ship.create_shipment(
                item_data  = item_data,
                buyer_info = buyer_info,
                amount     = final_price
            )

        memory.update(item_id, {
            "shipment_id":    shipment["order_id"],
            "awb":            shipment["awb"],
            "courier":        shipment["courier"],
            "tracking_url":   shipment["tracking_url"],
            "pickup_slot":    pickup_slot,
            "estimated_delivery": shipment.get("estimated_delivery")
        })

        state_manager.transition(item_id, AgentState.SHIPPING)

        log("logistics_service",
            f"✅ Shipment booked: AWB {shipment['awb']}",
            "SUCCESS")

        return {
            "success":            True,
            "awb":                shipment["awb"],
            "courier":            shipment["courier"],
            "tracking_url":       shipment["tracking_url"],
            "estimated_delivery": shipment.get("estimated_delivery")
        }

    except Exception as e:
        log("logistics_service",
            f"❌ Shipment booking failed: {e}", "ERROR")
        return {"success": False, "error": str(e)}

# ──────────────────────────────────────────
# GET TRACKING STATUS
# ──────────────────────────────────────────
def get_tracking(item_id: str) -> dict:
    """Get current tracking status for shipment."""
    awb = memory.get(item_id, "awb")
    if not awb:
        return {"status": "not_found", "timeline": []}

    try:
        if config.IS_SIMULATION:
            from simulations.sim_router import fake_tracking_status
            return fake_tracking_status(item_id)
        else:
            return ship.get_tracking(awb)

    except Exception as e:
        log("logistics_service",
            f"❌ Tracking failed: {e}", "ERROR")
        return {"status": "error", "error": str(e)}

# ──────────────────────────────────────────
# GET PICKUP SLOTS
# ──────────────────────────────────────────
def get_pickup_slots() -> list:
    """Return available pickup time slots."""
    today    = datetime.now()
    slots    = []

    for i in range(1, 4):  # next 3 days
        date = today + timedelta(days=i)
        date_str = date.strftime("%A, %B %d")
        slots.extend([
            f"{date_str} — 9AM to 12PM",
            f"{date_str} — 12PM to 3PM",
            f"{date_str} — 3PM to 6PM",
        ])
    return slots

