"""
Facade for signup-related operations used by the Discord view layer.

The goal of this module is to provide one stable import surface for:
- signup state mutations
- signup message refresh operations

Views should import from this module instead of importing directly from
lower-level signup services.
"""

from services.signup_service import (
    get_signup_user,
    set_user_status,
    remove_user_signup,
    set_user_class,
    set_user_spec,
    update_user_name,
    update_user_note,
    update_user_spec,
)

from services.signup_refresh_service import (
    refresh_signup_message,
    refresh_signup_message_by_id,
)

__all__ = [
    "get_signup_user",
    "set_user_status",
    "remove_user_signup",
    "set_user_class",
    "set_user_spec",
    "update_user_name",
    "update_user_note",
    "update_user_spec",
    "refresh_signup_message",
    "refresh_signup_message_by_id",
]