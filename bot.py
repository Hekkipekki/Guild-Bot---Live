import asyncio
import traceback

import discord
from discord.ext import commands

import config
from data.signup_store import load_signups
from services.guild.weakauras_panel_service import ensure_weakauras_panel_for_guild
from views.raidpack_views import RaidPackView
from views.signup_views import SignupView


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

_views_registered = False
_commands_synced = False

EXTENSIONS = [
    "cogs.signup",
    "cogs.reminders",
    "cogs.guild_admin",
    "cogs.raid_builder",
    "cogs.raid_lifecycle",
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
        test_guild_id = getattr(config, "TEST_GUILD_ID", None)

        if test_guild_id:
            guild_obj = discord.Object(id=test_guild_id)

            # Clear old guild-only commands that may still exist from earlier testing
            bot.tree.clear_commands(guild=guild_obj)
            cleared = await bot.tree.sync(guild=guild_obj)
            print(f"Cleared guild slash commands for {test_guild_id}. Remaining guild commands: {len(cleared)}")

        # Sync current global commands
        synced = await bot.tree.sync()
        print(f"Globally synced {len(synced)} slash command(s).")

    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

    _commands_synced = True


async def _load_extensions() -> None:
    for extension in EXTENSIONS:
        await bot.load_extension(extension)


async def _ensure_weakauras_panels() -> None:
    for guild in bot.guilds:
        try:
            ok, message = await ensure_weakauras_panel_for_guild(bot, guild)
            print(f"[WA] {guild.name}: {message}")
        except Exception as e:
            print(f"[WA] {guild.name}: failed - {e}")


@bot.event
async def on_ready():
    _register_persistent_views()
    await _sync_guild_commands()
    await _ensure_weakauras_panels()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    print("Command error:")
    traceback.print_exception(type(error), error, error.__traceback__)


async def main():
    async with bot:
        await _load_extensions()
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())