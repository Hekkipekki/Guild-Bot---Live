import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import discord

from services.guild.guild_settings_service import (
    get_default_leader,
    get_default_description,
)
from services.raid.raid_template_service import (
    list_templates,
    save_template,
    build_raid_data_from_template,
    delete_template,
    overwrite_template,
)
from services.signup.signup_message_service import send_signup_message
from services.signup.signup_preset_service import build_signup_payload
from utils.discord_utils import delete_interaction_after
from utils.ui_timing import (
    RAID_CONTROL_AUTO_DELETE_SECONDS,
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
)


SWEDEN_TZ = ZoneInfo("Europe/Stockholm")


def _default_raid_data(guild_id: int, channel_id: int) -> dict:
    now = datetime.now(SWEDEN_TZ)

    return {
        "title": "New Raid Signup",
        "description": get_default_description(guild_id) or "Raid signup",
        "leader": get_default_leader(guild_id) or "Raid Leader",
        "date": now.strftime("%Y-%m-%d"),
        "time": "19:30",
        "channel_id": channel_id,
        "is_recurring": False,
        "recurring_interval_days": None,
    }


def _recurring_text(raid_data: dict) -> str:
    is_recurring = bool(raid_data.get("is_recurring", False))
    interval = raid_data.get("recurring_interval_days")

    if not is_recurring:
        return "No"

    if interval:
        return f"Yes — every {interval} day(s)"

    return "Yes"


def _build_preview_embed(guild: discord.Guild, raid_data: dict) -> discord.Embed:
    title = raid_data.get("title", "New Raid Signup")
    description = raid_data.get("description", "") or "-"
    leader = raid_data.get("leader", "") or "-"
    date_str = raid_data.get("date", "-")
    time_str = raid_data.get("time", "-")
    channel_id = raid_data.get("channel_id")

    channel_text = f"<#{channel_id}>" if channel_id else "-"

    embed = discord.Embed(
        title=f"Raid Builder — {guild.name}",
        description="Configure a new raid signup.",
        color=discord.Color.purple(),
    )
    embed.add_field(name="Title", value=title, inline=False)
    embed.add_field(name="Description", value=description, inline=False)
    embed.add_field(name="Leader", value=leader, inline=False)
    embed.add_field(name="Date", value=date_str, inline=True)
    embed.add_field(name="Time", value=time_str, inline=True)
    embed.add_field(name="Channel", value=channel_text, inline=True)
    embed.add_field(name="Recurring", value=_recurring_text(raid_data), inline=False)
    embed.set_footer(text="Use the buttons below to edit and post the raid.")

    return embed


def _build_signup_from_raid_data(
    guild_id: int,
    raid_data: dict,
) -> tuple[bool, dict | None, str | None]:
    date_str = (raid_data.get("date") or "").strip()
    time_str = (raid_data.get("time") or "").strip()

    try:
        year, month, day = [int(x) for x in date_str.split("-")]
    except ValueError:
        return False, None, "Date must be in YYYY-MM-DD format."

    try:
        hour, minute = [int(x) for x in time_str.split(":")]
    except ValueError:
        return False, None, "Time must be in HH:MM format."

    try:
        dt = datetime(year, month, day, hour, minute, tzinfo=SWEDEN_TZ)
    except ValueError as e:
        return False, None, f"Invalid date/time: {e}"

    start_ts = int(dt.timestamp())

    signup = build_signup_payload(
        guild_id=guild_id,
        title=raid_data.get("title", "New Raid Signup"),
        description=raid_data.get("description", ""),
        leader=raid_data.get("leader", ""),
        start_ts=start_ts,
        channel_id=raid_data.get("channel_id"),
    )

    signup["is_recurring"] = bool(raid_data.get("is_recurring", False))
    signup["recurring_interval_days"] = raid_data.get("recurring_interval_days")

    return True, signup, None


