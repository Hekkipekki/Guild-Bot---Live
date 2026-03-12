import discord
import config


def _player_line(user_id: str, entry: dict) -> str:
    name = (entry.get("name") or "").strip()
    if not name:
        name = (entry.get("display_name") or "").strip()

    if not name:
        name = f"<@{user_id}>"

    spec = entry.get("spec", "")
    emoji = config.SPEC_EMOJIS.get(spec, "")

    return f"{emoji} {name}".strip() if emoji else name


def _group_value(players: list[tuple[str, dict]]) -> str:
    if not players:
        return "-"

    return "\n".join(_player_line(user_id, entry) for user_id, entry in players)


def build_comp_embed(comp_data: dict) -> discord.Embed:
    title = comp_data.get("title", "Raid Comp")
    description = comp_data.get("description", "")
    leader = comp_data.get("leader", "")
    start_ts = comp_data.get("start_ts")

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.purple(),
    )

    if leader:
        embed.add_field(name="Leader", value=f"🏳️ {leader}", inline=False)

    if start_ts:
        embed.add_field(name="Date", value=f"<t:{start_ts}:D>", inline=True)
        embed.add_field(name="Time", value=f"<t:{start_ts}:t>", inline=True)
        embed.add_field(name="Countdown", value=f"<t:{start_ts}:R>", inline=True)

    embed.add_field(
        name="Group 1",
        value=_group_value(comp_data.get("group_1", [])),
        inline=True,
    )
    embed.add_field(
        name="Group 2",
        value=_group_value(comp_data.get("group_2", [])),
        inline=True,
    )

    bench_players = comp_data.get("bench_players", [])
    if bench_players:
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(
            name=f"Bench ({len(bench_players)})",
            value=_group_value(bench_players),
            inline=False,
        )

    embed.set_footer(text="Composition Tool")
    return embed