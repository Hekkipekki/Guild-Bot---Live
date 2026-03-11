import asyncio
import discord
import config

from services.signup_service import remove_user_signup
from services.signup_refresh_service import refresh_signup_message_by_id

from .helpers import get_signup_entry, delete_ephemeral_after
from .modals import EditNameModal, EditNoteModal
from .spec_edit_view import EditSpecView


class EditNameButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Edit Name",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditNameModal(self.raid_id, self.user_id))


class EditSpecButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Edit Spec",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        entry = get_signup_entry(self.raid_id, str(self.user_id))
        if not entry:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        selected_class = entry.get("class")
        if not selected_class or selected_class not in config.CLASS_SPECS:
            await interaction.response.send_message(
                "Class not found for this signup.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content="Choose a new spec:",
            embed=None,
            view=EditSpecView(self.raid_id, self.user_id, selected_class),
        )


class EditNoteButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Edit Note",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditNoteModal(self.raid_id, self.user_id))


class RemoveSignupButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Remove Signup",
            style=discord.ButtonStyle.danger,
            row=1,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        remove_user_signup(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
        )

        try:
            await refresh_signup_message_by_id(interaction.channel, self.raid_id)
        except Exception:
            pass

        await interaction.response.edit_message(
            content="❌ Signup removed.",
            embed=None,
            view=None,
        )

        asyncio.create_task(delete_ephemeral_after(interaction, 5))


class SignupOptionsView(discord.ui.View):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(timeout=90)
        self.add_item(EditNameButton(raid_id, user_id))
        self.add_item(EditSpecButton(raid_id, user_id))
        self.add_item(EditNoteButton(raid_id, user_id))
        self.add_item(RemoveSignupButton(raid_id, user_id))