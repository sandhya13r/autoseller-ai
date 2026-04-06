# agent/state_manager.py
from agent.state_machine import StateMachine
from constants import AgentState
from utils.logger import log # type: ignore

# ──────────────────────────────────────────
# IN-MEMORY SESSION STORE
# item_id → StateMachine instance
# ──────────────────────────────────────────
_sessions: dict[str, StateMachine] = {}

# ──────────────────────────────────────────
# CREATE SESSION
# ──────────────────────────────────────────
def create_session(item_id: str) -> StateMachine:
    """Create a new state machine session for an item."""
    sm = StateMachine(AgentState.IDLE)
    _sessions[item_id] = sm
    log("state_manager", f"Session created for item: {item_id}", "SUCCESS")
    return sm

# ──────────────────────────────────────────
# GET SESSION
# ──────────────────────────────────────────
def get_session(item_id: str) -> StateMachine:
    """Get existing session or create new one."""
    if item_id not in _sessions:
        log("state_manager", f"No session found for {item_id}, creating new", "WARN")
        return create_session(item_id)
    return _sessions[item_id]

# ──────────────────────────────────────────
# TRANSITION STATE
# ──────────────────────────────────────────
def transition(item_id: str, to_state: str) -> bool:
    """Transition an item's state machine to a new state."""
    sm = get_session(item_id)
    return sm.transition(to_state, item_id)

# ──────────────────────────────────────────
# GET CURRENT STATE
# ──────────────────────────────────────────
def get_state(item_id: str) -> str:
    """Get current state of an item."""
    sm = get_session(item_id)
    return sm.current_state

# ──────────────────────────────────────────
# GET FULL STATUS
# ──────────────────────────────────────────
def get_status(item_id: str) -> dict:
    """Get full status info for dashboard display."""
    sm = get_session(item_id)
    meta = sm.get_meta()
    return {
        "item_id":          item_id,
        "current_state":    sm.current_state,
        "label":            meta.get("label"),
        "description":      meta.get("description"),
        "icon":             meta.get("icon"),
        "color":            meta.get("color"),
        "progress":         sm.get_progress_percent(),
        "is_terminal":      sm.is_terminal(),
        "is_active":        sm.is_active(),
    }

# ──────────────────────────────────────────
# RESET SESSION
# ──────────────────────────────────────────
def reset_session(item_id: str):
    """Reset item back to idle state."""
    if item_id in _sessions:
        _sessions[item_id] = StateMachine(AgentState.IDLE)
        log("state_manager", f"Session reset for item: {item_id}", "WARN")

# ──────────────────────────────────────────
# DELETE SESSION
# ──────────────────────────────────────────
def delete_session(item_id: str):
    """Remove session from memory."""
    if item_id in _sessions:
        del _sessions[item_id]
        log("state_manager", f"Session deleted for item: {item_id}")

# ──────────────────────────────────────────
# GET ALL ACTIVE SESSIONS
# ──────────────────────────────────────────
def get_all_sessions() -> dict:
    """Get status of all active sessions."""
    return {
        item_id: get_status(item_id)
        for item_id in _sessions
    }