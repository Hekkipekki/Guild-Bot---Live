import time
import discord
from discord.ext import commands, tasks

from data.signup_store import load_signups, save_signups
from logic.unassigned import get_unassigned_players


MISSING_SIGNUP_THRESHOLDS = {
    "2880": "48 hours",
    "1440": "24 hours",
}

SIGNED_PLAYER_THRESHOLDS = {
    "60": "1 hour",
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

            # Skip raids that already started
            if seconds_left <= 0:
                continue

            minutes_left = seconds_left // 60

            channel = self.bot.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except Exception:
                    continue

            missing_reminders_sent = signup.setdefault(
                "missing_signup_reminders_sent",
                {
                    "2880": False,  # 48 hours
                    "1440": False,  # 24 hours
                },
            )

            signed_reminders_sent = signup.setdefault(
                "signed_player_reminders_sent",
                {
                    "60": False,  # 1 hour
                },
            )

            title = signup.get("title", "Raid")

            # --------------------------------------------------
            # 1) Missing signup reminders
            # --------------------------------------------------
            unassigned_players = get_unassigned_players(signup)

            if unassigned_players:
                for threshold_str, label in sorted(
                    MISSING_SIGNUP_THRESHOLDS.items(),
                    key=lambda item: int(item[0])
                ):
                    threshold = int(threshold_str)

                    if (
                        minutes_left <= threshold
                        and not missing_reminders_sent.get(threshold_str, False)
                    ):
                        mentions = "\n".join(f"<@{user_id}>" for user_id in unassigned_players)

                        await channel.send(
                            f"⏰ **Raid reminder — {label} remaining**\n"
                            f"**{title}** starts <t:{start_ts}:R>\n\n"
                            f"Still missing signup from:\n{mentions}"
                        )

                        missing_reminders_sent[threshold_str] = True
                        changed = True
                        break

            # --------------------------------------------------
            # 2) Signed player reminder
            # --------------------------------------------------
            users = signup.get("users", {})
            signed_players = [
                user_id
                for user_id, info in users.items()
                if info.get("status") == "sign"
            ]

            if signed_players:
                for threshold_str, label in sorted(
                    SIGNED_PLAYER_THRESHOLDS.items(),
                    key=lambda item: int(item[0])
                ):
                    threshold = int(threshold_str)

                    if (
                        minutes_left <= threshold
                        and not signed_reminders_sent.get(threshold_str, False)
                    ):
                        mentions = " ".join(f"<@{user_id}>" for user_id in signed_players)

                        await channel.send(
                            f"⏰ **Raid starts in {label}**\n"
                            f"{mentions}\n\n"
                            f"**{title}** starts <t:{start_ts}:R>\n"
                            f"Don't forget to check your bonus rolls, consumables, and your gear before raid starts — we don't want to lose any time."
                        )

                        signed_reminders_sent[threshold_str] = True
                        changed = True
                        break

        if changed:
            save_signups(data)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))