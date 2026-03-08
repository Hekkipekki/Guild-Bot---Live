import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "signups.json"


def load_signups() -> dict:
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_signups(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_message_signup(data: dict, message_id: int) -> dict:
    key = str(message_id)
    if key not in data:
        data[key] = {
            "title": "",
            "description": "",
            "leader": "",
            "start_ts": None,
            "users": {},
        }
    return data[key]


def init_message_signup(
    data: dict,
    message_id: int,
    title: str,
    description: str,
    leader: str = "",
    start_ts: int | None = None,
) -> None:
    data[str(message_id)] = {
        "title": title,
        "description": description,
        "leader": leader,
        "start_ts": start_ts,
        "users": {},
    }
    save_signups(data)


def remove_message_signup(data: dict, message_id: int) -> None:
    key = str(message_id)
    if key in data:
        del data[key]
        save_signups(data)