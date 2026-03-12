import asyncio
import traceback

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
_commands_synced = False

EXTENSIONS = [
    "cogs.wa_commands",
    "cogs.signup",
    "cogs.reminders",
    "cogs.guild_admin",
    "cogs.raid_builder",
]


def _get_persistent_signup_ids() -> list[str]:
    signups = load_signups()
    return list(signups.keys())


def _register_persistent_views() -> None:
    global _views_registered

    if _views_registered:
        return

    bot.add_view(RaidPackView())

    for message_id in _get_persistent_signup_ids():
        try:
            bot.add_view(SignupView(str(message_id)))
        except Exception as e:
            print(f"Failed to register SignupView for message {message_id}: {e}")

    _views_registered = True


async def _sync_guild_commands() -> None:
    global _commands_synced

    if _commands_synced:
        return

    try:
        guild_obj = discord.Object(id=config.TEST_GUILD_ID)
        bot.tree.copy_global_to(guild=guild_obj)
        synced = await bot.tree.sync(guild=guild_obj)
        print(f"Synced {len(synced)} guild slash command(s) to {config.TEST_GUILD_ID}.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

    _commands_synced = True


async def _load_extensions() -> None:
    for extension in EXTENSIONS:
        await bot.load_extension(extension)


@bot.event
async def on_ready():
    _register_persistent_views()
    await _sync_guild_commands()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    print("Command error:")
    traceback.print_exception(type(error), error, error.__traceback__)


@bot.command()
async def specicons(ctx):
    lines = [f'"{e.name}": "{str(e)}",' for e in ctx.guild.emojis]

    for i in range(0, len(lines), 20):
        chunk = "\n".join(lines[i:i + 20])
        await ctx.send(f"```python\n{chunk}\n```")


async def main():
    async with bot:
        await _load_extensions()
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())