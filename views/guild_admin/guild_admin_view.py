import asyncio
import discord

from utils.discord_utils import delete_interaction_after
from utils.ui_timing import RAID_CONTROL_AUTO_DELETE_SECONDS
from views.guild_admin.guild_admin_helpers import build_guild_config_embed
from views.guild_admin.guild_admin_modals import EditDefaultDescriptionModal
from views.guild_admin.guild_admin_manage_views import (
    RaidAdminManageChoiceView,
    RaidTeamManageChoiceView,
    WeakAurasChannelManageView,
)


class RefreshGuildConfigButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Show Config",
            style=discord.ButtonStyle.secondary,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content=None,
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class EditDefaultDescriptionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Edit Description",
            style=discord.ButtonStyle.secondary,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(EditDefaultDescriptionModal(guild.id))


class RaidAdminsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Raid Admins",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Manage raid admins.",
            embed=None,
            view=RaidAdminManageChoiceView(),
        )


class RaidTeamButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Raid Team",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Manage raid team.",
            embed=None,
            view=RaidTeamManageChoiceView(),
        )


class SetWeakAurasChannelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="WeakAuras Channel",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select the channel to use for WeakAuras posts.",
            embed=None,
            view=WeakAurasChannelManageView(),
        )


class GuildAdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(RefreshGuildConfigButton())
        self.add_item(EditDefaultDescriptionButton())
        self.add_item(RaidAdminsButton())
        self.add_item(RaidTeamButton())
        self.add_item(SetWeakAurasChannelButton())