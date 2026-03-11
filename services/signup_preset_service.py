import config


def build_signup_payload(
    *,
    title: str,
    description: str,
    leader: str,
    start_ts: int,
    channel_id: int,
    users: dict | None = None,
) -> dict:
    return {
        "title": title,
        "description": description,
        "leader": leader,
        "start_ts": start_ts,
        "channel_id": channel_id,
        "users": users or {},
        "expected_players": [
            str(player_id)
            for player_id in getattr(config, "DEFAULT_EXPECTED_PLAYERS", [])
        ],
        "missing_signup_reminders_sent": {
            "2880": False,
            "1440": False,
        },
        "signed_player_reminders_sent": {
            "60": False,
        },
    }