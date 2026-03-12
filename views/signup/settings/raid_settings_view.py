import asyncio
import discord

from utils.ui_timing import RAID_CONTROL_AUTO_DELETE_SECONDS
from utils.discord_utils import delete_interaction_after
from views.signup.settings.raid_settings_modals import (
    EditRaidTitleModal,
    EditRaidDescriptionModal,
    EditRaidLeaderModal,
    EditRaidDateModal,
    EditRaidTimeModal,
)


class EditRaidTitleButton(discord.ui.Button):
    def __init__(self, raid_id: str):
        super().__init__(
            label="Edit Title",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditRaidTitleModal(int(self.raid_id)))


class EditRaidDescriptionButton(discord.ui.Button):
    def __init__(self, raid_id: str):
        super().__init__(
            label="Edit Description",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditRaidDescriptionModal(int(self.raid_id)))


class EditRaidLeaderButton(discord.ui.Button):
    def __init__(self, raid_id: str):
        super().__init__(
            label="Edit Leader",
            style=discord.ButtonStyle.secondary,
            row=1,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditRaidLeaderModal(int(self.raid_id)))


class EditRaidDateButton(discord.ui.Button):
    def __init__(self, raid_id: str):
        super().__init__(
            label="Edit Date",
            style=discord.ButtonStyle.secondary,
            row=1,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditRaidDateModal(int(self.raid_id)))


class EditRaidTimeButton(discord.ui.Button):
    def __init__(self, raid_id: str):
        super().__init__(
            label="Edit Time",
            style=discord.ButtonStyle.secondary,
            row=2,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditRaidTimeModal(int(self.raid_id)))


class BackToRaidControlButton(discord.ui.Button):
    def __init__(self, raid_id: str):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.primary,
            row=3,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        from views.signup.raid_control.raid_control_view import RaidControlView

        await interaction.response.edit_message(
            content="Raid control panel",
            view=RaidControlView(self.raid_id),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidSettingsView(discord.ui.View):
    def __init__(self, raid_id: str):
        super().__init__(timeout=120)
        self.add_item(EditRaidTitleButton(raid_id))
        self.add_item(EditRaidDescriptionButton(raid_id))
        self.add_item(EditRaidLeaderButton(raid_id))
        self.add_item(EditRaidDateButton(raid_id))
        self.add_item(EditRaidTimeButton(raid_id))
        self.add_item(BackToRaidControlButton(raid_id))