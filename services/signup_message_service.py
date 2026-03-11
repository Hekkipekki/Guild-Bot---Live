from data.signup_store import load_signups, save_signups
from logic.embed_builder import build_signup_embed
from views.signup_views import SignupView


async def send_signup_message(ctx, signup: dict) -> None:
    embed = build_signup_embed(signup["title"], signup["description"], signup)

    message = await ctx.send(embed=embed)

    data = load_signups()
    data[str(message.id)] = signup
    save_signups(data)

    await message.edit(view=SignupView(str(message.id)))