import discord
from discord.utils import get
from discord.ext import commands

client = discord.Client(intents = discord.Intents.all())

class Ping(commands.Cog, name = 'ping'):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "ping",  with_app_command = True,description = "Checking latency")
    async def ping(self, message):
        await message.send('Pong! Took {0} ms'.format(round(self.bot.latency, 1)))


async def setup(bot):
    await bot.add_cog(Ping(bot))