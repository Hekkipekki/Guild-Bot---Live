import asyncio
import discord

from services.raid_control_service import (
    set_player_status,
    remove_player_signup,
)
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
                await interaction.response.send_message(
                    "Select a player first.",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
                return

            if not view.selected_action:
                await interaction.response.send_message(
                    "Select an action first.",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
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
                await interaction.response.send_message(
                    "Could not update that player.",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
                return

            await refresh_signup_message_by_id(interaction.channel, int(view.raid_id))

            await interaction.response.send_message(
                f"Player {action_text}.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            if interaction.response.is_done():
                msg = await interaction.followup.send(
                    f"Raid control failed: {type(e).__name__}: {e}",
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(
                    delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
            else:
                await interaction.response.send_message(
                    f"Raid control failed: {type(e).__name__}: {e}",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
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
            if interaction.response.is_done():
                msg = await interaction.followup.send(
                    f"Change Spec failed: {type(e).__name__}: {e}",
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(
                    delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
            else:
                await interaction.response.send_message(
                    f"Change Spec failed: {type(e).__name__}: {e}",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
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
            await refresh_signup_message_by_id(interaction.channel, int(view.raid_id))

            await interaction.response.send_message(
                "Raid refreshed.",
                ephemeral=True,
            )
            asyncio.create_task(
                delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            if interaction.response.is_done():
                msg = await interaction.followup.send(
                    f"Failed to refresh raid: {type(e).__name__}: {e}",
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(
                    delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
            else:
                await interaction.response.send_message(
                    f"Failed to refresh raid: {type(e).__name__}: {e}",
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
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