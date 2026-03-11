import discord

from utils.permissions import can_manage_raid_tools
from views.signup.raid_control_view import RaidControlView


class RaidControlButton(discord.ui.Button):
    def __init__(self, raid_id: str, row: int = 1):
        super().__init__(
            label="Raid Control",
            style=discord.ButtonStyle.secondary,
            row=row,
            custom_id=f"raid_control:{raid_id}",
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        if not can_manage_raid_tools(interaction.user):
            await interaction.response.send_message(
                "You do not have access to raid controls.",
                ephemeral=True,
            )
            return

        view = RaidControlView(self.raid_id)

        await interaction.response.send_message(
            "Raid control panel",
            view=view,
            ephemeral=True,
        )