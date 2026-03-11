import discord
from discord.ext import commands

from data.signup_store import load_signups, save_signups, remove_message_signup
from services.raid_preset_service import (
    build_wednesday_signup,
    build_sunday_signup,
    build_template_signup,
)
from services.signup_message_service import send_signup_message


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
        signup = build_wednesday_signup(ctx.channel.id)
        await send_signup_message(ctx, signup)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def template(self, ctx: commands.Context):
        signup = build_template_signup(ctx.channel.id)
        await send_signup_message(ctx, signup)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sunsignup(self, ctx: commands.Context):
        signup = build_sunday_signup(ctx.channel.id)
        await send_signup_message(ctx, signup)


async def setup(bot):
    await bot.add_cog(SignupCommands(bot))