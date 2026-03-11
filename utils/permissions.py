import config


def is_raid_controller(user_id: int) -> bool:
    """
    Returns True if the user is explicitly listed as a raid controller.
    """
    return user_id in getattr(config, "RAID_CONTROL_USER_IDS", [])


def is_admin(member) -> bool:
    """
    Returns True if the Discord member has administrator permissions.
    """
    try:
        return member.guild_permissions.administrator
    except AttributeError:
        return False


def can_manage_raid_tools(member) -> bool:
    """
    Permission for raid management tools such as:

    - raid control panel
    - /raidleader
    - /raiddesc
    - /raiddate
    - /raidtime
    - /raidtitle
    - !wedsignup / !sunsignup
    """
    if member is None:
        return False

    if is_admin(member):
        return True

    if is_raid_controller(member.id):
        return True

    return False


def can_use_admin_tools(member) -> bool:
    """
    Permission for dangerous bot-level commands such as:

    - !nuke
    - destructive resets
    """
    if member is None:
        return False

    return is_admin(member)