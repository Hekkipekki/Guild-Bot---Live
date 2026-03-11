import asyncio
import discord

from data.signup_store import load_signups
from utils.emoji_helpers import parse_spec_emoji
from utils.ui_timing import SIGNUP_OPTIONS_AUTO_DELETE_SECONDS


AUTO_DELETE_SECONDS = SIGNUP_OPTIONS_AUTO_DELETE_SECONDS


async def delete_ephemeral_after(
    interaction: discord.Interaction,
    seconds: int = AUTO_DELETE_SECONDS,
):
    try:
        await asyncio.sleep(seconds)
        await interaction.delete_original_response()
    except Exception:
        pass


async def delete_followup_message_after(
    message,
    seconds: int = AUTO_DELETE_SECONDS,
):
    try:
        await asyncio.sleep(seconds)
        await message.delete()
    except Exception:
        pass


def get_signup_entry(raid_id: int, user_id: str) -> dict | None:
    data = load_signups()
    raid = data.get(str(raid_id), {})
    users = raid.get("users", {})
    return users.get(str(user_id))