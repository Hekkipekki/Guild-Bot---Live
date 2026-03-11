import discord
import config

from services.raid_control_service import (
    get_players,
    get_valid_specs_for_player,
    change_player_spec,
)
from services.signup_refresh_service import refresh_signup_message_by_id


class RaidControlSpecPlayerSelect(discord.ui.Select):
    def __init__(self, raid_id: str):
        self.raid_id = raid_id

        players = get_players(raid_id)
        options = []

        for player in players[:25]:
            name = player.get("name") or "Unknown"
            wow_class = player.get("class") or "Unknown"
            spec = player.get("spec") or "Unknown"
            status = player.get("status") or "Unknown"

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=str(player["user_id"]),
                    description=f"{wow_class} • {spec} • {status}"[:100],
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No players found",
                    value="__none__",
                    description="There are no signups to manage.",
                )
            )

        super().__init__(
            placeholder="Select player...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "__none__":
            await interaction.response.defer()
            return

        self.view.selected_user_id = self.values[0]
        self.view.rebuild_spec_select()

        await interaction.response.edit_message(
            content="Change a player's spec for this raid only.",
            view=self.view,
        )


class RaidControlSpecSelect(discord.ui.Select):
    def __init__(self, raid_id: str, user_id: str | None):
        self.raid_id = raid_id
        self.user_id = user_id

        options = []

        if user_id:
            valid_specs = get_valid_specs_for_player(raid_id, user_id)

            for item in valid_specs:
                spec_name = item["spec"]
                role_name = item["role"]
                emoji = None

                raw = config.SPEC_EMOJIS.get(spec_name)
                if raw:
                    try:
                        emoji = discord.PartialEmoji.from_str(raw)
                    except Exception:
                        emoji = None

                options.append(
                    discord.SelectOption(
                        label=spec_name[:100],
                        value=spec_name,
                        description=f"Role: {role_name}"[:100],
                        emoji=emoji,
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(
                    label="Select a player first",
                    value="__none__",
                    description="Spec choices appear after player selection.",
                )
            )

        super().__init__(
            placeholder="Select spec...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "__none__":
            await interaction.response.defer()
            return

        self.view.selected_spec = self.values[0]
        await interaction.response.defer()


class ApplySpecChangeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Apply Spec",
            style=discord.ButtonStyle.primary,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if not view.selected_user_id:
            await interaction.response.send_message(
                "Select a player first.",
                ephemeral=True,
            )
            return

        if not view.selected_spec:
            await interaction.response.send_message(
                "Select a spec first.",
                ephemeral=True,
            )
            return

        ok = change_player_spec(
            view.raid_id,
            view.selected_user_id,
            view.selected_spec,
        )

        if not ok:
            await interaction.response.send_message(
                "Could not change that player's spec.",
                ephemeral=True,
            )
            return

        try:
            await refresh_signup_message_by_id(interaction.channel, int(view.raid_id))
        except Exception as e:
            await interaction.response.send_message(
                f"Spec updated, but failed to refresh raid: {e}",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Player spec changed to {view.selected_spec}.",
            ephemeral=True,
        )


class RaidControlSpecView(discord.ui.View):
    def __init__(self, raid_id: str):
        super().__init__(timeout=120)
        self.raid_id = raid_id
        self.selected_user_id = None
        self.selected_spec = None

        self.player_select = RaidControlSpecPlayerSelect(raid_id)
        self.spec_select = RaidControlSpecSelect(raid_id, None)

        self.add_item(self.player_select)
        self.add_item(self.spec_select)
        self.add_item(ApplySpecChangeButton())

    def rebuild_spec_select(self):
        if self.spec_select in self.children:
            self.remove_item(self.spec_select)

        self.selected_spec = None
        self.spec_select = RaidControlSpecSelect(self.raid_id, self.selected_user_id)
        self.add_item(self.spec_select)