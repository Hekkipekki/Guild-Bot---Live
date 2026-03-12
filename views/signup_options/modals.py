import asyncio
import discord

from services.character_service import update_character_name, update_character_spec
from services.signup_service import (
    update_user_name,
    update_user_note,
)
from services.signup_ui_service import (
    refresh_main_signup_from_channel,
)
from utils.ui_timing import (
    SIGNUP_OPTIONS_AUTO_DELETE_SECONDS,
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
)
from .helpers import get_signup_entry, delete_ephemeral_after
from .embeds import build_signup_options_embed


async def _show_modal_error(interaction: discord.Interaction, message: str) -> None:
    if interaction.response.is_done():
        return

    await interaction.response.send_message(message, ephemeral=True)
    asyncio.create_task(
        delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
    )


class EditNameModal(discord.ui.Modal, title="Edit Character Name"):
    new_name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Enter your in-game name",
        max_length=32,
    )

    def __init__(self, raid_id: int, user_id: int):
        super().__init__()
        self.raid_id = raid_id
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        entry = get_signup_entry(self.raid_id, str(self.user_id))
        if not entry:
            await _show_modal_error(interaction, "Signup not found.")
            return

        new_name = str(self.new_name).strip()
        class_name = entry.get("class")

        ok = update_user_name(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
            new_name=new_name,
        )

        if not ok:
            await _show_modal_error(interaction, "Signup not found.")
            return

        if class_name:
            update_character_name(self.user_id, class_name, new_name)

        refreshed = await refresh_main_signup_from_channel(interaction, self.raid_id)
        if not refreshed:
            return

        updated = get_signup_entry(self.raid_id, str(self.user_id))
        if not updated:
            await _show_modal_error(interaction, "Signup not found.")
            return

        from .options_view import SignupOptionsView

        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(updated),
            view=SignupOptionsView(self.raid_id, self.user_id),
        )

        asyncio.create_task(
            delete_ephemeral_after(interaction, SIGNUP_OPTIONS_AUTO_DELETE_SECONDS)
        )


class EditNoteModal(discord.ui.Modal, title="Edit Note"):
    new_note = discord.ui.TextInput(
        label="Note",
        placeholder="Optional note for raid leader",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=200,
    )

    def __init__(self, raid_id: int, user_id: int):
        super().__init__()
        self.raid_id = raid_id
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        ok = update_user_note(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
            note=str(self.new_note).strip(),
        )

        if not ok:
            await _show_modal_error(interaction, "Signup not found.")
            return

        refreshed = await refresh_main_signup_from_channel(interaction, self.raid_id)
        if not refreshed:
            return

        updated = get_signup_entry(self.raid_id, str(self.user_id))
        if not updated:
            await _show_modal_error(interaction, "Signup not found.")
            return

        from .options_view import SignupOptionsView

        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(updated),
            view=SignupOptionsView(self.raid_id, self.user_id),
        )

        asyncio.create_task(
            delete_ephemeral_after(interaction, SIGNUP_OPTIONS_AUTO_DELETE_SECONDS)
        )