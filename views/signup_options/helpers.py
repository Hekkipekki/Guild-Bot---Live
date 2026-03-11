import asyncio
import discord

from data.signup_store import load_signups
from utils.emoji_helpers import parse_spec_emoji


AUTO_DELETE_SECONDS = 45


async def delete_ephemeral_after(
    interaction: discord.Interaction,
    seconds: int = AUTO_DELETE_SECONDS,
):
    """
    Deletes the ORIGINAL interaction response.
    Only use this when the original response is the ephemeral message itself.
    """
    try:
        await asyncio.sleep(seconds)
        await interaction.delete_original_response()
    except Exception:
        pass


async def delete_followup_message_after(
    message,
    seconds: int = AUTO_DELETE_SECONDS,
):
    """
    Deletes a FOLLOWUP ephemeral/webhook message returned by
    interaction.followup.send(..., wait=True).
    Safe for temporary ephemeral followups.
    """
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