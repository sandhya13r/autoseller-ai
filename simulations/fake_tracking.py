# simulations/fake_tracking.py
from utils.logger import log
from datetime import datetime, timedelta

# ──────────────────────────────────────────
# TRACKING STATUS TIMELINE
# ──────────────────────────────────────────
TRACKING_STAGES = [
    {
        "status":      "pending",
        "label":       "Order Placed",
        "description": "Your order has been placed successfully",
        "icon":        "📋",
        "color":       "blue"
    },
    {
        "status":      "pickup_scheduled",
        "label":       "Pickup Scheduled",
        "description": "Courier will pick up item today",
        "icon":        "📅",
        "color":       "blue"
    },
    {
        "status":      "picked_up",
        "label":       "Item Picked Up",
        "description": "Item collected by Delhivery courier",
        "icon":        "📦",
        "color":       "orange"
    },
    {
        "status":      "in_transit",
        "label":       "In Transit",
        "description": "Item is on its way to you",
        "icon":        "🚚",
        "color":       "orange"
    },
    {
        "status":      "out_for_delivery",
        "label":       "Out for Delivery",
        "description": "Item is out for delivery today",
        "icon":        "🏍️",
        "color":       "green"
    },
    {
        "status":      "delivered",
        "label":       "Delivered",
        "description": "Item delivered successfully! Enjoy! 🎉",
        "icon":        "🎉",
        "color":       "green"
    }
]

# ── in memory tracking state per item
_tracking_state: dict[str, int] = {}
_tracking_times: dict[str, list] = {}

# ──────────────────────────────────────────
# GET STATUS
# ──────────────────────────────────────────
def get_status(item_id: str) -> dict:
    """
    Calculates progress and returns current simulation status.
    """
    if item_id not in _tracking_state:
        _init_tracking(item_id)

    current_stage = _tracking_state[item_id]
    stage_data    = TRACKING_STAGES[current_stage]
    
    
    progress_map = {0: 35, 1: 45, 2: 60, 3: 75, 4: 90, 5: 100}
    calculated_progress = progress_map.get(current_stage, 35)

    times = _tracking_times.get(item_id, [])
    timeline = []
    for i, stage in enumerate(TRACKING_STAGES):
        timeline.append({
            "status":      stage["status"],
            "description": stage["description"],
            "icon":        stage["icon"],
            "label":       stage["label"],
            "completed":   i <= current_stage,
            "active":      i == current_stage,
            "timestamp":   times[i] if i < len(times) else None
        })

    return {
        "status":            stage_data["status"],
        "current_state":     stage_data["status"], 
        "label":             stage_data["label"],
        "description":       stage_data["description"],
        "progress":          calculated_progress,  # CRITICAL for frontend switching
        "current_stage":     current_stage,
        "awb":               f"AWB{item_id[:8].upper()}",
        "courier":           "Delhivery",
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%B %d, %Y"),
        "is_delivered":      current_stage == len(TRACKING_STAGES) - 1,
        "timeline":          timeline
    }
# ──────────────────────────────────────────
# ADVANCE STAGE (for demo)
# ──────────────────────────────────────────
def advance_stage(item_id: str) -> dict:
    """
    Manually advance tracking to next stage.
    Used during demo to show progression.
    """
    if item_id not in _tracking_state:
        _init_tracking(item_id)

    current = _tracking_state[item_id]
    if current < len(TRACKING_STAGES) - 1:
        _tracking_state[item_id] += 1
        _tracking_times[item_id].append(
            datetime.now().strftime("%b %d, %I:%M %p")
        )
        log("fake_tracking",
            f"🎬 Advanced to stage {_tracking_state[item_id]} "
            f"for {item_id}")

    return get_status(item_id)

# ──────────────────────────────────────────
# INIT TRACKING
# ──────────────────────────────────────────
def _init_tracking(item_id: str):
    """Initialize tracking for item."""
    _tracking_state[item_id] = 0
    now = datetime.now()
    _tracking_times[item_id] = [
        now.strftime("%b %d, %I:%M %p")
    ]
    log("fake_tracking",
        f"🎬 Tracking initialized for {item_id}")

# ──────────────────────────────────────────
# RESET (for demo restart)
# ──────────────────────────────────────────
def reset_tracking(item_id: str):
    """Reset tracking to beginning."""
    if item_id in _tracking_state:
        del _tracking_state[item_id]
    if item_id in _tracking_times:
        del _tracking_times[item_id]