import discord
import config

from logic.roster_builder import rebuild_roster
from logic.unassigned import get_unassigned_players


def get_player_display_text(user_id: str, info: dict) -> str:
    """
    Priority for signed players:
    1. explicit signup character name
    2. fallback to stored display_name if present
    3. fallback to Discord mention
    """
    char_name = (info.get("name") or "").strip()
    if char_name:
        return char_name

    display_name = (info.get("display_name") or "").strip()
    if display_name:
        return display_name

    return f"<@{user_id}>"


def format_player_line(user_id: str, info: dict) -> str:
    spec = info.get("spec", "Unknown")
    emoji = config.SPEC_EMOJIS.get(spec, "")
    player_text = get_player_display_text(user_id, info)

    return f"{emoji} {player_text}" if emoji else player_text


def format_unassigned_player(user_id: str) -> str:
    return f"<@{user_id}>"


def build_signup_embed(title: str, description: str, signup: dict) -> discord.Embed:
    users = signup.get("users", {})
    roster = rebuild_roster(users)

    embed = discord.Embed(
        title=title,
        color=discord.Color.purple(),
    )

    leader_text = signup.get("leader", "Hekkipekki / Rhegaran")
    start_ts = signup.get("start_ts")

    tanks = roster["roles"]["Tank"]
    healers = roster["roles"]["Healer"]
    dps = roster["roles"]["DPS"]

    melee_count = sum(
        1
        for _, info in users.items()
        if info.get("status") == "sign" and info.get("role") == "Melee"
    )
    ranged_count = sum(
        1
        for _, info in users.items()
        if info.get("status") == "sign" and info.get("role") == "Ranged"
    )
    total_signed = len(tanks) + len(healers) + len(dps)

    tank_value = "\n".join(
        format_player_line(user_id, info) for user_id, info in tanks
    ) if tanks else "-"

    healer_value = "\n".join(
        format_player_line(user_id, info) for user_id, info in healers
    ) if healers else "-"

    dps_value = "\n".join(
        format_player_line(user_id, info) for user_id, info in dps
    ) if dps else "-"

    summary_icons = getattr(config, "SUMMARY_EMOJIS", {})

    countdown_icon = summary_icons.get("Countdown", "⏳")
    absence_icon = summary_icons.get("Absence", "🚫")
    signups_icon = summary_icons.get("Signups", "👥")
    dps_icon = summary_icons.get("DPS", "⚔️")
    tank_icon = summary_icons.get("Tank", "🛡️")
    healer_icon = summary_icons.get("Healer", "➕")
    tentative_icon = summary_icons.get("Tentative", "❔")
    late_icon = summary_icons.get("Late", "🕒")
    calendar_icon = summary_icons.get("Calendar", "📅")
    bench_icon = summary_icons.get("Bench", "🪑")

    embed.description = description

    embed.add_field(name="Leader", value=f"🏳️ {leader_text}", inline=True)
    embed.add_field(name="Signups", value=f"{signups_icon} {total_signed}", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    if start_ts:
        date_value = f"{calendar_icon} <t:{start_ts}:D>"
        time_value = f"🕒 <t:{start_ts}:t>"
        countdown_value = f"{countdown_icon} <t:{start_ts}:R>"
    else:
        date_value = f"{calendar_icon} -"
        time_value = "🕒 -"
        countdown_value = f"{countdown_icon} -"

    embed.add_field(name="Date", value=date_value, inline=True)
    embed.add_field(name="Time", value=time_value, inline=True)
    embed.add_field(name="Countdown", value=countdown_value, inline=True)

    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.add_field(
        name=f"{tank_icon} Tanks ({len(tanks)})",
        value=tank_value,
        inline=True,
    )
    embed.add_field(
        name=f"{healer_icon} Healers ({len(healers)})",
        value=healer_value,
        inline=True,
    )
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(
        name=f"{dps_icon} DPS ({len(dps)}) — Melee {melee_count} / Ranged {ranged_count}",
        value=dps_value,
        inline=False,
    )

    def add_optional_line(label: str, entries: list, icon: str):
        if not entries:
            return

        value = "\n".join(
            format_player_line(user_id, info) for user_id, info in entries
        )

        embed.add_field(
            name=f"{icon} {label} ({len(entries)})",
            value=value,
            inline=False,
        )

    add_optional_line("Late", roster["late"], late_icon)
    add_optional_line("Tentative", roster["tentative"], tentative_icon)
    add_optional_line("Bench", roster["bench"], bench_icon)
    add_optional_line("Absence", roster["absence"], absence_icon)

    unassigned_players = get_unassigned_players(signup)

    if unassigned_players:
        embed.add_field(
            name=f"📌 Unassigned Players ({len(unassigned_players)})",
            value=" ".join(format_unassigned_player(user_id) for user_id in unassigned_players),
            inline=False,
        )

    return embed