import discord
from discord import app_commands
from discord.ext import commands

from utils.permissions import can_manage_raid_tools
from views.raid_builder import RaidStartView


class RaidBuilderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="raid", description="Open the raid creation panel.")
    async def raid(self, interaction: discord.Interaction):
        if not can_manage_raid_tools(interaction.user):
            await interaction.response.send_message(
                "⛔ You do not have access to create raids.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        channel = interaction.channel

        if guild is None or channel is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Raid setup",
            view=RaidStartView(guild.id, channel.id),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(RaidBuilderCommands(bot))