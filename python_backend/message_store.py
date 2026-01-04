# import json
# import uuid
# import os

# # Always store mapping in project directory
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# STORE_FILE = os.path.join(BASE_DIR, "message_map.json")


# def save_mapping(from_email, subject):
#     msg_id = str(uuid.uuid4())

#     # Load existing mappings safely
#     try:
#         with open(STORE_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#             if not isinstance(data, dict):
#                 data = {}
#     except (FileNotFoundError, json.JSONDecodeError):
#         data = {}

#     data[msg_id] = {
#         "from_email": from_email,
#         "subject": subject
#     }

#     # Save back
#     with open(STORE_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

#     return msg_id


# def get_mapping(msg_id):
#     try:
#         with open(STORE_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#             return data.get(msg_id)
#     except (FileNotFoundError, json.JSONDecodeError):
#         return None


# import json
# import os
# from threading import Lock

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# REPLY_MAP_FILE = os.path.join(BASE_DIR, "reply_map.json")

# LOCK = Lock()


# def load_reply_map() -> dict:
#     if not os.path.exists(REPLY_MAP_FILE):
#         return {}

#     try:
#         with open(REPLY_MAP_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#             return data if isinstance(data, dict) else {}
#     except Exception:
#         return {}


# def save_reply_mapping(reply_id: str, email_data: dict):
#     """
#     Save reply_id → email metadata for WhatsApp replies
#     """
#     if not reply_id or not email_data:
#         return

#     with LOCK:
#         data = load_reply_map()
#         data[reply_id] = {
#             "to": email_data.get("from"),
#             "subject": email_data.get("subject"),
#             "message_id": email_data.get("message_id"),
#             "imap_id": email_data.get("imap_id"),
#         }

#         temp = REPLY_MAP_FILE + ".tmp"
#         with open(temp, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=2)
#         os.replace(temp, REPLY_MAP_FILE)


import json
import os
from threading import Lock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPLY_MAP_FILE = os.path.join(BASE_DIR, "reply_map.json")

LOCK = Lock()

# =================================================
# LOAD ALL REPLY MAPPINGS
# =================================================
def load_reply_map() -> dict:
    if not os.path.exists(REPLY_MAP_FILE):
        return {}

    try:
        with open(REPLY_MAP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


# =================================================
# SAVE REPLY → EMAIL + USER MAPPING
# =================================================
def save_reply_mapping(reply_id: str, email_data: dict, user_id: int):
    """
    Stores:
    reply_id → original email metadata + user_id
    """

    if not reply_id or not isinstance(email_data, dict) or not user_id:
        return

    reply_id = str(reply_id)

    with LOCK:
        data = load_reply_map()

        data[reply_id] = {
            "from": email_data.get("from", ""),
            "subject": email_data.get("subject", ""),
            "message_id": email_data.get("message_id", ""),
            "imap_id": email_data.get("imap_id", ""),
            "user_id": int(user_id)
        }

        tmp = REPLY_MAP_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        os.replace(tmp, REPLY_MAP_FILE)


# =================================================
# GET ORIGINAL EMAIL BY REPLY ID
# =================================================
def get_original_email(reply_id: str) -> dict | None:
    if not reply_id:
        return None

    reply_id = str(reply_id)
    data = load_reply_map()
    return data.get(reply_id)


# =================================================
# BACKWARD COMPATIBILITY (SAFE)
# =================================================
def get_reply_mapping(reply_id: str) -> dict | None:
    return get_original_email(reply_id)
