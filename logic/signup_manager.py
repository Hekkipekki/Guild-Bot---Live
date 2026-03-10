import time
import discord

from data.signup_store import load_signups, save_signups, get_message_signup
from logic.embed_builder import build_signup_embed


async def refresh_signup_message(interaction: discord.Interaction, raid_id: int) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)

    title = signup.get("title", "Raid Signup")
    description = signup.get("description", "")
    embed = build_signup_embed(title, description, signup)

    from views.signup_views import SignupView

    await interaction.message.edit(
        embed=embed,
        view=SignupView(str(raid_id)),
    )


async def refresh_signup_message_by_id(
    channel: discord.abc.Messageable,
    raid_id: int,
) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)

    title = signup.get("title", "Raid Signup")
    description = signup.get("description", "")
    embed = build_signup_embed(title, description, signup)

    from views.signup_views import SignupView

    message = await channel.fetch_message(raid_id)
    await message.edit(
        embed=embed,
        view=SignupView(str(raid_id)),
    )


def get_signup_user(raid_id: int, user_id: str) -> dict | None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    return signup.get("users", {}).get(user_id)


def set_user_status(raid_id: int, user_id: str, status: str) -> tuple[bool, str | None]:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    users.setdefault(user_id, {})

    if users[user_id].get("spec") in ("", "Unknown", None):
        return False, "⚠ Please select your class first from the dropdown."

    users[user_id]["status"] = status
    users[user_id]["timestamp"] = time.time()
    users[user_id].setdefault("note", "")
    users[user_id].setdefault("name", "")

    save_signups(data)
    return True, None


def remove_user_signup(raid_id: int, user_id: str) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    if user_id in users:
        del users[user_id]

    save_signups(data)


def set_user_class(raid_id: int, user_id: str, selected_class: str) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    users.setdefault(user_id, {})
    users[user_id]["class"] = selected_class
    users[user_id]["spec"] = ""
    users[user_id]["role"] = ""
    users[user_id]["timestamp"] = time.time()
    users[user_id].setdefault("name", "")
    users[user_id].setdefault("note", "")

    save_signups(data)


def set_user_spec(
    raid_id: int,
    user_id: str,
    selected_class: str,
    selected_spec: str,
    role: str,
    *,
    character_name: str | None = None,
    auto_sign: bool = False,
) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    users.setdefault(user_id, {})
    entry = users[user_id]

    entry["class"] = selected_class
    entry["spec"] = selected_spec
    entry["role"] = role
    entry["timestamp"] = time.time()

    if character_name is not None:
        entry["name"] = character_name
    else:
        entry.setdefault("name", f"{selected_spec} {selected_class}")

    entry.setdefault("note", "")

    if auto_sign:
        entry["status"] = "sign"
    else:
        entry.pop("status", None)

    save_signups(data)


def update_user_name(raid_id: int, user_id: str, new_name: str) -> bool:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    if user_id not in users:
        return False

    users[user_id]["name"] = new_name.strip()
    users[user_id]["timestamp"] = time.time()
    users[user_id].setdefault("note", "")

    save_signups(data)
    return True


def update_user_note(raid_id: int, user_id: str, note: str) -> bool:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    if user_id not in users:
        return False

    users[user_id]["note"] = note.strip()
    users[user_id]["timestamp"] = time.time()
    users[user_id].setdefault("name", "")

    save_signups(data)
    return True


def update_user_spec(
    raid_id: int,
    user_id: str,
    selected_class: str,
    selected_spec: str,
    role: str,
) -> bool:
    data = load_signups()
    signup = get_message_signup(data, raid_id)
    users = signup["users"]

    if user_id not in users:
        return False

    entry = users[user_id]
    entry["class"] = selected_class
    entry["spec"] = selected_spec
    entry["role"] = role
    entry["timestamp"] = time.time()
    entry.setdefault("note", "")
    entry.setdefault("name", f"{selected_spec} {selected_class}")

    save_signups(data)
    return True