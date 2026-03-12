from services.guild.guild_settings_service import get_raid_control_users


def can_manage_raid_tools(user) -> bool:
    if getattr(user.guild_permissions, "administrator", False):
        return True

    guild = getattr(user, "guild", None)
    if guild is None:
        return False

    allowed_ids = get_raid_control_users(guild.id)
    return str(user.id) in allowed_ids