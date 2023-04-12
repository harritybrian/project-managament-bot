import discord
import TicketSystem
from discord import app_commands, member, utils
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot, has_permissions, MissingPermissions

client = discord.Client(intents = discord.Intents.all())

class Add(commands.Cog, name = 'add'):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "add",  with_app_command = True,description = "Adds user to existing ticket")
    @app_commands.describe(user = "User you want to add to the ticket")
    async def add(self, interaction: discord.Interaction, user: discord.Member):
      if "ticket-for-" in interaction.channel.name:
        
        if  interaction.channel.permissions_for(user).send_messages:
            await interaction.interaction.response.send_message(f"{user.mention} is already added to the ticket!")

        else:
            await interaction.channel.set_permissions(user, view_channel = True, send_messages = True,
                                                  attach_files = True, embed_links = True)
            await interaction.interaction.response.send_message(f"{user.mention} has been added to the ticket!")
      else:
        await interaction.interaction.response.send_message("This can only be used in a ticket channel", ephemeral = True)


async def setup(bot):
    await bot.add_cog(Add(bot))

