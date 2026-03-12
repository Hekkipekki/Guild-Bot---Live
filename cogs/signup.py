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

    async def _delete_command_message(self, ctx: commands.Context) -> None:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        except discord.NotFound:
            pass

    async def _send_temporary_confirmation(
        self,
        ctx: commands.Context,
        content: str,
        *,
        delete_after: int = 5,
    ) -> None:
        msg = await ctx.send(content)
        try:
            await msg.delete(delay=delete_after)
        except (discord.Forbidden, discord.NotFound):
            pass

    async def _post_signup(self, ctx: commands.Context, signup: dict) -> None:
        await self._delete_command_message(ctx)

        ok = await send_signup_message(ctx, signup)
        if not ok:
            await self._send_temporary_confirmation(
                ctx,
                "⚠ Failed to create signup message.",
            )

    async def _delete_linked_comp_message(
        self,
        channel: discord.abc.Messageable,
        signup: dict,
    ) -> bool:
        comp_message_id = signup.get("comp_message_id")
        if not comp_message_id:
            return False

        try:
            comp_message = await channel.fetch_message(comp_message_id)
            await comp_message.delete()
            return True
        except (discord.NotFound, discord.Forbidden):
            return False
        except Exception:
            return False

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: commands.Context):
        await self._delete_command_message(ctx)

        data = load_signups()
        deleted_messages = await ctx.channel.purge(limit=1000)

        removed_signups = 0
        deleted_comp_messages = 0

        for message in deleted_messages:
            signup = data.get(str(message.id))

            if signup:
                comp_deleted = await self._delete_linked_comp_message(ctx.channel, signup)
                if comp_deleted:
                    deleted_comp_messages += 1

            if remove_message_signup(data, message.id, save=False):
                removed_signups += 1

        if removed_signups:
            save_signups(data)

        await self._send_temporary_confirmation(
            ctx,
            f"💣 Deleted {len(deleted_messages)} messages. "
            f"Removed {removed_signups} signup entries from JSON. "
            f"Deleted {deleted_comp_messages} linked comp message(s).",
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def wedsignup(self, ctx: commands.Context):
        signup = build_wednesday_signup(ctx.channel.id)
        await self._post_signup(ctx, signup)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def template(self, ctx: commands.Context):
        signup = build_template_signup(ctx.channel.id)
        await self._post_signup(ctx, signup)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sunsignup(self, ctx: commands.Context):
        signup = build_sunday_signup(ctx.channel.id)
        await self._post_signup(ctx, signup)


async def setup(bot):
    await bot.add_cog(SignupCommands(bot))