import asyncio
import discord

from services.guild.guild_settings_service import (
    get_guild_defaults,
    set_default_leader,
    set_default_description,
)
from utils.discord_utils import delete_interaction_after
from utils.ui_timing import RAID_CONTROL_AUTO_DELETE_SECONDS, ERROR_MESSAGE_AUTO_DELETE_SECONDS


def build_guild_config_embed(guild: discord.Guild) -> discord.Embed:
    settings = get_guild_defaults(guild.id)

    raid_admins = settings.get("raid_control_user_ids", [])
    raid_team = settings.get("expected_players", [])
    default_leader = settings.get("default_leader", "") or "-"
    default_description = settings.get("default_description", "") or "-"
    weakauras_channel_id = settings.get("weakauras_channel_id")

    raid_admin_text = "\n".join(f"- <@{user_id}>" for user_id in raid_admins) if raid_admins else "-"
    raid_team_text = "\n".join(f"- <@{user_id}>" for user_id in raid_team) if raid_team else "-"
    wa_channel_text = f"<#{weakauras_channel_id}>" if weakauras_channel_id else "-"

    embed = discord.Embed(
        title=f"Guild Admin — {guild.name}",
        description="Configure this server's raid bot settings.",
        color=discord.Color.purple(),
    )
    embed.add_field(name="Default Leader", value=default_leader, inline=False)
    embed.add_field(name="Default Description", value=default_description, inline=False)
    embed.add_field(name="Raid Admins", value=raid_admin_text, inline=False)
    embed.add_field(name="Raid Team", value=raid_team_text, inline=False)
    embed.add_field(name="WeakAuras Channel", value=wa_channel_text, inline=False)
    embed.set_footer(text="This admin panel closes automatically.")

    return embed


class EditDefaultLeaderModal(discord.ui.Modal, title="Edit Default Raid Leader"):
    new_leader = discord.ui.TextInput(
        label="Default Raid Leader",
        placeholder="Example: Hekkipekki / Rhegaran",
        max_length=100,
    )

    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        set_default_leader(self.guild_id, str(self.new_leader).strip())

        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class EditDefaultDescriptionModal(discord.ui.Modal, title="Edit Default Raid Description"):
    new_description = discord.ui.TextInput(
        label="Default Raid Description",
        placeholder="Example: Continuation of HC Progress",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False,
    )

    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        set_default_description(self.guild_id, str(self.new_description).strip())

        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RefreshGuildConfigButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Show Config",
            style=discord.ButtonStyle.primary,
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
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class EditDefaultLeaderButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Edit Leader",
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

        await interaction.response.send_modal(EditDefaultLeaderModal(guild.id))


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


class RaidAdminsInfoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Raid Admins",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Use `/raidadmin add`, `/raidadmin remove`, and `/raidadmin list` for now.\n"
            "This section will be moved fully into the panel next.",
            ephemeral=True,
        )
        asyncio.create_task(
            delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
        )


class RaidTeamInfoButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Raid Team",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Use `/raidteam add`, `/raidteam remove`, and `/raidteam list` for now.\n"
            "This section will be moved fully into the panel next.",
            ephemeral=True,
        )
        asyncio.create_task(
            delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
        )


class GuildAdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(RefreshGuildConfigButton())
        self.add_item(EditDefaultLeaderButton())
        self.add_item(EditDefaultDescriptionButton())
        self.add_item(RaidAdminsInfoButton())
        self.add_item(RaidTeamInfoButton())