import asyncio
import discord
import config

from data.character_store import (
    get_user_characters,
    add_character,
    remove_character,
)
from logic.signup_manager import set_user_spec, refresh_signup_message_by_id
from views.signup_options import (
    SignupOptionsView,
    build_signup_options_embed,
    get_signup_entry,
    delete_ephemeral_after,
)


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

        remove_character(self.user_id, real_index)

        await interaction.response.edit_message(
            content=f"🗑 Removed **{char_to_remove['name']}**",
            view=ManageCharactersView(
                self.user_id,
                self.parent_message_id,
                filter_class=self.filter_class,
            ),
        )
        asyncio.create_task(delete_ephemeral_after(interaction, 15))


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
        await interaction.response.edit_message(
            content="Select your saved character:",
            view=CharacterView(
                self.user_id,
                self.parent_message_id,
                filter_class=self.filter_class,
            ),
        )
        asyncio.create_task(delete_ephemeral_after(interaction, 30))


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


class ManageCharactersView(discord.ui.View):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        super().__init__(timeout=60)
        self.add_item(RemoveCharacterSelect(user_id, parent_message_id, filter_class=filter_class))
        self.add_item(BackToCharacterMenuButton(user_id, parent_message_id, filter_class=filter_class))


class CharacterView(discord.ui.View):
    def __init__(self, user_id: int, parent_message_id: int, filter_class: str | None = None):
        super().__init__(timeout=60)
        self.add_item(CharacterSelect(user_id, parent_message_id, filter_class=filter_class))


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