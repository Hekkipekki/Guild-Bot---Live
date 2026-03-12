from data.signup_store import load_signups, save_signups
from logic.embed_builder import build_signup_embed
from views.signup_views import SignupView


def _store_signup_for_message(message_id: int, signup: dict) -> None:
    data = load_signups()
    data[str(message_id)] = signup
    save_signups(data)


async def send_signup_message(ctx, signup: dict) -> bool:
    try:
        embed = build_signup_embed(signup["title"], signup["description"], signup)

        message = await ctx.send(embed=embed)

        _store_signup_for_message(message.id, signup)

        await message.edit(view=SignupView(str(message.id)))
        return True

    except Exception:
        return False