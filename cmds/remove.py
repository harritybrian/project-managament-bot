import discord
import TicketSystem
from discord import app_commands, member, utils
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot, has_permissions, MissingPermissions

class Remove(commands.Cog, name = 'remove'):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "remove",  with_app_command = True,description = "Removes user from existing ticket")
    @app_commands.describe(user = "User you want to remove from the ticket")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
      if "ticket-for-" in interaction.channel.name:
        if not interaction.channel.permissions_for(user).send_messages:
            await interaction.interaction.response.send_message(f"{user.mention} has does not exist in the ticket!")
        else:
            await interaction.channel.set_permissions(user, overwrite = None)
            await interaction.interaction.response.send_message(f"{user.mention} has been removed from the ticket!")
      else:
        await interaction.interaction.response.send_message("This can only be used in a ticket channel", ephemeral = True)


async def setup(bot):
    await bot.add_cog(Remove(bot))
