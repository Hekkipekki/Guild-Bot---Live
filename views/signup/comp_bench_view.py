import asyncio
import discord

from services.comp_message_service import post_comp_message
from utils.ui_timing import RAID_CONTROL_AUTO_DELETE_SECONDS, ERROR_MESSAGE_AUTO_DELETE_SECONDS
from views.signup_options.helpers import (
    delete_ephemeral_after,
    delete_followup_message_after,
)


def _display_role(entry: dict) -> str:
    role = entry.get("role", "")
    if role in ("Melee", "Ranged"):
        return "DPS"
    return role


def _player_label(user_id: str, entry: dict) -> str:
    name = entry.get("name") or entry.get("display_name") or user_id
    spec = entry.get("spec", "")
    role = _display_role(entry)
    return f"{name} ({spec} {role})"


def _sort_by_timestamp(players: list[tuple[str, dict]]) -> list[tuple[str, dict]]:
    return sorted(players, key=lambda item: item[1].get("timestamp", 0))


def _group_signed(players: list[tuple[str, dict]]) -> dict[str, list[tuple[str, dict]]]:
    grouped = {"Tank": [], "Healer": [], "DPS": []}

    for user_id, entry in players:
        role = _display_role(entry)
        if role in grouped:
            grouped[role].append((user_id, entry))

    return grouped


def _rebuild_comp_from_choice(comp_data: dict, benched_user_id: str) -> dict:
    signed_players = [
        (user_id, entry)
        for user_id, entry in comp_data.get("signed_players", [])
        if user_id != benched_user_id
    ]

    grouped = _group_signed(_sort_by_timestamp(signed_players))
    role_targets = comp_data.get("role_targets", {})

    tanks = grouped["Tank"][:role_targets.get("Tank", 2)]
    healers = grouped["Healer"][:role_targets.get("Healer", 0)]
    dps = grouped["DPS"][:role_targets.get("DPS", 0)]

    selected_players = tanks + healers + dps
    selected_ids = {user_id for user_id, _ in selected_players}

    group_1 = list(tanks) + list(healers)
    remaining_dps = list(dps)

    while len(group_1) < 5 and remaining_dps:
        group_1.append(remaining_dps.pop(0))

    group_2 = remaining_dps

    existing_bench = [
        p for p in comp_data.get("bench_players", [])
        if p[0] not in selected_ids
    ]

    manually_benched_choice = next(
        ((user_id, entry) for user_id, entry in comp_data.get("signed_players", []) if user_id == benched_user_id),
        None,
    )

    overflow_signed = [
        (user_id, entry)
        for user_id, entry in signed_players
        if user_id not in selected_ids
    ]

    new_bench = list(existing_bench)
    if manually_benched_choice and all(manually_benched_choice[0] != uid for uid, _ in new_bench):
        new_bench.append(manually_benched_choice)

    for user_id, entry in overflow_signed:
        if all(user_id != existing_id for existing_id, _ in new_bench):
            new_bench.append((user_id, entry))

    updated = dict(comp_data)
    updated["selected_players"] = selected_players
    updated["mentions"] = [f"<@{user_id}>" for user_id, _ in selected_players]
    updated["group_1"] = group_1
    updated["group_2"] = group_2
    updated["bench_players"] = new_bench

    return updated


class BenchSelect(discord.ui.Select):
    def __init__(self, comp_data: dict, candidates: list[tuple[str, dict]]):
        options = []

        for user_id, entry in candidates:
            options.append(
                discord.SelectOption(
                    label=_player_label(user_id, entry)[:100],
                    value=user_id,
                )
            )

        super().__init__(
            placeholder="Select player to bench",
            min_values=1,
            max_values=1,
            options=options,
        )

        self.comp_data = comp_data
        self.candidates = candidates

    async def callback(self, interaction: discord.Interaction):
        try:
            selected_id = self.values[0]
            final_comp_data = _rebuild_comp_from_choice(self.comp_data, selected_id)

            await interaction.response.defer(ephemeral=True)

            ok, message = await post_comp_message(
                interaction.channel,
                final_comp_data,
            )

            if not ok:
                msg = await interaction.followup.send(
                    message,
                    ephemeral=True,
                    wait=True,
                )
                asyncio.create_task(
                    delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
                )
                return

            msg = await interaction.followup.send(
                "Comp posted.",
                ephemeral=True,
                wait=True,
            )

            asyncio.create_task(
                delete_followup_message_after(msg, RAID_CONTROL_AUTO_DELETE_SECONDS)
            )
        except Exception as e:
            msg = await interaction.followup.send(
                f"Failed to post comp: {type(e).__name__}: {e}",
                ephemeral=True,
                wait=True,
            )
            asyncio.create_task(
                delete_followup_message_after(msg, ERROR_MESSAGE_AUTO_DELETE_SECONDS)
            )


class CompBenchView(discord.ui.View):
    def __init__(self, comp_data: dict, candidates: list[tuple[str, dict]]):
        super().__init__(timeout=120)
        self.add_item(BenchSelect(comp_data, candidates))