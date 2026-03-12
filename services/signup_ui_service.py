import asyncio
import discord

from services.signup_refresh_service import (
    refresh_signup_message,
    refresh_signup_message_by_id,
)
from views.signup_options.embeds import build_signup_options_embed
from views.signup_options.helpers import (
    get_signup_entry,
    delete_ephemeral_after,
    delete_followup_message_after,
)
from utils.ui_timing import (
    SIGNUP_OPTIONS_AUTO_DELETE_SECONDS,
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
)


async def _send_error_response(
    interaction: discord.Interaction,
    message: str,
) -> None:
    if interaction.response.is_done():
        msg = await interaction.followup.send(
            message,
            ephemeral=True,
            wait=True,
        )
        asyncio.create_task(
            delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True,
        )
        asyncio.create_task(
            delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
        )


async def refresh_main_signup_from_interaction(
    interaction: discord.Interaction,
    raid_id: int,
) -> bool:
    try:
        ok = await refresh_signup_message(interaction, raid_id)
        if not ok:
            await _send_error_response(
                interaction,
                "⚠ Raid signup no longer exists.",
            )
            return False
        return True

    except discord.NotFound:
        await _send_error_response(
            interaction,
            "⚠ Could not find the signup message.",
        )
        return False

    except Exception as e:
        await _send_error_response(
            interaction,
            f"⚠ Could not refresh signup message: {e}",
        )
        return False


async def refresh_main_signup_from_channel(
    interaction: discord.Interaction,
    raid_id: int,
) -> bool:
    try:
        ok = await refresh_signup_message_by_id(interaction.channel, raid_id)
        if not ok:
            await _send_error_response(
                interaction,
                "⚠ Raid signup no longer exists.",
            )
            return False
        return True

    except discord.NotFound:
        await _send_error_response(
            interaction,
            "⚠ Could not find the signup message.",
        )
        return False

    except Exception as e:
        await _send_error_response(
            interaction,
            f"⚠ Could not refresh signup message: {e}",
        )
        return False


async def show_signup_options_panel(
    interaction: discord.Interaction,
    raid_id: int,
    user_id: int,
    *,
    delete_after: int = SIGNUP_OPTIONS_AUTO_DELETE_SECONDS,
) -> bool:
    from views.signup_options.options_view import SignupOptionsView

    entry = get_signup_entry(raid_id, str(user_id))
    if not entry:
        await _send_error_response(
            interaction,
            "⚠ Could not load signup options.",
        )
        return False

    if interaction.response.is_done():
        msg = await interaction.followup.send(
            embed=build_signup_options_embed(entry),
            view=SignupOptionsView(raid_id, user_id),
            ephemeral=True,
            wait=True,
        )
        asyncio.create_task(delete_followup_message_after(msg, delete_after))
    else:
        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(entry),
            view=SignupOptionsView(raid_id, user_id),
        )
        asyncio.create_task(delete_ephemeral_after(interaction, delete_after))

    return True


async def refresh_and_show_signup_options_from_interaction(
    interaction: discord.Interaction,
    raid_id: int,
    user_id: int,
    *,
    delete_after: int = SIGNUP_OPTIONS_AUTO_DELETE_SECONDS,
) -> bool:
    ok = await refresh_main_signup_from_interaction(interaction, raid_id)
    if not ok:
        return False

    return await show_signup_options_panel(
        interaction,
        raid_id,
        user_id,
        delete_after=delete_after,
    )


async def refresh_and_show_signup_options_from_channel(
    interaction: discord.Interaction,
    raid_id: int,
    user_id: int,
    *,
    delete_after: int = SIGNUP_OPTIONS_AUTO_DELETE_SECONDS,
) -> bool:
    ok = await refresh_main_signup_from_channel(interaction, raid_id)
    if not ok:
        return False

    return await show_signup_options_panel(
        interaction,
        raid_id,
        user_id,
        delete_after=delete_after,
    )