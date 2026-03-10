import asyncio
import discord
import config

from data.signup_store import load_signups
from data.character_store import (
    update_character_name_by_class,
    update_character_spec_by_class,
)
from logic.signup_manager import (
    remove_user_signup,
    refresh_signup_message_by_id,
    update_user_name,
    update_user_note,
    update_user_spec,
)


AUTO_DELETE_SECONDS = 45


async def delete_ephemeral_after(interaction: discord.Interaction, seconds: int = AUTO_DELETE_SECONDS):
    """
    Deletes the ORIGINAL interaction response.
    Only use this when the original response is the ephemeral message itself.
    """
    try:
        await asyncio.sleep(seconds)
        await interaction.delete_original_response()
    except Exception:
        pass


async def delete_followup_message_after(message, seconds: int = AUTO_DELETE_SECONDS):
    """
    Deletes a FOLLOWUP ephemeral/webhook message returned by interaction.followup.send(..., wait=True).
    Safe for temporary ephemeral followups.
    """
    try:
        await asyncio.sleep(seconds)
        await message.delete()
    except Exception:
        pass


def get_signup_entry(raid_id: int, user_id: str) -> dict | None:
    data = load_signups()
    raid = data.get(str(raid_id), {})
    users = raid.get("users", {})
    return users.get(str(user_id))


def parse_spec_emoji(spec_name: str):
    raw = config.SPEC_EMOJIS.get(spec_name)
    if not raw:
        return None

    try:
        return discord.PartialEmoji.from_str(raw)
    except Exception:
        return None


def build_signup_options_embed(entry: dict) -> discord.Embed:
    spec_name = entry.get("spec", "-")
    class_name = entry.get("class", "-")
    char_name = entry.get("name", "-")
    note = entry.get("note", "")
    spec_emoji = config.SPEC_EMOJIS.get(spec_name, "")

    embed = discord.Embed(
        title="✅ You have been signed up to the event!",
        description="## ⚙ Sign-Up Options",
        color=discord.Color.purple(),
    )

    embed.add_field(name="Name", value=char_name or "-", inline=False)
    embed.add_field(name="Class", value=class_name or "-", inline=True)
    embed.add_field(
        name="Spec",
        value=f"{spec_emoji} {spec_name}".strip() or "-",
        inline=True,
    )
    embed.add_field(name="Note", value=note or "-", inline=False)
    embed.set_footer(text=f"This panel closes automatically after {AUTO_DELETE_SECONDS} seconds.")

    return embed


class EditNameModal(discord.ui.Modal, title="Edit Character Name"):
    new_name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Enter your in-game name",
        max_length=32,
    )

    def __init__(self, raid_id: int, user_id: int):
        super().__init__()
        self.raid_id = raid_id
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        entry = get_signup_entry(self.raid_id, str(self.user_id))
        if not entry:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        new_name = str(self.new_name).strip()
        class_name = entry.get("class")

        ok = update_user_name(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
            new_name=new_name,
        )

        if not ok:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        if class_name:
            update_character_name_by_class(self.user_id, class_name, new_name)

        try:
            await refresh_signup_message_by_id(interaction.channel, self.raid_id)
        except Exception:
            pass

        updated = get_signup_entry(self.raid_id, str(self.user_id))
        if not updated:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(updated),
            view=SignupOptionsView(self.raid_id, self.user_id),
        )

        asyncio.create_task(delete_ephemeral_after(interaction))


class EditNoteModal(discord.ui.Modal, title="Edit Note"):
    new_note = discord.ui.TextInput(
        label="Note",
        placeholder="Optional note for raid leader",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=200,
    )

    def __init__(self, raid_id: int, user_id: int):
        super().__init__()
        self.raid_id = raid_id
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        ok = update_user_note(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
            note=str(self.new_note).strip(),
        )

        if not ok:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        try:
            await refresh_signup_message_by_id(interaction.channel, self.raid_id)
        except Exception:
            pass

        updated = get_signup_entry(self.raid_id, str(self.user_id))
        if not updated:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(updated),
            view=SignupOptionsView(self.raid_id, self.user_id),
        )

        asyncio.create_task(delete_ephemeral_after(interaction))


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

        update_character_spec_by_class(
            self.user_id,
            self.selected_class,
            selected_spec,
            role,
        )

        try:
            await refresh_signup_message_by_id(interaction.channel, self.raid_id)
        except Exception:
            pass

        updated = get_signup_entry(self.raid_id, str(self.user_id))
        if not updated:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=None,
            embed=build_signup_options_embed(updated),
            view=SignupOptionsView(self.raid_id, self.user_id),
        )

        asyncio.create_task(delete_ephemeral_after(interaction))


class EditSpecView(discord.ui.View):
    def __init__(self, raid_id: int, user_id: int, selected_class: str):
        super().__init__(timeout=60)
        self.add_item(EditSpecSelect(raid_id, user_id, selected_class))


class EditNameButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Edit Name",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditNameModal(self.raid_id, self.user_id))


class EditSpecButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Edit Spec",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        entry = get_signup_entry(self.raid_id, str(self.user_id))
        if not entry:
            await interaction.response.send_message("Signup not found.", ephemeral=True)
            return

        selected_class = entry.get("class")
        if not selected_class or selected_class not in config.CLASS_SPECS:
            await interaction.response.send_message(
                "Class not found for this signup.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content="Choose a new spec:",
            embed=None,
            view=EditSpecView(self.raid_id, self.user_id, selected_class),
        )


class EditNoteButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Edit Note",
            style=discord.ButtonStyle.secondary,
            row=0,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditNoteModal(self.raid_id, self.user_id))


class RemoveSignupButton(discord.ui.Button):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(
            label="Remove Signup",
            style=discord.ButtonStyle.danger,
            row=1,
        )
        self.raid_id = raid_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        remove_user_signup(
            raid_id=self.raid_id,
            user_id=str(self.user_id),
        )

        try:
            await refresh_signup_message_by_id(interaction.channel, self.raid_id)
        except Exception:
            pass

        await interaction.response.edit_message(
            content="❌ Signup removed.",
            embed=None,
            view=None,
        )

        asyncio.create_task(delete_ephemeral_after(interaction, 5))


class SignupOptionsView(discord.ui.View):
    def __init__(self, raid_id: int, user_id: int):
        super().__init__(timeout=90)
        self.add_item(EditNameButton(raid_id, user_id))
        self.add_item(EditSpecButton(raid_id, user_id))
        self.add_item(EditNoteButton(raid_id, user_id))
        self.add_item(RemoveSignupButton(raid_id, user_id))