# agent/memory.py
from datetime import datetime
from utils.logger import log

_memory: dict[str, dict] = {}

def init(item_id: str):
    _memory[item_id] = {
        "item_id":          item_id,
        "item_data":        None,
        "listing_data":     None,
        "platform":         None,
        "asking_price":     None,
        "min_price":        None,
        "buyer_info":       None,
        "buyer_profile":    None,
        "chat_history":     [],
        "current_offer":    None,
        "counter_rounds":   0,
        "final_price":      None,
        "negotiation_id":   None,
        "transaction_id":   None,
        "shipment_id":      None,
        "created_at":       datetime.now().isoformat()
    }
    log("memory", f"Memory initialized for item: {item_id}")

def get(item_id: str, key: str = None):
    if item_id not in _memory:
        init(item_id)
    if key:
        return _memory[item_id].get(key)
    return _memory[item_id]

def set(item_id: str, key: str, value):
    if item_id not in _memory:
        init(item_id)
    _memory[item_id][key] = value
    log("memory", f"[{item_id}] {key} updated")

def update(item_id: str, data: dict):
    if item_id not in _memory:
        init(item_id)
    _memory[item_id].update(data)
    log("memory", f"[{item_id}] Memory updated: {list(data.keys())}")

def add_chat_message(item_id: str, role: str, message: str):
    if item_id not in _memory:
        init(item_id)
    entry = {
        "role":      role,
        "message":   message,
        "timestamp": datetime.now().isoformat()
    }
    _memory[item_id]["chat_history"].append(entry)

def get_chat_history(item_id: str) -> list:
    return get(item_id, "chat_history") or []

def get_gemini_history(item_id: str) -> list:
    history = get_chat_history(item_id)
    gemini_history = []
    for entry in history:
        role = "user" if entry["role"] == "buyer" else "model"
        gemini_history.append({
            "role":  role,
            "parts": [entry["message"]]
        })
    return gemini_history

def clear(item_id: str):
    if item_id in _memory:
        del _memory[item_id]
        log("memory", f"Memory cleared for item: {item_id}")

def get_all() -> dict:
    return _memory