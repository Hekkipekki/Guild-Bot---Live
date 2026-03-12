import asyncio
import discord
import config

from services.raid_control_service import (
    get_players,
    get_valid_specs_for_player,
    change_player_spec,
)
from services.signup_refresh_service import refresh_signup_message_by_id
from views.signup_options.helpers import (
    delete_ephemeral_after,
    delete_followup_message_after,
)
from utils.ui_timing import (
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
    RAID_CONTROL_AUTO_DELETE_SECONDS,
)


async def _send_spec_error(
    interaction: discord.Interaction,
    message: str,
) -> None:
    if interaction.response.is_done():
        msg = await interaction.followup.send(
            message,
            ephemeral=True,
            wait=True,
        )
        asyncio.create_task(
            delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True,
        )
        asyncio.create_task(
            delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
        )


class RaidControlSpecPlayerSelect(discord.ui.Select):
    def __init__(self, raid_id: str):
        self.raid_id = raid_id

        players = get_players(raid_id)
        options = []

        for player in players[:25]:
            name = player.get("name") or "Unknown"
            wow_class = player.get("class") or "Unknown"
            spec = player.get("spec") or "Unknown"
            status = player.get("status") or "Unknown"

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=str(player["user_id"]),
                    description=f"{wow_class} • {spec} • {status}"[:100],
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No players found",
                    value="__none__",
                    description="There are no signups to manage.",
                )
            )

        super().__init__(
            placeholder="Select player...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        if selected_value == "__none__":
            self.view.selected_user_id = None
            self.view.selected_spec = None
            self.view.rebuild_spec_select()
            await interaction.response.edit_message(
                content="Change a player's spec for this raid only.",
                view=self.view,
            )
            return

        self.view.selected_user_id = selected_value
        self.view.selected_spec = None
        self.view.rebuild_spec_select()

        await interaction.response.edit_message(
            content="Change a player's spec for this raid only.",
            view=self.view,
        )


class RaidControlSpecSelect(discord.ui.Select):
    def __init__(self, raid_id: str, user_id: str | None):
        self.raid_id = raid_id
        self.user_id = user_id

        options = []

        if user_id:
            valid_specs = get_valid_specs_for_player(raid_id, user_id)

            for item in valid_specs:
                spec_name = item["spec"]
                role_name = item["role"]
                emoji = None

                raw = config.SPEC_EMOJIS.get(spec_name)
                if raw:
                    try:
                        emoji = discord.PartialEmoji.from_str(raw)
                    except Exception:
                        emoji = None

                options.append(
                    discord.SelectOption(
                        label=spec_name[:100],
                        value=spec_name,
                        description=f"Role: {role_name}"[:100],
                        emoji=emoji,
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(
                    label="Select a player first",
                    value="__none__",
                    description="Spec choices appear after player selection.",
                )
            )

        super().__init__(
            placeholder="Select spec...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        if selected_value == "__none__":
            self.view.selected_spec = None
            await interaction.response.defer()
            return

        self.view.selected_spec = selected_value
        await interaction.response.defer()


class ApplySpecChangeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Apply Spec",
            style=discord.ButtonStyle.primary,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if not view.selected_user_id:
            await _send_spec_error(interaction, "Select a player first.")
            return

        if not view.selected_spec:
            await _send_spec_error(interaction, "Select a spec first.")
            return

        ok = change_player_spec(
            view.raid_id,
            view.selected_user_id,
            view.selected_spec,
        )

        if not ok:
            await _send_spec_error(
                interaction,
                "Could not change that player's spec. The raid or signup may no longer exist.",
            )
            return

        try:
            refreshed = await refresh_signup_message_by_id(interaction.channel, int(view.raid_id))
            if not refreshed:
                await _send_spec_error(
                    interaction,
                    "Player spec updated, but the raid signup no longer exists.",
                )
                return

        except Exception as e:
            await _send_spec_error(
                interaction,
                f"Spec updated, but failed to refresh raid: {e}",
            )
            return

        await interaction.response.send_message(
            f"Player spec changed to {view.selected_spec}.",
            ephemeral=True,
        )
        asyncio.create_task(
            delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class RaidControlSpecView(discord.ui.View):
    def __init__(self, raid_id: str):
        super().__init__(timeout=120)
        self.raid_id = raid_id
        self.selected_user_id = None
        self.selected_spec = None

        self.player_select = RaidControlSpecPlayerSelect(raid_id)
        self.spec_select = RaidControlSpecSelect(raid_id, None)

        self.add_item(self.player_select)
        self.add_item(self.spec_select)
        self.add_item(ApplySpecChangeButton())

    def rebuild_spec_select(self):
        if self.spec_select in self.children:
            self.remove_item(self.spec_select)

        self.spec_select = RaidControlSpecSelect(self.raid_id, self.selected_user_id)
        self.add_item(self.spec_select)