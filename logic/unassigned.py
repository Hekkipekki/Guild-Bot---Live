def is_user_assigned(info: dict) -> bool:
    if not info:
        return False

    spec = info.get("spec")
    role = info.get("role")
    status = info.get("status")

    return spec not in ("", "Unknown", None) and role not in ("", "Unknown", None) and status not in (None, "")


def get_unassigned_players(signup: dict) -> list[str]:
    expected_players = signup.get("expected_players", [])
    users = signup.get("users", {})

    unassigned = []

    for user_id in expected_players:
        info = users.get(str(user_id))
        if not is_user_assigned(info):
            unassigned.append(str(user_id))

    return unassigned