import time
import discord
from discord.ext import commands, tasks

from data.signup_store import load_signups, save_signups
from logic.unassigned import get_unassigned_players


REMINDER_THRESHOLDS = {
    "1440": "24 hours",
    "360": "6 hours",
    "120": "2 hours",
    "30": "30 minutes",
}


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        data = load_signups()
        now = int(time.time())
        changed = False

        for raid_id, signup in data.items():
            start_ts = signup.get("start_ts")
            channel_id = signup.get("channel_id")

            if not start_ts or not channel_id:
                continue

            seconds_left = start_ts - now

            # Skip past raids
            if seconds_left <= 0:
                continue

            minutes_left = seconds_left // 60

            reminders_sent = signup.setdefault(
                "reminders_sent",
                {"1440": False, "360": False, "120": False, "30": False},
            )

            unassigned_players = get_unassigned_players(signup)
            if not unassigned_players:
                continue

            for threshold_str, label in REMINDER_THRESHOLDS.items():
                threshold = int(threshold_str)

                if minutes_left <= threshold and not reminders_sent.get(threshold_str, False):
                    channel = self.bot.get_channel(channel_id)
                    if channel is None:
                        try:
                            channel = await self.bot.fetch_channel(channel_id)
                        except Exception:
                            continue

                    mentions = "\n".join(f"<@{user_id}>" for user_id in unassigned_players)

                    title = signup.get("title", "Raid")
                    await channel.send(
                        f"⏰ **Raid reminder — {label} remaining**\n"
                        f"**{title}** starts <t:{start_ts}:R>\n\n"
                        f"Still missing signup from:\n{mentions}"
                    )

                    reminders_sent[threshold_str] = True
                    changed = True

        if changed:
            save_signups(data)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))