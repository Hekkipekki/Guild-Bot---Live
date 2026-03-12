import asyncio
import discord

from services.comp_message_service import post_comp_message
from views.signup.comp_bench_view import CompBenchView
from views.signup_options.helpers import (
    delete_ephemeral_after,
    delete_followup_message_after,
)
from utils.ui_timing import (
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
    RAID_CONTROL_AUTO_DELETE_SECONDS,
)


async def _send_choice_error(interaction: discord.Interaction, message: str) -> None:
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


class BuildCompOptionButton(discord.ui.Button):
    def __init__(self, label_text: str, comp_data: dict, row: int = 0):
        super().__init__(
            label=f"Build {label_text}",
            style=discord.ButtonStyle.success,
            row=row,
        )
        self.comp_data = comp_data

    async def callback(self, interaction: discord.Interaction):
        try:
            comp_data = self.comp_data
            candidates = comp_data.get("bench_choice_candidates", [])

            # Multiple valid candidates -> let raid leader choose manually
            if len(candidates) > 1:
                await interaction.response.send_message(
                    "Select which player should be benched:",
                    view=CompBenchView(comp_data, candidates),
                    ephemeral=True,
                )
                asyncio.create_task(
                    delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
                )
                return

            # No real bench decision needed (or only one unavoidable candidate)
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
                "Comp posted.",
                ephemeral=True,
                wait=True,
            )
            asyncio.create_task(
                delete_followup_message_after(msg, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )

        except Exception as e:
            await _send_choice_error(
                interaction,
                f"Comp build failed: {type(e).__name__}: {e}",
            )


class CancelCompChoiceButton(discord.ui.Button):
    def __init__(self, row: int = 1):
        super().__init__(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Comp build cancelled.",
            view=None,
        )
        asyncio.create_task(
            delete_ephemeral_after(interaction, RAID_CONTROL_AUTO_DELETE_SECONDS)
        )


class CompChoiceView(discord.ui.View):
    def __init__(self, option_226: dict, option_235: dict):
        super().__init__(timeout=120)
        self.add_item(BuildCompOptionButton("2/2/6", option_226, row=0))
        self.add_item(BuildCompOptionButton("2/3/5", option_235, row=0))
        self.add_item(CancelCompChoiceButton(row=1))