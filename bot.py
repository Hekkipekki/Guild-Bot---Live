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
_commands_synced = False


@bot.event
async def on_ready():
    global _views_registered, _commands_synced

    if not _views_registered:
        bot.add_view(RaidPackView())

        signups = load_signups()
        for message_id in signups.keys():
            try:
                bot.add_view(SignupView(str(message_id), bot))
            except Exception as e:
                print(f"Failed to register SignupView for message {message_id}: {e}")

        _views_registered = True

    if not _commands_synced:
        try:
            guild_obj = discord.Object(id=config.TEST_GUILD_ID)
            bot.tree.copy_global_to(guild=guild_obj)
            synced = await bot.tree.sync(guild=guild_obj)
            print(f"Synced {len(synced)} guild slash command(s) to {config.TEST_GUILD_ID}.")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")

        _commands_synced = True

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
        await bot.load_extension("cogs.raid_leader")
        await bot.load_extension("cogs.reminders")
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())