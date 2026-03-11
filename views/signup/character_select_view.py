import asyncio
import discord

from data.character_store import get_user_characters
from logic.signup_manager import set_user_spec, refresh_signup_message_by_id
from views.signup_options import (
    SignupOptionsView,
    build_signup_options_embed,
    get_signup_entry,
    delete_ephemeral_after,
)
from views.signup.shared import parse_spec_emoji
from views.signup.character_add_view import AddCharacterClassView
from views.signup.character_manage_view import ManageCharactersView


class CharacterSelect(discord.ui.Select):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        self.parent_message_id = parent_message_id
        self.user_id = user_id
        self.filter_class = filter_class

        characters = get_user_characters(user_id)

        if filter_class:
            characters = [c for c in characters if c["class"] == filter_class]

        self.filtered_characters = characters
        options = []

        for i, char in enumerate(characters):
            spec = char["spec"]
            emoji = parse_spec_emoji(spec)

            options.append(
                discord.SelectOption(
                    label=char["name"],
                    description=f"{char['class']} • {char['spec']}",
                    value=str(i),
                    emoji=emoji,
                )
            )

        options.append(
            discord.SelectOption(
                label="Add Character",
                value="add",
                emoji="➕",
            )
        )

        options.append(
            discord.SelectOption(
                label="Manage Characters",
                value="manage",
                emoji="⚙️",
            )
        )

        placeholder = "Select your saved character"
        if filter_class:
            placeholder = f"Select your {filter_class} character"

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]

        if value == "add":
            await interaction.response.edit_message(
                content="Choose a class to save as a character:",
                view=AddCharacterClassView(
                    interaction.user.id,
                    self.parent_message_id,
                    preselected_class=self.filter_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 30))
            return

        if value == "manage":
            await interaction.response.edit_message(
                content="Manage your saved characters:",
                view=ManageCharactersView(
                    interaction.user.id,
                    self.parent_message_id,
                    filter_class=self.filter_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 30))
            return

        if int(value) >= len(self.filtered_characters):
            await interaction.response.edit_message(
                content="⚠ Character not found.",
                view=CharacterView(
                    interaction.user.id,
                    self.parent_message_id,
                    filter_class=self.filter_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        char = self.filtered_characters[int(value)]

        selected_class = char["class"]
        selected_spec = char["spec"]
        role = char["role"]

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
                f"⚠ Character selection failed: {e}",
                ephemeral=True,
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        entry = get_signup_entry(self.parent_message_id, str(interaction.user.id))
        if not entry:
            await interaction.response.send_message(
                "⚠ Signed up, but could not load signup options.",
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


class CharacterView(discord.ui.View):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        super().__init__(timeout=60)
        self.add_item(CharacterSelect(user_id, parent_message_id, filter_class=filter_class))