import discord
import config

from utils.ui_timing import SIGNUP_OPTIONS_AUTO_DELETE_SECONDS


def build_signup_options_embed(entry: dict) -> discord.Embed:
    spec_name = entry.get("spec", "-")
    class_name = entry.get("class", "-")
    char_name = entry.get("name", "-")
    note = entry.get("note", "")
    spec_emoji = config.SPEC_EMOJIS.get(spec_name, "")

    embed = discord.Embed(
        title="✅ You have been signed up to the event!",
        description="## ⚙ Sign-Up Options",
        color=discord.Color.purple(),
    )

    embed.add_field(name="Name", value=char_name or "-", inline=False)
    embed.add_field(name="Class", value=class_name or "-", inline=True)
    embed.add_field(
        name="Spec",
        value=f"{spec_emoji} {spec_name}".strip() or "-",
        inline=True,
    )
    embed.add_field(name="Note", value=note or "-", inline=False)
    embed.set_footer(
        text=f"This panel closes automatically after {AUTO_DELETE_SECONDS} seconds."
    )

    return embed