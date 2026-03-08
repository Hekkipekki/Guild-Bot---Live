from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

from data.signup_store import load_signups, save_signups
from views.signup_views import SignupView, build_signup_embed


SWEDEN_TZ = ZoneInfo("Europe/Stockholm")


def make_start_ts(year: int, month: int, day: int, hour: int, minute: int) -> int:
    dt = datetime(year, month, day, hour, minute, tzinfo=SWEDEN_TZ)
    return int(dt.timestamp())


def next_weekday(weekday: int, hour: int, minute: int) -> int:
    now = datetime.now(SWEDEN_TZ)

    days_ahead = weekday - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    next_day = now + timedelta(days=days_ahead)

    event_time = next_day.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    return int(event_time.timestamp())


class SignupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_signup_message(
        self,
        ctx: commands.Context,
        *,
        title: str,
        description: str,
        leader: str,
        start_ts: int,
    ) -> None:
        signup = {
            "title": title,
            "description": description,
            "leader": leader,
            "start_ts": start_ts,
            "users": {},
        }

        embed = build_signup_embed(signup["title"], signup["description"], signup)

        message = await ctx.send(embed=embed)
        await message.edit(view=SignupView(str(message.id)))

        data = load_signups()
        data[str(message.id)] = signup
        save_signups(data)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        deleted = await ctx.channel.purge(limit=1000)

        msg = await ctx.send(f"💣 Deleted {len(deleted)} messages.")
        await msg.delete(delay=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def wedsignup(self, ctx: commands.Context):
        start_ts = next_weekday(2, 19, 30)

        await self.create_signup_message(
            ctx,
            title="HC Progression - Wednesday",
            description="Continuation of HC Progress",
            leader="Hekkipekki / Rhegaran",
            start_ts=start_ts,
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sunsignup(self, ctx: commands.Context):
        start_ts = next_weekday(6, 19, 30)

        await self.create_signup_message(
            ctx,
            title="HC Progression - Sunday",
            description="Continuation of HC Progress",
            leader="Hekkipekki / Rhegaran",
            start_ts=start_ts,
        )


async def setup(bot):
    await bot.add_cog(SignupCommands(bot))