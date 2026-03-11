import asyncio
import discord
import config

from data.character_store import add_character
from logic.signup_manager import set_user_spec, refresh_signup_message_by_id
from views.signup_options import (
    SignupOptionsView,
    build_signup_options_embed,
    get_signup_entry,
    delete_ephemeral_after,
)
from views.signup.shared import (
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
        asyncio.create_task(delete_ephemeral_after(interaction, 30))


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

        added = add_character(interaction.user.id, char)

        if not added:
            from views.signup.character_select_view import CharacterView

            await interaction.response.edit_message(
                content=f"⚠ **{char['name']}** is already saved.",
                view=CharacterView(
                    interaction.user.id,
                    self.parent_message_id,
                    filter_class=self.filter_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        set_user_spec(
            raid_id=self.parent_message_id,
            user_id=str(interaction.user.id),
            selected_class=selected_class,
            selected_spec=selected_spec,
            role=role,
            character_name=char["name"],
            auto_sign=True,
        )

        try:
            await refresh_signup_message_by_id(
                interaction.channel,
                self.parent_message_id,
            )
        except discord.NotFound:
            await interaction.response.send_message(
                "⚠ Could not find the signup message.",
                ephemeral=True,
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return
        except Exception as e:
            await interaction.response.send_message(
                f"⚠ Character creation failed: {e}",
                ephemeral=True,
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        entry = get_signup_entry(self.parent_message_id, str(interaction.user.id))
        if not entry:
            await interaction.response.send_message(
                "⚠ Saved and signed, but could not load signup options.",
                ephemeral=True,
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(entry),
            view=SignupOptionsView(self.parent_message_id, interaction.user.id),
        )
        asyncio.create_task(delete_ephemeral_after(interaction, 45))


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