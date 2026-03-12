import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent / "guild_settings.json"

DEFAULT_GUILD_SETTINGS = {
    "raid_control_user_ids": [],
    "expected_players": [],
    "default_leader": "",
    "default_description": "",
    "weakauras_channel_id": None,
}


def _ensure_data_dir() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def _build_default_settings() -> dict[str, Any]:
    return dict(DEFAULT_GUILD_SETTINGS)


def load_guild_settings() -> dict[str, dict[str, Any]]:
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_guild_settings(data: dict[str, dict[str, Any]]) -> None:
    _ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_guild_settings(guild_id: int | str) -> dict[str, Any]:
    data = load_guild_settings()
    return data.get(str(guild_id), {})


def ensure_guild_settings(guild_id: int | str) -> dict[str, Any]:
    data = load_guild_settings()
    key = str(guild_id)

    if key not in data:
        data[key] = _build_default_settings()
        save_guild_settings(data)

    return data[key]


def update_guild_settings(guild_id: int | str, updates: dict[str, Any]) -> dict[str, Any]:
    data = load_guild_settings()
    key = str(guild_id)

    if key not in data:
        data[key] = _build_default_settings()

    data[key].update(updates)
    save_guild_settings(data)
    return data[key]