import asyncio
import discord
import config

from services.character.character_service import add_user_character
from services.signup.signup_service import set_user_spec
from services.signup.signup_ui_service import (
    refresh_and_show_signup_options_from_channel,
)
from utils.ui_timing import (
    CHARACTER_MENU_AUTO_DELETE_SECONDS,
    ERROR_MESSAGE_AUTO_DELETE_SECONDS,
)
from utils.discord_utils import delete_interaction_after
from views.signup.main.shared import (
    parse_spec_emoji,
    parse_class_emoji,
    BackToCharacterMenuButton,
)


def prettify_character_name(spec: str, wow_class: str) -> str:
    pretty_spec = {
        "ProtectionWarrior": "Protection",
        "HolyPaladin": "Holy",
        "ProtectionPaladin": "Protection",
        "RestorationDruid": "Restoration",
        "HolyPriest": "Holy",
        "RestorationShaman": "Restoration",
        "FrostDK": "Frost",
    }.get(spec, spec)

    return f"{pretty_spec} {wow_class}"


class AddCharacterClassSelect(discord.ui.Select):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        self.user_id = user_id
        self.parent_message_id = parent_message_id
        self.filter_class = filter_class

        options = []
        for class_name in config.CLASSES:
            options.append(
                discord.SelectOption(
                    label=class_name,
                    value=class_name,
                    emoji=parse_class_emoji(class_name),
                )
            )

        super().__init__(
            placeholder="Select class to add",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_class = self.values[0]

        await interaction.response.edit_message(
            content=f"Choose a spec for **{selected_class}**:",
            view=AddCharacterSpecView(
                user_id=self.user_id,
                parent_message_id=self.parent_message_id,
                selected_class=selected_class,
                filter_class=self.filter_class,
            ),
        )
        asyncio.create_task(
            delete_interaction_after(interaction, CHARACTER_MENU_AUTO_DELETE_SECONDS)
        )


class AddCharacterSpecSelect(discord.ui.Select):
    def __init__(
        self,
        user_id: int,
        parent_message_id: int,
        selected_class: str,
        filter_class: str | None = None,
    ):
        self.user_id = user_id
        self.parent_message_id = parent_message_id
        self.selected_class = selected_class
        self.filter_class = filter_class

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
        selected_spec = self.values[0]
        selected_class = self.selected_class
        role = config.CLASS_SPECS[selected_class][selected_spec]

        char = {
            "name": prettify_character_name(selected_spec, selected_class),
            "class": selected_class,
            "spec": selected_spec,
            "role": role,
        }

        added = add_user_character(interaction.user.id, char)

        if not added:
            from views.signup.character.character_select_view import CharacterView

            await interaction.response.edit_message(
                content=f"⚠ **{char['name']}** is already saved.",
                view=CharacterView(
                    interaction.user.id,
                    self.parent_message_id,
                    filter_class=self.filter_class,
                ),
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        ok = set_user_spec(
            raid_id=self.parent_message_id,
            user_id=str(interaction.user.id),
            selected_class=selected_class,
            selected_spec=selected_spec,
            role=role,
            character_name=char["name"],
            auto_sign=True,
        )

        if not ok:
            await interaction.response.edit_message(
                content="⚠ Raid signup no longer exists.",
                view=None,
            )
            asyncio.create_task(
                delete_interaction_after(interaction, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )
            return

        await refresh_and_show_signup_options_from_channel(
            interaction,
            self.parent_message_id,
            interaction.user.id,
        )


class AddCharacterClassView(discord.ui.View):
    def __init__(self, user_id: int, parent_message_id: int, preselected_class: str | None = None):
        super().__init__(timeout=60)

        if preselected_class:
            self.add_item(
                AddCharacterSpecSelect(
                    user_id=user_id,
                    parent_message_id=parent_message_id,
                    selected_class=preselected_class,
                    filter_class=preselected_class,
                )
            )
        else:
            self.add_item(
                AddCharacterClassSelect(
                    user_id,
                    parent_message_id,
                )
            )

        self.add_item(
            BackToCharacterMenuButton(
                user_id,
                parent_message_id,
                filter_class=preselected_class,
            )
        )


class AddCharacterSpecView(discord.ui.View):
    def __init__(
        self,
        user_id: int,
        parent_message_id: int,
        selected_class: str,
        filter_class: str | None = None,
    ):
        super().__init__(timeout=60)
        self.add_item(
            AddCharacterSpecSelect(
                user_id,
                parent_message_id,
                selected_class,
                filter_class=filter_class,
            )
        )
        self.add_item(
            BackToCharacterMenuButton(
                user_id,
                parent_message_id,
                filter_class=filter_class,
            )
        )