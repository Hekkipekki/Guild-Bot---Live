from data.signup_store import load_signups, save_signups
from services.signup_refresh_service import refresh_signup_message


def get_signup_data(raid_id: str):
    data = load_signups()
    return data.get(str(raid_id))


def get_players(raid_id: str):
    signup = get_signup_data(raid_id)

    if not signup:
        return []

    users = signup.get("users", {})

    players = []

    for user_id, entry in users.items():
        players.append({
            "user_id": user_id,
            "name": entry.get("name", "Unknown"),
            "class": entry.get("class"),
            "spec": entry.get("spec"),
            "status": entry.get("status")
        })

    return players


def set_player_status(raid_id: str, user_id: str, new_status: str):

    data = load_signups()

    raid = data.get(str(raid_id))

    if not raid:
        return False

    users = raid.get("users", {})

    if user_id not in users:
        return False

    users[user_id]["status"] = new_status

    save_signups(data)

    return True


def remove_player_signup(raid_id: str, user_id: str):

    data = load_signups()

    raid = data.get(str(raid_id))

    if not raid:
        return False

    users = raid.get("users", {})

    if user_id not in users:
        return False

    del users[user_id]

    save_signups(data)

    return True


async def refresh_raid(bot, raid_id: str):
    """
    Rebuild and update the raid signup embed.
    """
    await refresh_signup_message(bot, raid_id)