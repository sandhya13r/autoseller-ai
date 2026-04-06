# routes/agent.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from agent import state_manager, memory
from agent.orchestrator import confirm_delivery
from utils.logger import get_logs
from utils.explain import explain_pipeline
import config
from simulations import fake_tracking
from database.db import get_db
from database.models import Item


router = APIRouter(prefix="/agent", tags=["Agent"])
@router.post("/advance/{item_id}")
async def advance_agent_simulation(item_id: str):
    """
    Manually advance the simulation stage.
    This is what your 'Confirm Pickup' button calls.
    """
    new_status = fake_tracking.advance_stage(item_id)
    return {"success": True, "new_status": new_status}

@router.post("/reset/{item_id}")
async def reset_agent_simulation(item_id: str):
    """Resets the tracking for a fresh demo."""
    fake_tracking.reset_tracking(item_id)
    return {"success": True}



@router.get("/status/{item_id}")
async def get_status(item_id: str):
    status = state_manager.get_status(item_id)

    # simulation delivery override
    if config.IS_SIMULATION:
        sim_data = fake_tracking.get_status(item_id)
        if sim_data.get("is_delivered"):
            status["current_state"] = "delivered"
            status["progress"] = 100
            status["label"] = "Delivered Successfully"
            status["icon"] = "🎉"

    mem = memory.get(item_id)
    steps = explain_pipeline(item_id, mem)

    # ✅ FETCH ITEM FROM DB
    db = next(get_db())
    item = db.query(Item).filter(Item.id == item_id).first()

    return {
    **status,
    "explanation_steps": steps,
    "mode": config.APP_MODE,

    "image_url": item.image_url if item else None,
    "asking_price": item.estimated_price if item else None,

    "item_data": (
        {
            "title": item.title,
            "category": item.category,
            "condition": item.condition,
            "brand": (item.ai_analysis or {}).get("brand", ""),
            "key_features": (item.ai_analysis or {}).get("key_features", []),
            **(item.ai_analysis or {})
        }
        if item else {}
    ),

    "listing_data": (
        {
            "title": item.title,
            "description": (item.ai_analysis or {}).get("description", ""),
            "tags": (item.ai_analysis or {}).get("tags", []),
            "platform": "OLX"
        }
        if item else {}
    ),

    # ✅ ADD THIS (CRITICAL)
    "platform": "OLX"
}
@router.get("/logs")
async def get_agent_logs():
    """Get agent activity logs for dashboard."""
    return {"logs": get_logs()}

@router.post("/mode/{mode}")
async def set_mode(mode: str):
    """
    Toggle between simulation and real mode.
    mode: 'simulation' or 'real'
    """
    if mode not in ["simulation", "real"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Mode must be 'simulation' or 'real'"}
        )
    config.APP_MODE      = mode
    config.IS_SIMULATION = mode == "simulation"
    return {
        "success": True,
        "mode":    mode,
        "message": f"Switched to {'🎬 Simulation' if mode == 'simulation' else '⚡ Real'} mode"
    }

@router.get("/sessions")
async def get_all_sessions():
    """Get all active agent sessions."""
    return state_manager.get_all_sessions()

@router.post("/deliver/{item_id}")
async def mark_delivered(item_id: str):
    """Mark item as delivered (webhook/manual)."""
    result = confirm_delivery(item_id)
    return result