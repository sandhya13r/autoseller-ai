# routes/chat.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from schemas.chat_schema import (
    BuyerMessageRequest,
    BuyerContactRequest
)
from schemas.negotiation_schema import DealConfirmRequest
from agent.orchestrator import (
    handle_buyer_message,
    confirm_deal
)
from services.contact_service import (
    store_buyer_contact,
    validate_contact,
    get_contact_message
)
from services.notification_service import notify_deal_confirmed
from agent import memory, state_manager
from utils.logger import log

router = APIRouter(prefix="/chat", tags=["Chat"])

# ──────────────────────────────────────────
# HELPER — init sim data if memory empty
# ──────────────────────────────────────────
def _ensure_memory(item_id: str):
    """
    If item memory is empty (e.g. server restarted),
    initialize with simulation data so chat still works.
    """
    item_data = memory.get(item_id, "item_data")
    if not item_data:
        from simulations.sim_router import fake_analysis
        from agent.state_manager import create_session
        from constants import AgentState
        memory.init(item_id)
        item_data = fake_analysis("")
        memory.set(item_id, "item_data", item_data)
        memory.set(item_id, "asking_price", 42000)
        memory.set(item_id, "min_price", 35000)
        create_session(item_id)
        state_manager.transition(item_id, AgentState.NEGOTIATING)
        log("chat_route",
            f"🎬 Sim memory initialized for {item_id}")
    return item_data

# ──────────────────────────────────────────
# SEND MESSAGE
# ──────────────────────────────────────────
@router.post("/message")
async def send_message(request: BuyerMessageRequest):
    """
    Receive buyer message and return agent reply.
    Core negotiation endpoint.
    """
    # ensure memory is populated
    _ensure_memory(request.item_id)

    try:
        reply = handle_buyer_message(
            request.item_id,
            request.message
        )
        return {
            "success": True,
            "reply":   reply,
            "state":   state_manager.get_state(request.item_id)
        }
    except Exception as e:
        log("chat_route", f"❌ Error: {e}", "ERROR")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ──────────────────────────────────────────
# CONTACT
# ──────────────────────────────────────────
@router.post("/contact")
async def submit_contact(request: BuyerContactRequest):
    """Store buyer contact details."""
    validation = validate_contact(
        request.phone,
        request.name
    )
    if not validation["valid"]:
        return JSONResponse(
            status_code=400,
            content={"errors": validation["errors"]}
        )
    store_buyer_contact(
        request.item_id,
        request.name,
        request.phone,
        request.email
    )
    return {"success": True, "message": "Contact saved"}

# ──────────────────────────────────────────
# CONFIRM DEAL
# ──────────────────────────────────────────
@router.post("/confirm-deal")
async def confirm_deal_route(request: DealConfirmRequest):
    """Confirm deal and trigger payment flow."""
    store_buyer_contact(
        request.item_id,
        request.buyer_name,
        request.buyer_phone,
        request.buyer_email
    )
    result = confirm_deal(
        request.item_id,
        request.final_price
    )
    return result

# ──────────────────────────────────────────
# CHAT HISTORY
# ──────────────────────────────────────────
@router.get("/history/{item_id}")
async def get_history(item_id: str):
    """Get chat history for an item."""
    from agent.memory import get_chat_history
    history = get_chat_history(item_id)
    return {
        "item_id":  item_id,
        "messages": history,
        "state":    state_manager.get_state(item_id)
    }

# ──────────────────────────────────────────
# GREETING
# ──────────────────────────────────────────
@router.get("/greeting/{item_id}")
async def get_greeting(item_id: str):
    """Get initial buyer greeting message."""
    from services.buyer_service import get_greeting

    # ensure memory populated
    item_data = _ensure_memory(item_id)

    return {
        "message": get_greeting(item_data),
        "item_id": item_id
    }