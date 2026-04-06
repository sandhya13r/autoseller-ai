# routes/payment.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from schemas.payment_schema import (
    PaymentCreateRequest,
    PaymentConfirmRequest
)
from services.payment_service import (
    create_payment,
    confirm_payment
)
from agent.orchestrator import confirm_payment as orchestrator_confirm
from utils.logger import log
import config

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/create")
async def create_payment_order(request: PaymentCreateRequest):
    """Create Razorpay payment order."""
    result = create_payment(request.item_id)
    return result

@router.post("/confirm")
async def confirm_payment_route(request: PaymentConfirmRequest):
    """
    Confirm payment after successful transaction.
    Called by frontend after Razorpay success.
    """
    try:
        result = confirm_payment(
            item_id    = request.item_id,
            payment_id = request.payment_id,
            order_id   = request.order_id,
            signature  = request.signature
        )

        if result["success"]:
            # trigger orchestrator
            orchestrator_confirm(
                request.item_id,
                request.payment_id
            )

        return result

    except Exception as e:
        log("payment_route", f"❌ Error: {e}", "ERROR")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.post("/simulate-confirm/{item_id}")
async def simulate_payment_confirm(item_id: str):
    """
    Instantly confirm payment in simulation mode.
    Used during demo.
    """
    if not config.IS_SIMULATION:
        return JSONResponse(
            status_code=400,
            content={"error": "Only available in simulation mode"}
        )

    from simulations.sim_router import fake_payment_confirm
    result = fake_payment_confirm(item_id)

    if result["success"]:
        orchestrator_confirm(item_id, result["payment_id"])

    return result

@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """Razorpay webhook for payment events."""
    try:
        body = await request.json()
        event = body.get("event")

        if event == "payment.captured":
            payment = body["payload"]["payment"]["entity"]
            notes   = payment.get("notes", {})
            item_id = notes.get("item_id")

            if item_id:
                confirm_payment(
                    item_id    = item_id,
                    payment_id = payment["id"],
                    order_id   = payment["order_id"],
                    signature  = None
                )
                log("payment_webhook",
                    f"✅ Webhook: payment captured {payment['id']}",
                    "SUCCESS")

        return {"status": "ok"}

    except Exception as e:
        log("payment_route",
            f"❌ Webhook error: {e}", "ERROR")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )