import time
import discord
from discord.ext import commands, tasks

from data.signup_store import load_signups, save_signups
from services.reminder_service import (
    ensure_missing_signup_reminder_state,
    ensure_signed_player_reminder_state,
    get_signup_title,
    get_missing_players,
    get_signed_players,
    find_missing_signup_threshold_to_send,
    find_signed_player_threshold_to_send,
    build_missing_signup_reminder_message,
    build_signed_player_reminder_message,
)


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
            if seconds_left <= 0:
                continue

            minutes_left = seconds_left // 60

            channel = self.bot.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except Exception:
                    continue

            missing_reminders_sent = ensure_missing_signup_reminder_state(signup)
            signed_reminders_sent = ensure_signed_player_reminder_state(signup)
            title = get_signup_title(signup)

            # 1) Missing signup reminders
            missing_players = get_missing_players(signup)
            if missing_players:
                threshold_info = find_missing_signup_threshold_to_send(
                    minutes_left,
                    missing_reminders_sent,
                )

                if threshold_info:
                    threshold_str, label = threshold_info

                    await channel.send(
                        build_missing_signup_reminder_message(
                            title=title,
                            label=label,
                            start_ts=start_ts,
                            user_ids=missing_players,
                        )
                    )

                    missing_reminders_sent[threshold_str] = True
                    changed = True

            # 2) Signed player reminder
            signed_players = get_signed_players(signup)
            if signed_players:
                threshold_info = find_signed_player_threshold_to_send(
                    minutes_left,
                    signed_reminders_sent,
                )

                if threshold_info:
                    threshold_str, label = threshold_info

                    await channel.send(
                        build_signed_player_reminder_message(
                            title=title,
                            label=label,
                            start_ts=start_ts,
                            user_ids=signed_players,
                        )
                    )

                    signed_reminders_sent[threshold_str] = True
                    changed = True

        if changed:
            save_signups(data)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))