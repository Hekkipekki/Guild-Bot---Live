import discord
import config

from logic.signup_manager import (
    set_user_class,
    set_user_spec,
    refresh_signup_message_by_id,
)


class ClassSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=class_name, value=class_name)
            for class_name in config.CLASSES
        ]

        super().__init__(
            placeholder="Select your class",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_class = self.values[0]
        parent_message_id = self.view.parent_message_id
        user_id = str(interaction.user.id)

        set_user_class(parent_message_id, user_id, selected_class)

        await interaction.response.edit_message(
            content=f"Class set to **{selected_class}**. Now choose your spec:",
            view=SpecPickerView(
                parent_message_id=parent_message_id,
                selected_class=selected_class,
            ),
        )


class SpecSelect(discord.ui.Select):
    def __init__(self, selected_class: str):
        self.selected_class = selected_class

        options = [
            discord.SelectOption(label=spec, value=spec)
            for spec in config.CLASS_SPECS[selected_class].keys()
        ]

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

        parent_message_id = self.view.parent_message_id
        user_id = str(interaction.user.id)

        set_user_spec(
            raid_id=parent_message_id,
            user_id=user_id,
            selected_class=selected_class,
            selected_spec=selected_spec,
            role=role,
            auto_sign=True,
        )

        try:
            await refresh_signup_message_by_id(interaction.channel, parent_message_id)
        except discord.NotFound:
            await interaction.response.send_message(
                "⚠ Could not find the signup message.",
                ephemeral=True,
            )
            return
        except Exception as e:
            await interaction.response.send_message(
                f"⚠ Spec selection failed: {e}",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content="✅ Class and spec saved.",
            view=None,
        )


class ClassPickerView(discord.ui.View):
    def __init__(self, parent_message_id: int):
        super().__init__(timeout=120)
        self.parent_message_id = parent_message_id
        self.add_item(ClassSelect())


class SpecPickerView(discord.ui.View):
    def __init__(self, parent_message_id: int, selected_class: str):
        super().__init__(timeout=120)
        self.parent_message_id = parent_message_id
        self.add_item(SpecSelect(selected_class=selected_class))