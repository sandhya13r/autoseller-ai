# utils/logger.py
from datetime import datetime

agent_logs = []

def log(module: str, message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "module":    module,
        "message":   message,
        "level":     level
    }
    agent_logs.append(entry)
    if len(agent_logs) > 100:
        agent_logs.pop(0)
    icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️"}.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} [{module.upper()}] {message}")

def get_logs() -> list:
    return agent_logs

def clear_logs():
    agent_logs.clear()