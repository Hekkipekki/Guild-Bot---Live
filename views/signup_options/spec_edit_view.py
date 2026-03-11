import asyncio
import discord
import config

from services.character_service import update_character_spec
from services.signup_service import update_user_spec
from services.signup_ui_service import (
    refresh_and_show_signup_options_from_channel,
)
from .helpers import get_signup_entry, parse_spec_emoji, delete_ephemeral_after


class EditSpecSelect(discord.ui.Select):
    def __init__(self, raid_id: int, user_id: int, selected_class: str):
        self.raid_id = raid_id
        self.user_id = user_id
        self.selected_class = selected_class

        options = []
        for spec, role in config.CLASS_SPECS[selected_class].items():
            options.append(
                discord.SelectOption(
                    label=spec,
                    value=spec,
                    description=f"Role: {role}",
                    emoji=parse_spec_emoji(spec),
                )
            )

        super().__init__(
            placeholder=f"Select spec for {selected_class}",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        entry = get_signup_entry(self.raid_id, str(self.user_id))
        if not entry:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        selected_spec = self.values[0]
        role = config.CLASS_SPECS[self.selected_class][selected_spec]

        ok = update_user_spec(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
            selected_class=self.selected_class,
            selected_spec=selected_spec,
            role=role,
        )

        if not ok:
            await interaction.response.send_message("Could not update spec.", ephemeral=True)
            return

        update_character_spec(
            self.user_id,
            self.selected_class,
            selected_spec,
            role,
        )

        await refresh_and_show_signup_options_from_channel(
            interaction,
            self.raid_id,
            self.user_id,
            delete_after=45,
        )


class EditSpecView(discord.ui.View):
    def __init__(self, raid_id: int, user_id: int, selected_class: str):
        super().__init__(timeout=60)
        self.add_item(EditSpecSelect(raid_id, user_id, selected_class))