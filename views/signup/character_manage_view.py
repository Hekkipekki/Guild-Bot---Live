import asyncio
import discord

from services.character_service import get_user_characters, remove_user_character
from views.signup_options import delete_ephemeral_after
from views.signup.shared import parse_spec_emoji, BackToCharacterMenuButton


class RemoveCharacterSelect(discord.ui.Select):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        self.user_id = user_id
        self.parent_message_id = parent_message_id
        self.filter_class = filter_class

        characters = get_user_characters(user_id)

        if filter_class:
            characters = [c for c in characters if c["class"] == filter_class]

        self.filtered_characters = characters
        options = []

        for i, char in enumerate(characters):
            options.append(
                discord.SelectOption(
                    label=char["name"],
                    description=f"{char['class']} • {char['spec']}",
                    value=str(i),
                    emoji=parse_spec_emoji(char["spec"]),
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No saved characters",
                    value="none",
                    emoji="📭",
                )
            )

        super().__init__(
            placeholder="Select character to remove",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]

        if value == "none":
            await interaction.response.defer()
            asyncio.create_task(delete_ephemeral_after(interaction, 5))
            return

        if int(value) >= len(self.filtered_characters):
            await interaction.response.edit_message(
                content="⚠ Character not found.",
                view=ManageCharactersView(
                    self.user_id,
                    self.parent_message_id,
                    filter_class=self.filter_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        char_to_remove = self.filtered_characters[int(value)]

        all_characters = get_user_characters(self.user_id)
        real_index = next(
            (i for i, c in enumerate(all_characters) if c == char_to_remove),
            None,
        )

        if real_index is None:
            await interaction.response.edit_message(
                content="⚠ Character not found.",
                view=ManageCharactersView(
                    self.user_id,
                    self.parent_message_id,
                    filter_class=self.filter_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        remove_user_character(self.user_id, real_index)

        await interaction.response.edit_message(
            content=f"🗑 Removed **{char_to_remove['name']}**",
            view=ManageCharactersView(
                self.user_id,
                self.parent_message_id,
                filter_class=self.filter_class,
            ),
        )
        asyncio.create_task(delete_ephemeral_after(interaction, 15))


class ManageCharactersView(discord.ui.View):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        super().__init__(timeout=60)
        self.add_item(RemoveCharacterSelect(user_id, parent_message_id, filter_class=filter_class))
        self.add_item(BackToCharacterMenuButton(user_id, parent_message_id, filter_class=filter_class))