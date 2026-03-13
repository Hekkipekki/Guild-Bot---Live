import asyncio
import discord

from services.guild.guild_settings_service import (
    get_guild_defaults,
    set_default_description,
    add_raid_control_user,
    remove_raid_control_user,
    add_expected_player,
    remove_expected_player,
    set_weakauras_channel_id,
)
from utils.discord_utils import delete_interaction_after
from utils.ui_timing import RAID_CONTROL_AUTO_DELETE_SECONDS, ERROR_MESSAGE_AUTO_DELETE_SECONDS


def build_guild_config_embed(guild: discord.Guild) -> discord.Embed:
    settings = get_guild_defaults(guild.id)

    raid_admins = settings.get("raid_control_user_ids", [])
    raid_team = settings.get("expected_players", [])
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
    embed.add_field(name="Raid Description Template", value=default_description, inline=False)
    embed.add_field(name="Raid Admins", value=raid_admin_text, inline=False)
    embed.add_field(name="Raid Team", value=raid_team_text, inline=False)
    embed.add_field(name="WeakAuras Channel", value=wa_channel_text, inline=False)
    embed.set_footer(text="This admin panel closes automatically.")
    return embed


class EditDefaultDescriptionModal(discord.ui.Modal, title="Edit Raid Description Template"):
    new_description = discord.ui.TextInput(
        label="Raid Description Template",
        placeholder="Example: Be online 10 minutes early, flasks and food required.",
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


class RaidAdminUserSelect(discord.ui.UserSelect):
    def __init__(self, mode: str):
        self.mode = mode
        placeholder = "Select users to add as raid admins..." if mode == "add" else "Select users to remove from raid admins..."

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=25,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("⚠ This command can only be used in a server.", ephemeral=True)
            return

        changed = 0
        for member in self.values:
            if self.mode == "add":
                if add_raid_control_user(guild.id, member.id):
                    changed += 1
            else:
                if remove_raid_control_user(guild.id, member.id):
                    changed += 1

        await interaction.response.edit_message(
            content=f"✅ Updated raid admins. Changed {changed} user(s).",
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidTeamUserSelect(discord.ui.UserSelect):
    def __init__(self, mode: str):
        self.mode = mode
        placeholder = "Select users to add to raid team..." if mode == "add" else "Select users to remove from raid team..."

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=25,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("⚠ This command can only be used in a server.", ephemeral=True)
            return

        changed = 0
        for member in self.values:
            if self.mode == "add":
                if add_expected_player(guild.id, member.id):
                    changed += 1
            else:
                if remove_expected_player(guild.id, member.id):
                    changed += 1

        await interaction.response.edit_message(
            content=f"✅ Updated raid team. Changed {changed} user(s).",
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class BackToGuildAdminButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("⚠ This command can only be used in a server.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=None,
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidAdminManageView(discord.ui.View):
    def __init__(self, mode: str):
        super().__init__(timeout=120)
        self.add_item(RaidAdminUserSelect(mode))
        self.add_item(BackToGuildAdminButton())


class RaidTeamManageView(discord.ui.View):
    def __init__(self, mode: str):
        super().__init__(timeout=120)
        self.add_item(RaidTeamUserSelect(mode))
        self.add_item(BackToGuildAdminButton())


class ManageRaidAdminsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Add Raid Admins",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select users to add as raid admins.",
            embed=None,
            view=RaidAdminManageView("add"),
        )


class RemoveRaidAdminsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Remove Raid Admins",
            style=discord.ButtonStyle.secondary,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select users to remove from raid admins.",
            embed=None,
            view=RaidAdminManageView("remove"),
        )


class ManageRaidTeamButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Add Raid Team",
            style=discord.ButtonStyle.secondary,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select users to add to the raid team.",
            embed=None,
            view=RaidTeamManageView("add"),
        )


class RemoveRaidTeamButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Remove Raid Team",
            style=discord.ButtonStyle.secondary,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select users to remove from the raid team.",
            embed=None,
            view=RaidTeamManageView("remove"),
        )

class WeakAurasChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Select the WeakAuras channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
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

        channel = self.values[0]
        set_weakauras_channel_id(guild.id, channel.id)

        from services.guild.weakauras_panel_service import ensure_weakauras_panel_for_guild

        ok, message = await ensure_weakauras_panel_for_guild(interaction.client, guild)

        status_line = f"✅ WeakAuras channel set to {channel.mention}."
        if message:
            status_line += f"\n{message}"

        await interaction.response.edit_message(
            content=status_line,
            embed=build_guild_config_embed(guild),
            view=GuildAdminView(),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class WeakAurasChannelManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(WeakAurasChannelSelect())
        self.add_item(BackToGuildAdminButton())


class SetWeakAurasChannelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Set WeakAuras Channel",
            style=discord.ButtonStyle.secondary,
            row=3,
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
        self.add_item(ManageRaidAdminsButton())
        self.add_item(RemoveRaidAdminsButton())
        self.add_item(ManageRaidTeamButton())
        self.add_item(RemoveRaidTeamButton())
        self.add_item(SetWeakAurasChannelButton())