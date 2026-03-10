import json
import os

FILE = "data/characters.json"


def load_characters():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_characters(data):
    os.makedirs(os.path.dirname(FILE), exist_ok=True)

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_user_characters(user_id: int):
    data = load_characters()
    return data.get(str(user_id), [])


def get_character_by_class(user_id: int, class_name: str):
    characters = get_user_characters(user_id)

    for char in characters:
        if char.get("class") == class_name:
            return char

    return None


def add_character(user_id: int, char: dict):
    data = load_characters()
    user = str(user_id)

    if user not in data:
        data[user] = []

    existing = data[user]

    # max 1 saved character per class
    for saved in existing:
        if saved.get("class") == char.get("class"):
            return False

    existing.append(char)
    save_characters(data)
    return True


def remove_character(user_id: int, index: int):
    data = load_characters()
    user = str(user_id)

    if user in data and 0 <= index < len(data[user]):
        data[user].pop(index)
        save_characters(data)
        return True

    return False


def update_character_name_by_class(user_id: int, class_name: str, new_name: str) -> bool:
    data = load_characters()
    user = str(user_id)

    if user not in data:
        return False

    for char in data[user]:
        if char.get("class") == class_name:
            char["name"] = new_name.strip()
            save_characters(data)
            return True

    return False


def update_character_spec_by_class(user_id: int, class_name: str, new_spec: str, new_role: str) -> bool:
    data = load_characters()
    user = str(user_id)

    if user not in data:
        return False

    for char in data[user]:
        if char.get("class") == class_name:
            char["spec"] = new_spec
            char["role"] = new_role
            save_characters(data)
            return True

    return False