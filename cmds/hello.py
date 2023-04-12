import discord
from discord.utils import get
from discord.ext import commands

client = discord.Client(intents = discord.Intents.all())

class Hello(commands.Cog, name = 'hello'):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = 'hello', with_app_command = True, description = "A welcoming message!")
    async def hello(self, message):
        await message.send(f'Hello {message.author.display_name}!')


async def setup(bot):
    await bot.add_cog(Hello(bot))