# routes/delivery.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from schemas.delivery_schema import PickupScheduleRequest
from services.logistics_service import (
    book_shipment,
    get_tracking,
    get_pickup_slots
)
from services.notification_service import (
    notify_pickup_scheduled,
    notify_order_shipped
)
from agent import memory, state_manager
from utils.logger import log

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.get("/slots")
async def get_slots():
    """Get available pickup time slots."""
    slots = get_pickup_slots()
    return {"slots": slots}

@router.post("/schedule")
async def schedule_pickup(request: PickupScheduleRequest):
    """
    Schedule pickup and book Shiprocket courier.
    """
    try:
        # store seller address in memory
        memory.update(request.item_id, {
            "seller_address": request.seller_address,
            "seller_city":    request.seller_city,
            "seller_pincode": request.seller_pincode,
            "seller_state":   request.seller_state,
        })

        # book shipment
        result = book_shipment(
            request.item_id,
            request.selected_slot
        )

        if result["success"]:
            log("delivery_route",
                f"✅ Pickup scheduled: {request.selected_slot}")

            # notify seller
            mem       = memory.get(request.item_id)
            seller_id = mem.get("seller_id", "")
            if seller_id:
                notify_pickup_scheduled(
                    seller_id,
                    request.selected_slot,
                    result.get("courier", "Courier"),
                    request.item_id
                )

        return result

    except Exception as e:
        log("delivery_route", f"❌ Error: {e}", "ERROR")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/track/{item_id}")
async def track_order(item_id: str):
    """Get live tracking status for an item."""
    return get_tracking(item_id)

@router.post("/advance/{item_id}")
async def advance_tracking(item_id: str):
    """Advance tracking stage manually for demo."""
    from simulations.fake_tracking import advance_stage
    from agent import state_manager
    from constants import AgentState
    
    result = advance_stage(item_id)
    
    # if delivered, update agent state
    if result.get("is_delivered"):
        state_manager.transition(item_id, AgentState.DELIVERED)
        from agent.orchestrator import confirm_delivery
        confirm_delivery(item_id)
    
    return result