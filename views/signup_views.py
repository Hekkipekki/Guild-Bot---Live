import asyncio
import discord
import config

from logic.signup_manager import (
    set_user_status,
    refresh_signup_message,
)
from views.signup_options import (
    SignupOptionsView,
    build_signup_options_embed,
    get_signup_entry,
    delete_ephemeral_after,
    delete_followup_message_after,
)


def get_button_emoji(name: str):
    emoji_map = getattr(config, "BUTTON_EMOJIS", {})
    value = emoji_map.get(name)

    if not value:
        return None

    try:
        return discord.PartialEmoji.from_str(value)
    except Exception:
        return None


class SignupStatusButton(discord.ui.Button):
    def __init__(
        self,
        *,
        raid_id: str,
        status: str,
        label: str,
        emoji_name: str,
        style: discord.ButtonStyle,
        row: int,
    ):
        super().__init__(
            label=label,
            emoji=get_button_emoji(emoji_name),
            style=style,
            custom_id=f"signup:{status}:{raid_id}",
            row=row,
        )
        self.raid_id = raid_id
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        ok, error_message = set_user_status(
            raid_id=int(self.raid_id),
            user_id=str(interaction.user.id),
            status=self.status,
        )

        if not ok:
            await interaction.response.send_message(error_message, ephemeral=True)
            asyncio.create_task(delete_ephemeral_after(interaction, 10))
            return

        await interaction.response.defer()
        await refresh_signup_message(interaction, int(self.raid_id))


class ClassDropdown(discord.ui.Select):
    def __init__(self, raid_id: str):
        self.raid_id = raid_id

        options = []
        for cls in config.CLASSES:
            raw_emoji = config.CLASS_EMOJIS.get(cls)
            emoji = None

            if raw_emoji:
                try:
                    emoji = discord.PartialEmoji.from_str(raw_emoji)
                except Exception:
                    emoji = None

            options.append(
                discord.SelectOption(
                    label=cls,
                    value=cls,
                    emoji=emoji,
                )
            )

        super().__init__(
            placeholder="Select your class...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"signup:classdropdown:{raid_id}",
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            selected_class = self.values[0]

            from data.character_store import get_user_characters
            from logic.signup_manager import set_user_spec
            from views.character_select import AddCharacterSpecView

            characters = get_user_characters(interaction.user.id)

            saved_char = None
            for char in characters:
                if char.get("class") == selected_class:
                    saved_char = char
                    break

            # Saved character exists -> auto sign
            if saved_char:
                set_user_spec(
                    raid_id=int(self.raid_id),
                    user_id=str(interaction.user.id),
                    selected_class=saved_char["class"],
                    selected_spec=saved_char["spec"],
                    role=saved_char["role"],
                    character_name=saved_char["name"],
                    auto_sign=True,
                )

                await interaction.response.defer()
                await refresh_signup_message(interaction, int(self.raid_id))

                entry = get_signup_entry(int(self.raid_id), str(interaction.user.id))
                if not entry:
                    msg = await interaction.followup.send(
                        "⚠ Signed up, but could not load signup options.",
                        ephemeral=True,
                        wait=True,
                    )
                    asyncio.create_task(delete_followup_message_after(msg, 10))
                    return

                msg = await interaction.followup.send(
                    embed=build_signup_options_embed(entry),
                    view=SignupOptionsView(int(self.raid_id), interaction.user.id),
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(delete_followup_message_after(msg, 45))
                return

            # No saved character -> open spec picker directly
            await interaction.response.send_message(
                f"Select your specialization for **{selected_class}**:",
                ephemeral=True,
                view=AddCharacterSpecView(
                    user_id=interaction.user.id,
                    parent_message_id=int(self.raid_id),
                    selected_class=selected_class,
                    filter_class=selected_class,
                ),
            )
            asyncio.create_task(delete_ephemeral_after(interaction, 30))

        except Exception as e:
            if interaction.response.is_done():
                msg = await interaction.followup.send(
                    f"⚠ Class select failed: `{type(e).__name__}: {e}`",
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(delete_followup_message_after(msg, 10))
            else:
                await interaction.response.send_message(
                    f"⚠ Class select failed: `{type(e).__name__}: {e}`",
                    ephemeral=True,
                )
                asyncio.create_task(delete_ephemeral_after(interaction, 10))


class SignupView(discord.ui.View):
    def __init__(self, raid_id: str):
        super().__init__(timeout=None)
        self.raid_id = raid_id

        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="sign",
                label="Sign",
                emoji_name="sign",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="late",
                label="Late",
                emoji_name="late",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="bench",
                label="Bench",
                emoji_name="bench",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="tentative",
                label="Tentative",
                emoji_name="tentative",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="absence",
                label="Absence",
                emoji_name="absence",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )

        self.add_item(ClassDropdown(raid_id))