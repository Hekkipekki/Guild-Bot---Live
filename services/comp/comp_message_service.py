import discord

from data.signup_store import load_signups, save_signups, find_message_signup
from logic.embed.comp_embed import build_comp_embed


def _apply_signup_metadata_to_comp_data(signup: dict, comp_data: dict) -> dict:
    updated = dict(comp_data)
    updated["title"] = signup.get("title", updated.get("title", "Raid Comp"))
    updated["description"] = signup.get("description", updated.get("description", ""))
    updated["leader"] = signup.get("leader", updated.get("leader", ""))
    updated["start_ts"] = signup.get("start_ts", updated.get("start_ts"))
    return updated


async def post_comp_message(channel, comp_data: dict) -> tuple[bool, str]:
    data = load_signups()
    raid_id = comp_data["raid_id"]
    signup = find_message_signup(data, raid_id)

    if not signup:
        return False, "Raid not found."

    comp_data = _apply_signup_metadata_to_comp_data(signup, comp_data)

    embed = build_comp_embed(comp_data)
    mentions = " ".join(comp_data.get("mentions", []))
    message_id = signup.get("comp_message_id")

    try:
        # EDIT existing comp message
        if message_id:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(content=mentions, embed=embed)

                signup["last_comp_data"] = comp_data
                save_signups(data)

                return True, "Comp updated."
            except discord.NotFound:
                signup["comp_message_id"] = None
                save_signups(data)

        # CREATE new comp message
        msg = await channel.send(
            content=mentions,
            embed=embed,
        )

        signup["comp_message_id"] = msg.id
        signup["last_comp_data"] = comp_data
        save_signups(data)

        return True, "Comp posted."

    except Exception as e:
        return False, str(e)


async def refresh_existing_comp_message(channel, raid_id: int | str) -> tuple[bool, str]:
    data = load_signups()
    signup = find_message_signup(data, raid_id)

    if not signup:
        return False, "Raid not found."

    comp_message_id = signup.get("comp_message_id")
    last_comp_data = signup.get("last_comp_data")

    if not comp_message_id or not last_comp_data:
        return True, "No existing comp message to refresh."

    updated_comp_data = _apply_signup_metadata_to_comp_data(signup, last_comp_data)
    embed = build_comp_embed(updated_comp_data)
    mentions = " ".join(updated_comp_data.get("mentions", []))

    try:
        msg = await channel.fetch_message(comp_message_id)
        await msg.edit(content=mentions, embed=embed)

        signup["last_comp_data"] = updated_comp_data
        save_signups(data)

        return True, "Comp metadata refreshed."

    except discord.NotFound:
        signup["comp_message_id"] = None
        save_signups(data)
        return False, "Existing comp message was not found."

    except Exception as e:
        return False, str(e)