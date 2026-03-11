import discord

from data.signup_store import load_signups, get_message_signup
from logic.embed.signup_embed import build_signup_embed


async def refresh_signup_message(interaction: discord.Interaction, raid_id: int) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)

    title = signup.get("title", "Raid Signup")
    description = signup.get("description", "")
    embed = build_signup_embed(title, description, signup)

    from views.signup_views import SignupView

    await interaction.message.edit(
        embed=embed,
        view = SignupView(str(raid_id), bot),
    )


async def refresh_signup_message_by_id(
    channel: discord.abc.Messageable,
    raid_id: int,
) -> None:
    data = load_signups()
    signup = get_message_signup(data, raid_id)

    title = signup.get("title", "Raid Signup")
    description = signup.get("description", "")
    embed = build_signup_embed(title, description, signup)

    from views.signup_views import SignupView

    message = await channel.fetch_message(raid_id)
    await message.edit(
        embed=embed,
        view = SignupView(str(raid_id), bot),
    )