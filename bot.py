import asyncio
import discord
from discord.ext import commands

import config
from data.signup_store import load_signups
from views.raidpack_views import RaidPackView
from views.signup_views import SignupView

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
_views_registered = False


@bot.event
async def on_ready():
    global _views_registered

    if not _views_registered:
        bot.add_view(RaidPackView())

        signups = load_signups()
        for message_id in signups.keys():
            try:
                bot.add_view(SignupView(str(message_id)), message_id=int(message_id))
            except Exception as e:
                print(f"Failed to register SignupView for message {message_id}: {e}")

        _views_registered = True

    print(f"Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    print(f"Command error: {error}")
    await ctx.send(f"Command error: {error}")


@bot.command()
async def specicons(ctx):
    lines = [f'"{e.name}": "{str(e)}",' for e in ctx.guild.emojis]

    for i in range(0, len(lines), 20):
        chunk = "\n".join(lines[i:i + 20])
        await ctx.send(f"```python\n{chunk}\n```")


async def main():
    async with bot:
        await bot.load_extension("cogs.wa_commands")
        await bot.load_extension("cogs.signup")
        await bot.load_extension("cogs.reminders")
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())