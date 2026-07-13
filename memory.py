import json
import os

from config import USER_MEMORY


def load_users():
    if not os.path.exists(USER_MEMORY):
        return {}

    with open(USER_MEMORY, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USER_MEMORY, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def remember(chat_id, key, value):
    users = load_users()

    chat_id = str(chat_id)

    if chat_id not in users:
        users[chat_id] = {}

    users[chat_id][key] = value

    save_users(users)


def recall(chat_id):
    users = load_users()

    return users.get(str(chat_id), {})
