# agent/state_machine.py
from constants import AgentState
from utils.logger import log # type: ignore

# ──────────────────────────────────────────
# VALID TRANSITIONS
# defines what state can move to what next
# ──────────────────────────────────────────
VALID_TRANSITIONS = {
    AgentState.IDLE: [
        AgentState.ANALYZING
    ],
    AgentState.ANALYZING: [
        AgentState.LISTING,
        AgentState.IDLE           # fallback if analysis fails
    ],
    AgentState.LISTING: [
        AgentState.WAITING_FOR_BUYER,
        AgentState.IDLE           # fallback if listing fails
    ],
    AgentState.WAITING_FOR_BUYER: [
        AgentState.NEGOTIATING,
        AgentState.CANCELLED      # seller cancels listing
    ],
    AgentState.NEGOTIATING: [
        AgentState.DEAL_CONFIRMED,
        AgentState.WAITING_FOR_BUYER,  # negotiation failed, wait for new buyer
        AgentState.CANCELLED
    ],
    AgentState.DEAL_CONFIRMED: [
        AgentState.AWAITING_PAYMENT,
        AgentState.NEGOTIATING,   # buyer backs out, reopen negotiation
        AgentState.CANCELLED
    ],
    AgentState.AWAITING_PAYMENT: [
        AgentState.PAYMENT_CONFIRMED,
        AgentState.DEAL_CONFIRMED,  # payment failed, retry
        AgentState.CANCELLED
    ],
    AgentState.PAYMENT_CONFIRMED: [
        AgentState.SCHEDULING
    ],
    AgentState.SCHEDULING: [
        AgentState.SHIPPING
    ],
    AgentState.SHIPPING: [
        AgentState.DELIVERED,
        AgentState.CANCELLED      # delivery failed
    ],
    AgentState.DELIVERED: [],     # terminal state
    AgentState.CANCELLED: [],     # terminal state
}

# ──────────────────────────────────────────
# STATE METADATA
# human readable info about each state
# ──────────────────────────────────────────
STATE_META = {
    AgentState.IDLE: {
        "label":       "Idle",
        "description": "Waiting for item upload",
        "icon":        "⏸️",
        "color":       "gray"
    },
    AgentState.ANALYZING: {
        "label":       "Analyzing",
        "description": "AI is analyzing your item",
        "icon":        "🔍",
        "color":       "blue"
    },
    AgentState.LISTING: {
        "label":       "Creating Listing",
        "description": "Generating listing and selecting platform",
        "icon":        "📝",
        "color":       "blue"
    },
    AgentState.WAITING_FOR_BUYER: {
        "label":       "Waiting for Buyer",
        "description": "Listing is live, waiting for interested buyers",
        "icon":        "👀",
        "color":       "yellow"
    },
    AgentState.NEGOTIATING: {
        "label":       "Negotiating",
        "description": "Agent is chatting with a buyer",
        "icon":        "💬",
        "color":       "orange"
    },
    AgentState.DEAL_CONFIRMED: {
        "label":       "Deal Confirmed",
        "description": "Price agreed, awaiting payment",
        "icon":        "🤝",
        "color":       "green"
    },
    AgentState.AWAITING_PAYMENT: {
        "label":       "Awaiting Payment",
        "description": "Payment link sent to buyer",
        "icon":        "💳",
        "color":       "orange"
    },
    AgentState.PAYMENT_CONFIRMED: {
        "label":       "Payment Confirmed",
        "description": "Payment received successfully",
        "icon":        "✅",
        "color":       "green"
    },
    AgentState.SCHEDULING: {
        "label":       "Scheduling Pickup",
        "description": "Collecting seller availability and booking courier",
        "icon":        "📅",
        "color":       "blue"
    },
    AgentState.SHIPPING: {
        "label":       "Shipping",
        "description": "Item picked up and in transit",
        "icon":        "🚚",
        "color":       "blue"
    },
    AgentState.DELIVERED: {
        "label":       "Delivered",
        "description": "Item delivered successfully",
        "icon":        "🎉",
        "color":       "green"
    },
    AgentState.CANCELLED: {
        "label":       "Cancelled",
        "description": "Transaction was cancelled",
        "icon":        "❌",
        "color":       "red"
    },
}

# ──────────────────────────────────────────
# STATE MACHINE CLASS
# ──────────────────────────────────────────
class StateMachine:

    def __init__(self, current_state: str = AgentState.IDLE):
        self.current_state = current_state

    def can_transition(self, to_state: str) -> bool:
        """Check if transition from current to target state is valid."""
        allowed = VALID_TRANSITIONS.get(self.current_state, [])
        return to_state in allowed

    def transition(self, to_state: str, item_id: str = "") -> bool:
        """
        Attempt to transition to a new state.
        Returns True if successful, False if invalid.
        """
        if self.can_transition(to_state):
            old_state = self.current_state
            self.current_state = to_state
            log(
                "state_machine",
                f"[{item_id}] {old_state} → {to_state}",
                "SUCCESS"
            )
            return True
        else:
            log(
                "state_machine",
                f"[{item_id}] Invalid transition: {self.current_state} → {to_state}",
                "ERROR"
            )
            return False

    def get_meta(self) -> dict:
        """Get human readable info about current state."""
        return STATE_META.get(self.current_state, {})

    def is_terminal(self) -> bool:
        """Check if current state is a terminal state."""
        return self.current_state in [
            AgentState.DELIVERED,
            AgentState.CANCELLED
        ]

    def is_active(self) -> bool:
        """Check if agent is actively working."""
        return not self.is_terminal() and \
               self.current_state != AgentState.IDLE

    def get_progress_percent(self) -> int:
        """Returns progress percentage for dashboard progress bar."""
        progress_map = {
            AgentState.IDLE:              0,
            AgentState.ANALYZING:        10,
            AgentState.LISTING:          20,
            AgentState.WAITING_FOR_BUYER:35,
            AgentState.NEGOTIATING:      50,
            AgentState.DEAL_CONFIRMED:   65,
            AgentState.AWAITING_PAYMENT: 72,
            AgentState.PAYMENT_CONFIRMED:80,
            AgentState.SCHEDULING:       88,
            AgentState.SHIPPING:         93,
            AgentState.DELIVERED:       100,
            AgentState.CANCELLED:         0,
        }
        return progress_map.get(self.current_state, 0)

    def __repr__(self):
        meta = self.get_meta()
        return f"<StateMachine [{meta.get('icon')}] {self.current_state}>"