class RaidTitleModal(discord.ui.Modal, title="Edit Raid Title"):
    new_title = discord.ui.TextInput(
        label="Raid Title",
        placeholder="Enter raid title",
        max_length=100,
    )

    def __init__(self, raid_data: dict):
        super().__init__()
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        self.raid_data["title"] = str(self.new_title).strip()

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidDescriptionModal(discord.ui.Modal, title="Edit Raid Description"):
    new_description = discord.ui.TextInput(
        label="Raid Description",
        placeholder="Enter raid description",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False,
    )

    def __init__(self, raid_data: dict):
        super().__init__()
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        self.raid_data["description"] = str(self.new_description).strip()

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidLeaderModal(discord.ui.Modal, title="Edit Raid Leader"):
    new_leader = discord.ui.TextInput(
        label="Raid Leader",
        placeholder="Enter raid leader",
        max_length=100,
    )

    def __init__(self, raid_data: dict):
        super().__init__()
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        self.raid_data["leader"] = str(self.new_leader).strip()

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidDateModal(discord.ui.Modal, title="Edit Raid Date"):
    new_date = discord.ui.TextInput(
        label="Raid Date",
        placeholder="YYYY-MM-DD",
        max_length=10,
    )

    def __init__(self, raid_data: dict):
        super().__init__()
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        self.raid_data["date"] = str(self.new_date).strip()

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidTimeModal(discord.ui.Modal, title="Edit Raid Time"):
    new_time = discord.ui.TextInput(
        label="Raid Time",
        placeholder="HH:MM",
        max_length=5,
    )

    def __init__(self, raid_data: dict):
        super().__init__()
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        self.raid_data["time"] = str(self.new_time).strip()

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RecurringRaidModal(discord.ui.Modal, title="Recurring Raid Settings"):
    interval_days = discord.ui.TextInput(
        label="Repeat every X days",
        placeholder="Example: 7 (leave blank to disable)",
        max_length=3,
        required=False,
    )

    def __init__(self, raid_data: dict):
        super().__init__()
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        raw = str(self.interval_days).strip()

        if not raw:
            self.raid_data["is_recurring"] = False
            self.raid_data["recurring_interval_days"] = None
        else:
            try:
                interval = int(raw)
            except ValueError:
                await interaction.response.send_message(
                    "⚠ Interval must be a whole number.",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
                return

            if interval <= 0:
                await interaction.response.send_message(
                    "⚠ Interval must be greater than 0.",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
                return

            self.raid_data["is_recurring"] = True
            self.raid_data["recurring_interval_days"] = interval

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class SaveTemplateModal(discord.ui.Modal, title="Save Raid Template"):
    template_name = discord.ui.TextInput(
        label="Template Name",
        placeholder="Example: Wednesday HC",
        max_length=50,
    )

    def __init__(self, guild_id: int, raid_data: dict):
        super().__init__()
        self.guild_id = guild_id
        self.raid_data = dict(raid_data)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        name = str(self.template_name).strip()
        ok = save_template(self.guild_id, name, self.raid_data)

        if ok:
            await interaction.response.edit_message(
                content="✅ Template saved.",
                embed=_build_preview_embed(guild, self.raid_data),
                view=RaidBuilderView(self.raid_data),
            )
            asyncio.create_task(
                delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            content=f"⚠ A template named **{name}** already exists.",
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data, existing_template_name=name),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class TemplateDateModal(discord.ui.Modal, title="Set Raid Date from Template"):
    raid_date = discord.ui.TextInput(
        label="Raid Date",
        placeholder="YYYY-MM-DD",
        max_length=10,
    )

    def __init__(self, guild_id: int, channel_id: int, template_name: str):
        super().__init__()
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.template_name = template_name

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        raid_data = build_raid_data_from_template(
            self.guild_id,
            self.channel_id,
            self.template_name,
            str(self.raid_date).strip(),
        )

        if not raid_data:
            await interaction.response.send_message(
                "⚠ Could not load that template.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            content=None,
            embed=_build_preview_embed(guild, raid_data),
            view=RaidBuilderView(raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, raid_data: dict):
        self.raid_data = dict(raid_data)

        super().__init__(
            placeholder="Select channel to post the raid in...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
            row=2,
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
        self.raid_data["channel_id"] = channel.id

        await interaction.response.edit_message(
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidTemplateSelect(discord.ui.Select):
    def __init__(self, guild_id: int, channel_id: int):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.templates = list_templates(guild_id)

        options = []
        for template in self.templates[:25]:
            options.append(
                discord.SelectOption(
                    label=template.get("name", "Unnamed Template")[:100],
                    description=template.get("title", "Raid Template")[:100],
                    value=template.get("name", ""),
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No saved templates",
                    description="Save a template first in the raid builder.",
                    value="__none__",
                )
            )

        super().__init__(
            placeholder="Select a saved template...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_name = self.values[0]

        if selected_name == "__none__":
            await interaction.response.send_message(
                "⚠ No templates are saved for this server yet.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.send_modal(
            TemplateDateModal(self.guild_id, self.channel_id, selected_name)
        )


class DeleteTemplateSelect(discord.ui.Select):
    def __init__(self, guild_id: int, channel_id: int):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.templates = list_templates(guild_id)

        options = []
        for template in self.templates[:25]:
            options.append(
                discord.SelectOption(
                    label=template.get("name", "Unnamed Template")[:100],
                    description=template.get("title", "Raid Template")[:100],
                    value=template.get("name", ""),
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No saved templates",
                    description="Nothing to delete.",
                    value="__none__",
                )
            )

        super().__init__(
            placeholder="Select a template to delete...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_name = self.values[0]

        if selected_name == "__none__":
            await interaction.response.send_message(
                "⚠ No templates are saved for this server yet.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        ok = delete_template(self.guild_id, selected_name)
        if not ok:
            await interaction.response.send_message(
                "⚠ Could not delete that template.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            content=f"✅ Deleted template **{selected_name}**.",
            embed=None,
            view=RaidTemplateView(self.guild_id, self.channel_id),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class EditTitleButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Edit Title", style=discord.ButtonStyle.secondary, row=0)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RaidTitleModal(self.raid_data))


class EditDescriptionButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Edit Description", style=discord.ButtonStyle.secondary, row=0)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RaidDescriptionModal(self.raid_data))


class EditLeaderButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Edit Leader", style=discord.ButtonStyle.secondary, row=0)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RaidLeaderModal(self.raid_data))


class EditDateButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Edit Date", style=discord.ButtonStyle.secondary, row=1)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RaidDateModal(self.raid_data))


class EditTimeButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Edit Time", style=discord.ButtonStyle.secondary, row=1)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RaidTimeModal(self.raid_data))


class RecurringRaidButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Recurring Raid", style=discord.ButtonStyle.secondary, row=1)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RecurringRaidModal(self.raid_data))


class SaveTemplateButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(
            label="Save Template",
            style=discord.ButtonStyle.primary,
            row=3,
        )
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(
            SaveTemplateModal(guild.id, self.raid_data)
        )


class OverwriteTemplateButton(discord.ui.Button):
    def __init__(self, raid_data: dict, template_name: str):
        super().__init__(
            label=f"Overwrite: {template_name[:40]}",
            style=discord.ButtonStyle.danger,
            row=3,
        )
        self.raid_data = dict(raid_data)
        self.template_name = template_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        ok = overwrite_template(guild.id, self.template_name, self.raid_data)

        if not ok:
            await interaction.response.send_message(
                "⚠ Could not overwrite template.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            content=f"✅ Template **{self.template_name}** overwritten.",
            embed=_build_preview_embed(guild, self.raid_data),
            view=RaidBuilderView(self.raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class PostRaidButton(discord.ui.Button):
    def __init__(self, raid_data: dict):
        super().__init__(label="Post Raid", style=discord.ButtonStyle.success, row=3)
        self.raid_data = dict(raid_data)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        ok, signup, error = _build_signup_from_raid_data(guild.id, self.raid_data)
        if not ok or signup is None:
            await interaction.response.send_message(
                f"⚠ {error or 'Could not build raid signup.'}",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        channel_id = self.raid_data.get("channel_id")
        target_channel = guild.get_channel(channel_id)
        if target_channel is None:
            try:
                target_channel = await guild.fetch_channel(channel_id)
            except Exception:
                target_channel = None

        if target_channel is None:
            await interaction.response.send_message(
                "⚠ Could not find the selected channel.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        class _ChannelCtx:
            def __init__(self, channel):
                self.channel = channel

            async def send(self, *args, **kwargs):
                return await self.channel.send(*args, **kwargs)

        ok = await send_signup_message(_ChannelCtx(target_channel), signup)

        if not ok:
            await interaction.response.send_message(
                "⚠ Failed to create signup message.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await interaction.response.edit_message(
            content="✅ Raid signup posted.",
            embed=None,
            view=None,
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class BackToRaidStartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.primary, row=4)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        channel = interaction.channel

        if guild is None or channel is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content="Raid setup",
            embed=None,
            view=RaidStartView(guild.id, channel.id),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class CancelRaidBuilderButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger, row=4)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Raid creation cancelled.",
            embed=None,
            view=None,
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class CreateNewRaidButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(label="Create New Raid", style=discord.ButtonStyle.success, row=0)
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        raid_data = _default_raid_data(self.guild_id, self.channel_id)

        await interaction.response.edit_message(
            content=None,
            embed=_build_preview_embed(guild, raid_data),
            view=RaidBuilderView(raid_data),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class UseTemplateButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(label="Use Template", style=discord.ButtonStyle.secondary, row=0)
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠ This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content="Select a saved template:",
            embed=None,
            view=RaidTemplateView(self.guild_id, self.channel_id),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class DeleteTemplateButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(
            label="Delete Template",
            style=discord.ButtonStyle.danger,
            row=1,
        )
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select a template to delete:",
            embed=None,
            view=DeleteTemplateView(self.guild_id, self.channel_id),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class CancelRaidStartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger, row=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Raid setup cancelled.",
            embed=None,
            view=None,
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class BackFromTemplateButton(discord.ui.Button):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(label="Back", style=discord.ButtonStyle.primary, row=1)
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Raid setup",
            embed=None,
            view=RaidStartView(self.guild_id, self.channel_id),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidStartView(discord.ui.View):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(timeout=120)
        self.add_item(CreateNewRaidButton(guild_id, channel_id))
        self.add_item(UseTemplateButton(guild_id, channel_id))
        self.add_item(CancelRaidStartButton())


class DeleteTemplateView(discord.ui.View):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(timeout=120)
        self.add_item(DeleteTemplateSelect(guild_id, channel_id))
        self.add_item(BackFromTemplateButton(guild_id, channel_id))


class RaidTemplateView(discord.ui.View):
    def __init__(self, guild_id: int, channel_id: int):
        super().__init__(timeout=120)
        self.add_item(RaidTemplateSelect(guild_id, channel_id))
        self.add_item(DeleteTemplateButton(guild_id, channel_id))
        self.add_item(BackFromTemplateButton(guild_id, channel_id))


class RaidBuilderView(discord.ui.View):
    def __init__(self, raid_data: dict, existing_template_name: str | None = None):
        super().__init__(timeout=120)
        self.add_item(EditTitleButton(raid_data))
        self.add_item(EditDescriptionButton(raid_data))
        self.add_item(EditLeaderButton(raid_data))
        self.add_item(EditDateButton(raid_data))
        self.add_item(EditTimeButton(raid_data))
        self.add_item(RecurringRaidButton(raid_data))
        self.add_item(RaidChannelSelect(raid_data))
        self.add_item(SaveTemplateButton(raid_data))

        if existing_template_name:
            self.add_item(OverwriteTemplateButton(raid_data, existing_template_name))

        self.add_item(PostRaidButton(raid_data))
        self.add_item(BackToRaidStartButton())
        self.add_item(CancelRaidBuilderButton())