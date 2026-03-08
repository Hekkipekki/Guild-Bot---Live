from discord.ext import commands
import config
from views.raidpack_views import RaidPackView


class WACommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tot(self, ctx: commands.Context):
        channel = self.bot.get_channel(config.WEAKAURAS_CHANNEL_ID)
        if channel is None:
            await ctx.send("❌ Could not find #weakauras channel.")
            return

        await channel.send(
            "**Click the buttons below to download the Raid Pack WAs**\n"
            'Click *"Dismiss this message"* if it shows an old version, then re-click the button.',
            view=RaidPackView(),
        )


async def setup(bot):
    await bot.add_cog(WACommands(bot))