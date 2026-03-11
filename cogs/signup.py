import discord
from discord.ext import commands

from data.signup_store import load_signups, save_signups, remove_message_signup
from services.signup_creation_service import (
    build_fake_users,
    build_signup_payload,
    send_signup_message,
)
from utils.time_helpers import next_weekday


class SignupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        deleted_messages = await ctx.channel.purge(limit=1000)

        data = load_signups()
        removed_signups = 0

        for message in deleted_messages:
            if remove_message_signup(data, message.id):
                removed_signups += 1

        if removed_signups:
            save_signups(data)

        msg = await ctx.send(
            f"💣 Deleted {len(deleted_messages)} messages. "
            f"Removed {removed_signups} signup entries from JSON."
        )
        await msg.delete(delay=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def wedsignup(self, ctx: commands.Context):
        signup = build_signup_payload(
            title="HC Progression - Wednesday",
            description="Continuation of HC Progress",
            leader="Hekkipekki / Rhegaran",
            start_ts=next_weekday(2, 19, 30),
            channel_id=ctx.channel.id,
        )
        await send_signup_message(ctx, signup)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def template(self, ctx: commands.Context):
        signup = build_signup_payload(
            title="HC Progression - Template Preview",
            description="Visual preview with fake raid roster",
            leader="Hekkipekki / Rhegaran",
            start_ts=next_weekday(2, 19, 30),
            channel_id=ctx.channel.id,
            users=build_fake_users(),
        )
        await send_signup_message(ctx, signup)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sunsignup(self, ctx: commands.Context):
        signup = build_signup_payload(
            title="HC Progression - Sunday",
            description="Continuation of HC Progress",
            leader="Hekkipekki / Rhegaran",
            start_ts=next_weekday(6, 19, 30),
            channel_id=ctx.channel.id,
        )
        await send_signup_message(ctx, signup)


async def setup(bot):
    await bot.add_cog(SignupCommands(bot))