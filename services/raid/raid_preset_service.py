from services.signup.signup_preset_service import build_signup_payload
from services.signup.signup_template_service import build_fake_users
from utils.time_helpers import next_weekday


DEFAULT_LEADER = "Hekkipekki / Rhegaran"
DEFAULT_DESCRIPTION = "Continuation of HC Progress"


def build_wednesday_signup(channel_id: int) -> dict:
    return build_signup_payload(
        title="HC Progression - Wednesday",
        description=DEFAULT_DESCRIPTION,
        leader=DEFAULT_LEADER,
        start_ts=next_weekday(2, 19, 30),
        channel_id=channel_id,
    )


def build_sunday_signup(channel_id: int) -> dict:
    return build_signup_payload(
        title="HC Progression - Sunday",
        description=DEFAULT_DESCRIPTION,
        leader=DEFAULT_LEADER,
        start_ts=next_weekday(6, 19, 30),
        channel_id=channel_id,
    )


def build_template_signup(channel_id: int) -> dict:
    return build_signup_payload(
        title="HC Progression - Template Preview",
        description="Visual preview with fake raid roster",
        leader=DEFAULT_LEADER,
        start_ts=next_weekday(2, 19, 30),
        channel_id=channel_id,
        users=build_fake_users(),
    )