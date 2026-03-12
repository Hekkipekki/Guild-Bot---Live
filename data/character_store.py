import json
from pathlib import Path


FILE = Path(__file__).resolve().parent / "characters.json"


def _ensure_data_dir() -> None:
    FILE.parent.mkdir(parents=True, exist_ok=True)


def load_characters() -> dict:
    if not FILE.exists():
        return {}

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_characters(data: dict) -> None:
    _ensure_data_dir()

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_user_characters(user_id: int) -> list[dict]:
    data = load_characters()
    user_chars = data.get(str(user_id), [])
    return user_chars if isinstance(user_chars, list) else []


def get_character_by_class(user_id: int, class_name: str) -> dict | None:
    characters = get_user_characters(user_id)

    for char in characters:
        if char.get("class") == class_name:
            return char

    return None


def add_character(user_id: int, char: dict) -> bool:
    data = load_characters()
    user = str(user_id)

    if user not in data or not isinstance(data[user], list):
        data[user] = []

    existing = data[user]

    for saved in existing:
        if saved.get("class") == char.get("class"):
            return False

    existing.append(char)
    save_characters(data)
    return True


def remove_character(user_id: int, index: int) -> bool:
    data = load_characters()
    user = str(user_id)

    if user not in data or not isinstance(data[user], list):
        return False

    if not (0 <= index < len(data[user])):
        return False

    data[user].pop(index)
    save_characters(data)
    return True


def update_character_name_by_class(user_id: int, class_name: str, new_name: str) -> bool:
    data = load_characters()
    user = str(user_id)

    if user not in data or not isinstance(data[user], list):
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

    if user not in data or not isinstance(data[user], list):
        return False

    for char in data[user]:
        if char.get("class") == class_name:
            char["spec"] = new_spec
            char["role"] = new_role
            save_characters(data)
            return True

    return False