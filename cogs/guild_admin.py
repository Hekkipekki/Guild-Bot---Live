import discord
from discord import app_commands
from discord.ext import commands

from services.guild.guild_settings_service import (
    add_raid_control_user,
    remove_raid_control_user,
    get_raid_control_users,
    add_expected_player,
    remove_expected_player,
    get_expected_players,
    set_default_description,
    get_guild_defaults,
)
from views.guild_admin.guild_admin_view import GuildAdminView, build_guild_config_embed


def _is_guild_admin(interaction: discord.Interaction) -> bool:
    user = interaction.user
    return getattr(user.guild_permissions, "administrator", False)


class GuildAdminCommands(commands.Cog):
    raidadmin = app_commands.Group(
        name="raidadmin",
        description="Manage raid admin access for this server.",
    )

    raidteam = app_commands.Group(
        name="raidteam",
        description="Manage expected raiders for this server.",
    )

    raiddefaults = app_commands.Group(
        name="raiddefaults",
        description="Manage default raid settings for this server.",
    )

    guildconfig = app_commands.Group(
        name="guildconfig",
        description="Show guild bot configuration.",
    )

    def __init__(self, bot):
        self.bot = bot

    async def _deny_if_not_admin(self, interaction: discord.Interaction) -> bool:
        if _is_guild_admin(interaction):
            return False

        await interaction.response.send_message(
            "⛔ You must be a server administrator to use this command.",
            ephemeral=True,
        )
        return True

    async def _get_guild_or_fail(
        self,
        interaction: discord.Interaction,
    ) -> discord.Guild | None:
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return None
        return guild

    @app_commands.command(name="guildadmin", description="Open the guild admin panel.")
    async def guildadmin(self, interaction: discord.Interaction):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        await interaction.response.send_message(
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
            ephemeral=True,
        )

    @raidadmin.command(name="add", description="Give a user raid admin access.")
    async def raidadmin_add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        added = add_raid_control_user(guild.id, user.id)
        if not added:
            await interaction.response.send_message(
                f"⚠ {user.mention} already has raid admin access.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Added {user.mention} to raid admin access.",
            ephemeral=True,
        )

    @raidadmin.command(name="remove", description="Remove a user's raid admin access.")
    async def raidadmin_remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        removed = remove_raid_control_user(guild.id, user.id)
        if not removed:
            await interaction.response.send_message(
                f"⚠ {user.mention} does not currently have raid admin access.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Removed {user.mention} from raid admin access.",
            ephemeral=True,
        )

    @raidadmin.command(name="list", description="Show all users with raid admin access.")
    async def raidadmin_list(self, interaction: discord.Interaction):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        user_ids = get_raid_control_users(guild.id)

        if not user_ids:
            await interaction.response.send_message(
                "No users currently have raid admin access.",
                ephemeral=True,
            )
            return

        lines = [f"- <@{user_id}>" for user_id in user_ids]
        await interaction.response.send_message(
            "**Raid Admins**\n" + "\n".join(lines),
            ephemeral=True,
        )

    @raidteam.command(name="add", description="Add a user to the expected raid team.")
    async def raidteam_add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        added = add_expected_player(guild.id, user.id)
        if not added:
            await interaction.response.send_message(
                f"⚠ {user.mention} is already in the raid team.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Added {user.mention} to the raid team.",
            ephemeral=True,
        )

    @raidteam.command(name="remove", description="Remove a user from the expected raid team.")
    async def raidteam_remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        removed = remove_expected_player(guild.id, user.id)
        if not removed:
            await interaction.response.send_message(
                f"⚠ {user.mention} is not currently in the raid team.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Removed {user.mention} from the raid team.",
            ephemeral=True,
        )

    @raidteam.command(name="list", description="Show the expected raid team for this server.")
    async def raidteam_list(self, interaction: discord.Interaction):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        user_ids = get_expected_players(guild.id)

        if not user_ids:
            await interaction.response.send_message(
                "No raid team members are currently configured.",
                ephemeral=True,
            )
            return

        lines = [f"- <@{user_id}>" for user_id in user_ids]
        await interaction.response.send_message(
            "**Raid Team**\n" + "\n".join(lines),
            ephemeral=True,
        )

    @raiddefaults.command(name="description", description="Set the default raid description text.")
    async def raiddefaults_description(
        self,
        interaction: discord.Interaction,
        description: str,
    ):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        set_default_description(guild.id, description)

        await interaction.response.send_message(
            f"✅ Default raid description set to:\n{description}",
            ephemeral=True,
        )

    @guildconfig.command(name="show", description="Show the current guild bot configuration.")
    async def guildconfig_show(self, interaction: discord.Interaction):
        if await self._deny_if_not_admin(interaction):
            return

        guild = await self._get_guild_or_fail(interaction)
        if guild is None:
            return

        settings = get_guild_defaults(guild.id)

        raid_admins = settings.get("raid_control_user_ids", [])
        raid_team = settings.get("expected_players", [])
        default_description = settings.get("default_description", "") or "-"
        weakauras_channel_id = settings.get("weakauras_channel_id")

        raid_admin_text = "\n".join(f"- <@{user_id}>" for user_id in raid_admins) if raid_admins else "-"
        raid_team_text = "\n".join(f"- <@{user_id}>" for user_id in raid_team) if raid_team else "-"
        wa_channel_text = f"<#{weakauras_channel_id}>" if weakauras_channel_id else "-"

        embed = discord.Embed(
            title="Guild Bot Configuration",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Default Leader", value=default_leader, inline=False)
        embed.add_field(name="Default Description", value=default_description, inline=False)
        embed.add_field(name="Raid Admins", value=raid_admin_text, inline=False)
        embed.add_field(name="Raid Team", value=raid_team_text, inline=False)
        embed.add_field(name="WeakAuras Channel", value=wa_channel_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(GuildAdminCommands(bot))