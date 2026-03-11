import config


def get_summary_icons() -> dict:
    summary_icons = getattr(config, "SUMMARY_EMOJIS", {})

    return {
        "countdown": summary_icons.get("Countdown", "⏳"),
        "absence": summary_icons.get("Absence", "🚫"),
        "signups": summary_icons.get("Signups", "👥"),
        "dps": summary_icons.get("DPS", "⚔️"),
        "tank": summary_icons.get("Tank", "🛡️"),
        "healer": summary_icons.get("Healer", "➕"),
        "tentative": summary_icons.get("Tentative", "❔"),
        "late": summary_icons.get("Late", "🕒"),
        "calendar": summary_icons.get("Calendar", "📅"),
        "bench": summary_icons.get("Bench", "🪑"),
    }


def count_signed_melee_and_ranged(users: dict) -> tuple[int, int]:
    melee_count = sum(
        1
        for _, info in users.items()
        if info.get("status") == "sign" and info.get("role") == "Melee"
    )
    ranged_count = sum(
        1
        for _, info in users.items()
        if info.get("status") == "sign" and info.get("role") == "Ranged"
    )

    return melee_count, ranged_count


def build_time_fields(start_ts: int | None, calendar_icon: str, countdown_icon: str) -> tuple[str, str, str]:
    if start_ts:
        date_value = f"{calendar_icon} <t:{start_ts}:D>"
        time_value = f"🕒 <t:{start_ts}:t>"
        countdown_value = f"{countdown_icon} <t:{start_ts}:R>"
    else:
        date_value = f"{calendar_icon} -"
        time_value = "🕒 -"
        countdown_value = f"{countdown_icon} -"

    return date_value, time_value, countdown_value