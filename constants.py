# constants.py

# ── Agent States (matches state_machine.py)
class AgentState:
    IDLE              = "idle"
    ANALYZING         = "analyzing"
    LISTING           = "listing"
    WAITING_FOR_BUYER = "waiting_for_buyer"
    NEGOTIATING       = "negotiating"
    DEAL_CONFIRMED    = "deal_confirmed"
    AWAITING_PAYMENT  = "awaiting_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    SCHEDULING        = "scheduling"
    SHIPPING          = "shipping"
    DELIVERED         = "delivered"
    CANCELLED         = "cancelled"

# ── Negotiation Thresholds
class NegotiationConfig:
    AUTO_ACCEPT_ABOVE  = 0.95   # auto accept if offer >= 95% of asking price
    AUTO_REJECT_BELOW  = 0.60   # auto reject if offer < 60% of asking price
    MAX_COUNTER_ROUNDS = 3      # max back and forth before escalating to seller
    MIN_PROFIT_MARGIN  = 0.70   # never go below 70% of estimated value

# ── Platforms
class Platform:
    OLX = {
        "name": "OLX",
        "url": "https://www.olx.in/post-ad",
        "best_for": ["electronics", "furniture", "vehicles", "mobiles"],
        "avg_days_to_sell": 5
    }
    FACEBOOK = {
        "name": "Facebook Marketplace",
        "url": "https://www.facebook.com/marketplace/create/item",
        "best_for": ["furniture", "clothing", "home", "books"],
        "avg_days_to_sell": 3
    }
    QUIKR = {
        "name": "Quikr",
        "url": "https://www.quikr.com/post-ad",
        "best_for": ["electronics", "jobs", "services"],
        "avg_days_to_sell": 7
    }
    ALL = [OLX, FACEBOOK, QUIKR]

# ── Item Categories
class Category:
    ELECTRONICS  = "electronics"
    MOBILES      = "mobiles"
    FURNITURE    = "furniture"
    CLOTHING     = "clothing"
    BOOKS        = "books"
    VEHICLES     = "vehicles"
    APPLIANCES   = "appliances"
    SPORTS       = "sports"
    TOYS         = "toys"
    OTHER        = "other"
    ALL = [
        ELECTRONICS, MOBILES, FURNITURE, CLOTHING,
        BOOKS, VEHICLES, APPLIANCES, SPORTS, TOYS, OTHER
    ]

# ── Item Conditions
class Condition:
    BRAND_NEW    = "brand_new"
    LIKE_NEW     = "like_new"
    GOOD         = "good"
    FAIR         = "fair"
    POOR         = "poor"

# ── Condition price multipliers
CONDITION_MULTIPLIER = {
    Condition.BRAND_NEW : 0.90,
    Condition.LIKE_NEW  : 0.75,
    Condition.GOOD      : 0.60,
    Condition.FAIR      : 0.45,
    Condition.POOR      : 0.30,
}

# ── Risk Flags
class RiskFlag:
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    BLOCKED  = "blocked"

# ── Notification Types
class NotificationType:
    NEW_OFFER         = "new_offer"
    DEAL_CONFIRMED    = "deal_confirmed"
    PAYMENT_RECEIVED  = "payment_received"
    PICKUP_SCHEDULED  = "pickup_scheduled"
    ORDER_SHIPPED     = "order_shipped"
    ORDER_DELIVERED   = "order_delivered"

# ── Simulation Timing (seconds)
class SimTiming:
    BUYER_FIRST_MESSAGE  = 3
    BUYER_REPLY_DELAY    = 4
    PAYMENT_CONFIRM      = 3
    PICKUP_STATUS        = 5
    IN_TRANSIT_STATUS    = 8
    DELIVERED_STATUS     = 12