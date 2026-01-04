# import json
# import os
# from threading import Lock
# from datetime import datetime

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# STATE_FILE = os.path.join(BASE_DIR, "system_state.json")

# LOCK = Lock()


# def _load_state():
#     if not os.path.exists(STATE_FILE):
#         return []

#     try:
#         with open(STATE_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#             return data if isinstance(data, list) else []
#     except Exception:
#         return []


# def _save_state(state):
#     with open(STATE_FILE, "w", encoding="utf-8") as f:
#         json.dump(state, f, indent=2)


# # =====================================================
# # LOG NEW EMAIL (Already used by message_formatter)
# # =====================================================
# def log_email(entry: dict):
#     with LOCK:
#         state = _load_state()
#         state.append(entry)
#         _save_state(state)


# # =====================================================
# # UPDATE STATUS (🔥 THIS WAS MISSING)
# # =====================================================
# def update_status(reply_id: str, status: str):
#     """
#     Update message status in dashboard/system_state.json
#     """
#     with LOCK:
#         state = _load_state()
#         updated = False

#         for item in state:
#             if item.get("reply_id") == reply_id:
#                 item["status"] = status
#                 item["updated_at"] = datetime.now().isoformat()
#                 updated = True
#                 break

#         if updated:
#             _save_state(state)


import json
import os
from threading import Lock
from datetime import datetime

# =========================================
# SOCKET.IO INSTANCE (INJECTED AT RUNTIME)
# =========================================
socketio = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "email_logs.json")

LOCK = Lock()

# Ensure directory exists (CRITICAL FIX)
os.makedirs(BASE_DIR, exist_ok=True)


# =========================================
# SOCKET.IO SETTER (MANDATORY)
# =========================================
def set_socketio(sock):
    """
    Called ONCE from dashboard_server.py
    """
    global socketio
    socketio = sock
    print("🔗 Socket.IO successfully injected into state_manager")


# =========================================
# FILE HELPERS
# =========================================
def _load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print("❌ Failed to load logs:", e)
        return []


def _save_logs(logs):
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("❌ Failed to save logs:", e)


# =========================================
# LOG NEW EMAIL (REAL-TIME)
# =========================================
def log_email(entry: dict):
    """
    Called when a NEW email is queued
    """
    with LOCK:
        logs = _load_logs()

        normalized = {
            "reply_id": entry.get("reply_id"),
            "user_id": entry.get("user_id"),
            "from": entry.get("from"),
            "subject": entry.get("subject"),
            "priority": entry.get("priority", "NORMAL"),
            "status": entry.get("status", "Queued"),
            "time": entry.get(
                "time",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
        }

        logs.append(normalized)
        _save_logs(logs)

        # 🔥 REAL-TIME PUSH
        if socketio:
            try:
                socketio.emit("email_update", normalized)
            except Exception as e:
                print("❌ Socket.IO emit failed:", e)
        else:
            print("⚠ Socket.IO not available → email_update skipped")


# =========================================
# UPDATE STATUS (REAL-TIME)
# =========================================
def update_status(reply_id: str, status: str):
    """
    Called when WhatsApp sent / replied / failed
    """
    with LOCK:
        logs = _load_logs()
        updated_item = None

        for item in logs:
            if item.get("reply_id") == reply_id:
                item["status"] = status
                item["updated_at"] = datetime.now().isoformat()
                updated_item = item
                break

        if not updated_item:
            print(f"⚠ Reply ID not found for status update: {reply_id}")
            return

        _save_logs(logs)

        # 🔥 REAL-TIME PUSH
        if socketio:
            try:
                socketio.emit("status_update", updated_item)
            except Exception as e:
                print("❌ Socket.IO status emit failed:", e)
        else:
            print("⚠ Socket.IO not available → status_update skipped")
