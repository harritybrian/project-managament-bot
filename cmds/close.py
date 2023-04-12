import discord
import TicketSystem
from discord import app_commands, member, utils
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot, has_permissions, MissingPermissions

client = discord.Client(intents = discord.Intents.all())

class Close(commands.Cog, name = 'close'):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "close",  with_app_command = True,description = "Close a ticket manually")
    async def close(self, interaction: discord.Interaction):
      if "ticket-for-" in interaction.channel.name:
        embed = discord.Embed(title = "Are you sure you want to close this ticket?", color = discord.Colour.brand_red())
        await interaction.interaction.response.send_message(embed = embed, view = TicketSystem.confirm(), ephemeral = True)
      else:
        await interaction.interaction.response.send_message("This can only be used in a ticket channel", ephemeral = True)


async def setup(bot):
    await bot.add_cog(Close(bot))

