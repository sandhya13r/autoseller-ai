# database/models.py
from sqlalchemy import (
    Column, String, Integer, Float,
    Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# ──────────────────────────────────────────
# USER
# ──────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id         = Column(String, primary_key=True, default=generate_uuid)
    name       = Column(String(100), nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    phone      = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # relationships
    items      = relationship("Item", back_populates="seller")

    def __repr__(self):
        return f"<User {self.name} | {self.email}>"

# ──────────────────────────────────────────
# ITEM
# ──────────────────────────────────────────
class Item(Base):
    __tablename__ = "items"

    id              = Column(String, primary_key=True, default=generate_uuid)
    seller_id       = Column(String, ForeignKey("users.id"), nullable=False)
    image_url       = Column(String, nullable=False)
    title           = Column(String(200), nullable=True)
    description     = Column(Text, nullable=True)

    # AI analysis results
    category        = Column(String(50), nullable=True)
    brand           = Column(String(100), nullable=True)
    model           = Column(String(100), nullable=True)
    condition       = Column(String(50), nullable=True)
    estimated_price = Column(Float, nullable=True)
    min_price       = Column(Float, nullable=True)
    max_price       = Column(Float, nullable=True)
    ai_analysis     = Column(JSON, nullable=True)  # full Gemini response

    # state
    agent_state     = Column(String(50), default="idle")
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, onupdate=func.now())

    # relationships
    seller          = relationship("User", back_populates="items")
    listing         = relationship("Listing", back_populates="item", uselist=False)

    def __repr__(self):
        return f"<Item {self.title} | {self.condition} | ₹{self.estimated_price}>"

# ──────────────────────────────────────────
# LISTING
# ──────────────────────────────────────────
class Listing(Base):
    __tablename__ = "listings"

    id               = Column(String, primary_key=True, default=generate_uuid)
    item_id          = Column(String, ForeignKey("items.id"), nullable=False)
    title            = Column(String(200), nullable=False)
    description      = Column(Text, nullable=False)
    tags             = Column(JSON, nullable=True)       # list of tags
    asking_price     = Column(Float, nullable=False)
    platform         = Column(String(50), nullable=True)
    platform_url     = Column(String(500), nullable=True)  # prefilled URL
    agent_chat_url   = Column(String(500), nullable=True)  # buyer chat link
    status           = Column(String(50), default="draft") # draft/active/sold/expired
    created_at       = Column(DateTime, server_default=func.now())

    # relationships
    item             = relationship("Item", back_populates="listing")
    negotiations     = relationship("Negotiation", back_populates="listing")

    def __repr__(self):
        return f"<Listing {self.title} | ₹{self.asking_price} | {self.status}>"

# ──────────────────────────────────────────
# NEGOTIATION
# ──────────────────────────────────────────
class Negotiation(Base):
    __tablename__ = "negotiations"

    id              = Column(String, primary_key=True, default=generate_uuid)
    listing_id      = Column(String, ForeignKey("listings.id"), nullable=False)

    # buyer info
    buyer_name      = Column(String(100), nullable=True)
    buyer_phone     = Column(String(20), nullable=True)
    buyer_email     = Column(String(100), nullable=True)

    # negotiation data
    initial_offer   = Column(Float, nullable=True)
    final_price     = Column(Float, nullable=True)
    rounds          = Column(Integer, default=0)
    chat_history    = Column(JSON, default=list)   # list of {role, message, timestamp}
    buyer_profile   = Column(JSON, nullable=True)  # trust score, behavior type
    risk_flag       = Column(String(20), default="low")

    # status
    status          = Column(String(50), default="active")
    # active / deal_confirmed / rejected / cancelled
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, onupdate=func.now())

    # relationships
    listing         = relationship("Listing", back_populates="negotiations")
    transaction     = relationship("Transaction", back_populates="negotiation", uselist=False)
    shipment        = relationship("Shipment", back_populates="negotiation", uselist=False)

    def __repr__(self):
        return f"<Negotiation {self.id} | ₹{self.final_price} | {self.status}>"

# ──────────────────────────────────────────
# TRANSACTION (Payment)
# ──────────────────────────────────────────
class Transaction(Base):
    __tablename__ = "transactions"

    id                  = Column(String, primary_key=True, default=generate_uuid)
    negotiation_id      = Column(String, ForeignKey("negotiations.id"), nullable=False)
    razorpay_order_id   = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    amount              = Column(Float, nullable=False)
    currency            = Column(String(10), default="INR")
    status              = Column(String(50), default="pending")
    # pending / paid / failed / refunded
    paid_at             = Column(DateTime, nullable=True)
    created_at          = Column(DateTime, server_default=func.now())

    # relationships
    negotiation         = relationship("Negotiation", back_populates="transaction")

    def __repr__(self):
        return f"<Transaction ₹{self.amount} | {self.status}>"

# ──────────────────────────────────────────
# SHIPMENT
# ──────────────────────────────────────────
class Shipment(Base):
    __tablename__ = "shipments"

    id                  = Column(String, primary_key=True, default=generate_uuid)
    negotiation_id      = Column(String, ForeignKey("negotiations.id"), nullable=False)

    # shiprocket data
    shiprocket_order_id = Column(String, nullable=True)
    awb_number          = Column(String, nullable=True)  # tracking number
    courier_name        = Column(String, nullable=True)
    tracking_url        = Column(String, nullable=True)

    # pickup details
    pickup_address      = Column(Text, nullable=True)
    pickup_scheduled_at = Column(DateTime, nullable=True)
    seller_available_slots = Column(JSON, nullable=True)

    # delivery details
    delivery_address    = Column(Text, nullable=True)
    estimated_delivery  = Column(DateTime, nullable=True)

    # status timeline
    status              = Column(String(50), default="pending")
    # pending/pickup_scheduled/picked_up/in_transit/out_for_delivery/delivered
    status_timeline     = Column(JSON, default=list)  # list of {status, timestamp, note}

    created_at          = Column(DateTime, server_default=func.now())
    updated_at          = Column(DateTime, onupdate=func.now())

    # relationships
    negotiation         = relationship("Negotiation", back_populates="shipment")

    def __repr__(self):
        return f"<Shipment AWB:{self.awb_number} | {self.status}>"

# ──────────────────────────────────────────
# NOTIFICATION
# ──────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id          = Column(String, primary_key=True, default=generate_uuid)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False)
    type        = Column(String(50), nullable=False)   # from constants.NotificationType
    title       = Column(String(200), nullable=False)
    message     = Column(Text, nullable=False)
    is_read     = Column(Boolean, default=False)
    extra_data  = Column(JSON, nullable=True)          # extra data like item_id, amount
    created_at  = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Notification {self.type} | {self.title} | read:{self.is_read}>"

# ──────────────────────────────────────────
# LONG TERM MEMORY (Agent Learning)
# ──────────────────────────────────────────
class AgentMemory(Base):
    __tablename__ = "agent_memory"

    id              = Column(String, primary_key=True, default=generate_uuid)
    category        = Column(String(50), nullable=False)
    platform        = Column(String(50), nullable=False)
    avg_days_sold   = Column(Float, nullable=True)
    avg_price_ratio = Column(Float, nullable=True)  # final/asking ratio
    success_count   = Column(Integer, default=0)
    fail_count      = Column(Integer, default=0)
    insights        = Column(JSON, nullable=True)   # key learnings
    updated_at      = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<AgentMemory {self.category} | {self.platform} | ratio:{self.avg_price_ratio}>"

