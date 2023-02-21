import discord
from discord.utils import get
from discord.ext import commands


client = discord.Client(intents = discord.Intents.all())

class Scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = 'schedule', with_app_command = True, description = "A test scheduler.")
    async def schedule1(self, msg):
        msg = await msg.send("React below to sign up!")
        emojis = ['\U00002705','\U0000274C']
        for emoji in emojis:
            await msg.add_reaction(emoji)


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
