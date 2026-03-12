import asyncio
import discord

from services.roster_comp_service import analyze_roster_comp
from services.comp_message_service import post_comp_message
from views.signup.comp_choice_view import CompChoiceView

from services.raid_control_service import (
    set_player_status,
    remove_player_signup,
)
from services.comp_message_service import post_comp_message
from services.signup_refresh_service import refresh_signup_message_by_id
from views.signup.raid_control_components import (
    RaidControlPlayerSelect,
    RaidControlActionSelect,
)
from views.signup_options.helpers import (
    delete_ephemeral_after,
    delete_followup_message_after,
)
from utils.ui_timing import (
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
    RAID_CONTROL_AUTO_DELETE_SECONDS,
)


async def _send_raid_control_error(
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


class ApplyRaidControlButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Apply",
            style=discord.ButtonStyle.primary,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            view = self.view

            if not view.selected_user_id:
                await _send_raid_control_error(interaction, "Select a player first.")
                return

            if not view.selected_action:
                await _send_raid_control_error(interaction, "Select an action first.")
                return

            if view.selected_action == "remove":
                ok = remove_player_signup(view.raid_id, view.selected_user_id)
                action_text = "removed"
            else:
                ok = set_player_status(
                    view.raid_id,
                    view.selected_user_id,
                    view.selected_action,
                )
                action_text = f"set to {view.selected_action}"

            if not ok:
                await _send_raid_control_error(
                    interaction,
                    "Could not update that player. The raid or signup may no longer exist.",
                )
                return

            refreshed = await refresh_signup_message_by_id(interaction.channel, int(view.raid_id))
            if not refreshed:
                await _send_raid_control_error(
                    interaction,
                    "Player updated, but the raid signup no longer exists.",
                )
                return

            await interaction.response.send_message(
                f"Player {action_text}.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            await _send_raid_control_error(
                interaction,
                f"Raid control failed: {type(e).__name__}: {e}",
            )


class ChangeSpecRaidControlButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Change Spec",
            style=discord.ButtonStyle.secondary,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            from views.signup.raid_control_spec_view import RaidControlSpecView

            view = self.view
            spec_view = RaidControlSpecView(view.raid_id)

            await interaction.response.send_message(
                "Change a player's spec for this raid only.",
                view=spec_view,
                ephemeral=True,
            )
            asyncio.create_task(
                delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            await _send_raid_control_error(
                interaction,
                f"Change Spec failed: {type(e).__name__}: {e}",
            )


class RefreshRaidControlButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Refresh Raid",
            style=discord.ButtonStyle.secondary,
            row=3,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            view = self.view
            refreshed = await refresh_signup_message_by_id(interaction.channel, int(view.raid_id))

            if not refreshed:
                await _send_raid_control_error(
                    interaction,
                    "⚠ Raid signup no longer exists.",
                )
                return

            await interaction.response.send_message(
                "Raid refreshed.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            await _send_raid_control_error(
                interaction,
                f"Failed to refresh raid: {type(e).__name__}: {e}",
            )


class RaidControlView(discord.ui.View):
    def __init__(self, raid_id: str):
        super().__init__(timeout=120)
        self.raid_id = raid_id
        self.selected_user_id = None
        self.selected_action = None

        self.add_item(RaidControlPlayerSelect(raid_id))
        self.add_item(RaidControlActionSelect())
        self.add_item(ApplyRaidControlButton())
        self.add_item(ChangeSpecRaidControlButton())
        self.add_item(RefreshRaidControlButton())
        self.add_item(BuildCompButton())

class BuildCompButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Build Comp",
            style=discord.ButtonStyle.success,
            row=3,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            view = self.view

            state, payload = analyze_roster_comp(view.raid_id)

            if state == "error" or not payload:
                await _send_raid_control_error(
                    interaction,
                    "Could not build comp. The raid may no longer exist.",
                )
                return

            if state == "ambiguous":
                await interaction.response.send_message(
                    "Two valid 10-man comps were found. Choose which one to post.",
                    view=CompChoiceView(
                        payload["option_226"],
                        payload["option_235"],
                    ),
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
                )
                return

            comp_data = payload["comp_data"]

            await interaction.response.defer(ephemeral=True)

            ok, message = await post_comp_message(
                interaction.channel,
                comp_data,
            )

            if not ok:
                msg = await interaction.followup.send(
                    message,
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(
                    delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
                return

            msg = await interaction.followup.send(
                "Comp message posted.",
                ephemeral=True,
                wait=True,
            )
            asyncio.create_task(
                delete_followup_message_after(msg, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            await _send_raid_control_error(
                interaction,
                f"Build Comp failed: {type(e).__name__}: {e}",
            )