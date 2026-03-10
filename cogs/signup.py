from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random

import discord
from discord.ext import commands

from data.signup_store import load_signups, save_signups, remove_message_signup
from views.signup_views import SignupView
from logic.embed_builder import build_signup_embed
import config


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


FAKE_NAMES = [
    "Thorgrim", "Leafhealz", "Shadowzap", "Bonkadin", "Totemlord",
    "Frostzug", "Moonbeef", "Sneakstab", "Pyroblastz", "Soulrot",
    "Mendrina", "Bearjuice", "Shockbot", "Arrowqt", "Smitey",
    "Hexella", "Clawbert", "Shieldbro", "Dotsdot", "Windbonk",
    "Holytoast", "Darkmoo", "Stonepaw", "Critlord", "Glimmer"
]


def build_fake_users() -> dict:
    tanks = [
        ("Death Knight", "Blood", "Tank"),
        ("Warrior", "ProtectionWarrior", "Tank"),
        ("Druid", "Guardian", "Tank"),
        ("Paladin", "ProtectionPaladin", "Tank"),
        ("Monk", "Brewmaster", "Tank"),
    ]

    healers = [
        ("Paladin", "HolyPaladin", "Healer"),
        ("Druid", "RestorationDruid", "Healer"),
        ("Priest", "Discipline", "Healer"),
        ("Priest", "HolyPriest", "Healer"),
        ("Shaman", "RestorationShaman", "Healer"),
        ("Monk", "Mistweaver", "Healer"),
    ]

    dps = [
        ("Warrior", "Arms", "Melee"),
        ("Warrior", "Fury", "Melee"),
        ("Druid", "Balance", "Ranged"),
        ("Druid", "Feral", "Melee"),
        ("Paladin", "Retribution", "Melee"),
        ("Monk", "Windwalker", "Melee"),
        ("Priest", "Shadow", "Ranged"),
        ("Mage", "Arcane", "Ranged"),
        ("Mage", "Fire", "Ranged"),
        ("Mage", "Frost", "Ranged"),
        ("Warlock", "Affliction", "Ranged"),
        ("Warlock", "Demonology", "Ranged"),
        ("Warlock", "Destruction", "Ranged"),
        ("Hunter", "Beast Mastery", "Ranged"),
        ("Hunter", "Marksmanship", "Ranged"),
        ("Hunter", "Survival", "Ranged"),
        ("Rogue", "Assassination", "Melee"),
        ("Rogue", "Combat", "Melee"),
        ("Rogue", "Subtlety", "Melee"),
        ("Shaman", "Elemental", "Ranged"),
        ("Shaman", "Enhancement", "Melee"),
        ("Death Knight", "FrostDK", "Melee"),
        ("Death Knight", "Unholy", "Melee"),
    ]

    tank_count = random.randint(1, 2)
    healer_count = random.randint(2, 3)
    dps_count = random.randint(8, 9)

    selected_tanks = random.sample(tanks, k=tank_count)
    selected_healers = random.sample(healers, k=healer_count)
    selected_dps = random.sample(dps, k=dps_count)

    selected_players = (
        [("sign", p) for p in selected_tanks] +
        [("sign", p) for p in selected_healers] +
        [("sign", p) for p in selected_dps]
    )

    extra_statuses = ["late", "tentative", "absence", "bench"]
    extra_pool = random.sample(dps + healers + tanks, k=4)

    selected_players += list(zip(extra_statuses, extra_pool))

    used_names = random.sample(FAKE_NAMES, k=len(selected_players))

    users = {}
    now = __import__("time").time()

    for i, (status, (player_class, spec, role)) in enumerate(selected_players):
        fake_user_id = f"demo_{i}"
        users[fake_user_id] = {
            "display_name": used_names[i],
            "class": player_class,
            "spec": spec,
            "role": role,
            "status": status,
            "timestamp": now + i,
        }

    return users


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
            "channel_id": ctx.channel.id,
            "users": {},
            "expected_players": [
                str(player_id)
                for player_id in getattr(config, "DEFAULT_EXPECTED_PLAYERS", [])
            ],
            "reminders_sent": {
                "1440": False,  # 24 hours
                "360": False,   # 6 hours
                "120": False,   # 2 hours
                "30": False,    # 30 minutes
            },
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
    async def template(self, ctx: commands.Context):
        start_ts = next_weekday(2, 19, 30)

        signup = {
            "title": "HC Progression - Template Preview",
            "description": "Visual preview with fake raid roster",
            "leader": "Hekkipekki / Rhegaran",
            "start_ts": start_ts,
            "channel_id": ctx.channel.id,
            "users": build_fake_users(),
            "expected_players": [
                str(player_id)
                for player_id in getattr(config, "DEFAULT_EXPECTED_PLAYERS", [])
            ],
            "reminders_sent": {
                "1440": False,
                "360": False,
                "120": False,
                "30": False,
            },
        }

        embed = build_signup_embed(signup["title"], signup["description"], signup)

        message = await ctx.send(embed=embed)
        await message.edit(view=SignupView(str(message.id)))

        data = load_signups()
        data[str(message.id)] = signup
        save_signups(data)

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