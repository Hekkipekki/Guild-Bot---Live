import discord


class RaidControlView(discord.ui.View):
    def __init__(self, raid_id: str, bot=None):
        super().__init__(timeout=120)
        self.raid_id = raid_id
        self.bot = bot

    @discord.ui.button(label="Set Status", style=discord.ButtonStyle.primary, row=0)
    async def set_status(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_message(
            f"Set Status for raid {self.raid_id} coming next.",
            ephemeral=True,
        )

    @discord.ui.button(label="Remove Signup", style=discord.ButtonStyle.danger, row=0)
    async def remove_signup(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_message(
            f"Remove Signup for raid {self.raid_id} coming next.",
            ephemeral=True,
        )

    @discord.ui.button(label="Refresh Raid", style=discord.ButtonStyle.secondary, row=1)
    async def refresh_raid_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if self.bot is None:
            await interaction.response.send_message(
                "Bot reference is missing, cannot refresh raid.",
                ephemeral=True,
            )
            return

        try:
            from services.raid_control_service import refresh_raid
            await refresh_raid(self.bot, self.raid_id)

            await interaction.response.send_message(
                "Raid refreshed.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Failed to refresh raid: {e}",
                ephemeral=True,
            )