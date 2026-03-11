import discord
from views.signup.status_buttons import SignupStatusButton
from views.signup.class_dropdown import ClassDropdown


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