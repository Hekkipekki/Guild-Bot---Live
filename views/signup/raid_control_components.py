import discord

from services.raid_control_service import get_players


ACTION_VALUES = {
    "bench": "Bench",
    "late": "Late",
    "tentative": "Tentative",
    "absence": "Absence",
    "remove": "Remove Signup",
}


class RaidControlPlayerSelect(discord.ui.Select):
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
        await interaction.response.defer()


class RaidControlActionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in ACTION_VALUES.items()
        ]

        super().__init__(
            placeholder="Select action...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_action = self.values[0]
        await interaction.response.defer()