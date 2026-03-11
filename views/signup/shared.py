import asyncio
import discord
import config

from views.signup_options import delete_ephemeral_after


def parse_spec_emoji(spec_name: str):
    raw = config.SPEC_EMOJIS.get(spec_name)
    if not raw:
        return None

    try:
        return discord.PartialEmoji.from_str(raw)
    except Exception:
        return None


def parse_class_emoji(class_name: str):
    raw = getattr(config, "CLASS_EMOJIS", {}).get(class_name)
    if not raw:
        return None

    try:
        return discord.PartialEmoji.from_str(raw)
    except Exception:
        return None


class BackToCharacterMenuButton(discord.ui.Button):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.secondary,
            emoji="↩️",
        )
        self.user_id = user_id
        self.parent_message_id = parent_message_id
        self.filter_class = filter_class

    async def callback(self, interaction: discord.Interaction):
        from views.signup.character_select_view import CharacterView

        await interaction.response.edit_message(
            content="Select your saved character:",
            view=CharacterView(
                self.user_id,
                self.parent_message_id,
                filter_class=self.filter_class,
            ),
        )
        asyncio.create_task(delete_ephemeral_after(interaction, 30))