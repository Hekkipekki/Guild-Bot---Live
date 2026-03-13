import discord

from services.guild.guild_settings_service import get_guild_defaults


def build_guild_config_embed(guild: discord.Guild) -> discord.Embed:
    settings = get_guild_defaults(guild.id)

    raid_admins = settings.get("raid_control_user_ids", [])
    raid_team = settings.get("expected_players", [])
    default_description = settings.get("default_description", "") or "-"
    weakauras_channel_id = settings.get("weakauras_channel_id")

    raid_admin_text = "\n".join(f"• <@{user_id}>" for user_id in raid_admins) if raid_admins else "-"
    raid_team_text = "\n".join(f"• <@{user_id}>" for user_id in raid_team) if raid_team else "-"
    wa_channel_text = f"<#{weakauras_channel_id}>" if weakauras_channel_id else "-"

    embed = discord.Embed(
        title=f"Guild Admin — {guild.name}",
        description="Configure this server's raid bot settings.",
        color=discord.Color.purple(),
    )
    embed.add_field(name="Raid Description Template", value=default_description, inline=False)
    embed.add_field(name="Raid Admins", value=raid_admin_text, inline=False)
    embed.add_field(name="Raid Team", value=raid_team_text, inline=False)
    embed.add_field(name="WeakAuras Channel", value=wa_channel_text, inline=False)
    embed.set_footer(text="This admin panel closes automatically.")
    return embed