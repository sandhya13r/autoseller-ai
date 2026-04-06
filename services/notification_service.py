# services/notification_service.py
from database.db import SessionLocal
from database.models import Notification
from constants import NotificationType
from utils.logger import log
from datetime import datetime

# ──────────────────────────────────────────
# CREATE NOTIFICATION
# ──────────────────────────────────────────
def create(
    user_id: str,
    type: str,
    title: str,
    message: str,
    extra_data: dict = None
) -> dict:
    """Create and store a notification."""
    db = SessionLocal()
    try:
        notif = Notification(
            user_id    = user_id,
            type       = type,
            title      = title,
            message    = message,
            extra_data = extra_data or {}
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        log("notification_service",
            f"✅ Notification created: {title}")

        return {
            "id":         notif.id,
            "type":       notif.type,
            "title":      notif.title,
            "message":    notif.message,
            "created_at": notif.created_at.isoformat()
        }

    except Exception as e:
        log("notification_service",
            f"❌ Failed: {e}", "ERROR")
        db.rollback()
        return {}
    finally:
        db.close()

# ──────────────────────────────────────────
# NOTIFY SELLER — key events
# ──────────────────────────────────────────
def notify_new_offer(
    seller_id: str,
    item_title: str,
    offer_amount: float,
    item_id: str
):
    create(
        user_id    = seller_id,
        type       = NotificationType.NEW_OFFER,
        title      = f"New offer on {item_title}",
        message    = f"A buyer offered ₹{int(offer_amount):,} for your item.",
        extra_data = {"item_id": item_id, "offer": offer_amount}
    )

def notify_deal_confirmed(
    seller_id: str,
    item_title: str,
    final_price: float,
    item_id: str
):
    create(
        user_id    = seller_id,
        type       = NotificationType.DEAL_CONFIRMED,
        title      = "🤝 Deal Confirmed!",
        message    = f"Your {item_title} sold for ₹{int(final_price):,}! Payment link sent to buyer.",
        extra_data = {"item_id": item_id, "final_price": final_price}
    )

def notify_payment_received(
    seller_id: str,
    item_title: str,
    amount: float,
    item_id: str
):
    create(
        user_id    = seller_id,
        type       = NotificationType.PAYMENT_RECEIVED,
        title      = "💰 Payment Received!",
        message    = f"₹{int(amount):,} received for {item_title}. Please share your pickup availability.",
        extra_data = {"item_id": item_id, "amount": amount}
    )

def notify_pickup_scheduled(
    seller_id: str,
    pickup_slot: str,
    courier: str,
    item_id: str
):
    create(
        user_id    = seller_id,
        type       = NotificationType.PICKUP_SCHEDULED,
        title      = "📅 Pickup Scheduled!",
        message    = f"{courier} will pick up your item on {pickup_slot}. Please keep it ready.",
        extra_data = {"item_id": item_id, "slot": pickup_slot}
    )

def notify_order_shipped(
    seller_id: str,
    awb: str,
    courier: str,
    item_id: str
):
    create(
        user_id    = seller_id,
        type       = NotificationType.ORDER_SHIPPED,
        title      = "🚚 Item Picked Up!",
        message    = f"Your item has been picked up by {courier}. AWB: {awb}",
        extra_data = {"item_id": item_id, "awb": awb}
    )

def notify_delivered(
    seller_id: str,
    item_title: str,
    item_id: str
):
    create(
        user_id    = seller_id,
        type       = NotificationType.ORDER_DELIVERED,
        title      = "🎉 Item Delivered!",
        message    = f"Your {item_title} has been delivered successfully!",
        extra_data = {"item_id": item_id}
    )

# ──────────────────────────────────────────
# GET NOTIFICATIONS
# ──────────────────────────────────────────
def get_notifications(user_id: str) -> list:
    """Get all notifications for a user."""
    db = SessionLocal()
    try:
        notifs = db.query(Notification)\
            .filter(Notification.user_id == user_id)\
            .order_by(Notification.created_at.desc())\
            .limit(20)\
            .all()

        return [
            {
                "id":         n.id,
                "type":       n.type,
                "title":      n.title,
                "message":    n.message,
                "is_read":    n.is_read,
                "extra_data": n.extra_data,
                "created_at": n.created_at.isoformat()
            }
            for n in notifs
        ]
    except Exception as e:
        log("notification_service",
            f"❌ Fetch failed: {e}", "ERROR")
        return []
    finally:
        db.close()

# ──────────────────────────────────────────
# MARK AS READ
# ──────────────────────────────────────────
def mark_read(notification_id: str):
    """Mark notification as read."""
    db = SessionLocal()
    try:
        notif = db.query(Notification)\
            .filter(Notification.id == notification_id)\
            .first()
        if notif:
            notif.is_read = True
            db.commit()
    except Exception as e:
        log("notification_service",
            f"❌ Mark read failed: {e}", "ERROR")
        db.rollback()
    finally:
        db.close()

# ──────────────────────────────────────────
# GET UNREAD COUNT
# ──────────────────────────────────────────
def get_unread_count(user_id: str) -> int:
    """Get unread notification count."""
    db = SessionLocal()
    try:
        return db.query(Notification)\
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).count()
    except:
        return 0
    finally:
        db.close()