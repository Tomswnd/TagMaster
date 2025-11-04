import json
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def _get_path(chat_id):
    return os.path.join(DATA_DIR, f"group_{chat_id}.json")

def load_categories(chat_id):
    path = _get_path(chat_id)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_categories(chat_id, categories):
    path = _get_path(chat_id)
    with open(path, "w") as f:
        json.dump(categories, f, indent=2)

def add_user_to_category(chat_id, category, user_id):
    cats = load_categories(chat_id)
    if category not in cats:
        return False  # categoria non esiste
    if user_id not in cats[category]["members"]:
        cats[category]["members"].append(user_id)
    save_categories(chat_id, cats)
    return True

def create_category(chat_id, category, creator_id):
    cats = load_categories(chat_id)
    if category in cats:
        return False
    cats[category] = {"members": [], "created_by": creator_id}
    save_categories(chat_id, cats)
    return True

def get_category_members(chat_id, category):
    cats = load_categories(chat_id)
    if category not in cats:
        return []
    return cats[category]["members"]
