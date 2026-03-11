import config


def can_manage_raid_tools(user) -> bool:
    """
    Check if a user is allowed to use raid leader tools.
    """

    if user.id in getattr(config, "RAID_CONTROL_USER_IDS", []):
        return True

    # Optional: allow server administrators as fallback
    if getattr(user.guild_permissions, "administrator", False):
        return True

    return False