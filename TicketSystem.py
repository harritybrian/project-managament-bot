import discord
import datetime
import pytz
import os
from discord import app_commands, member, utils
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot, has_permissions, MissingPermissions

class ticket_launcher(discord.ui.View):
  def __init__(slef) -> None:
    super().__init__(timeout = None)

  @discord.ui.button(label = "Create a Ticket",
                     style = discord.ButtonStyle.blurple,
                     custom_id = "ticket_button")
  async def ticket(self, interaction: discord.Interaction,
                   button: discord.ui.Button):

    # check if ticket exists already
    ticket = utils.get(interaction.guild.text_channels,
                       name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}")
    if ticket is not None:
      await interaction.response.send_message(f"You already have a ticket open at {ticket.mention}!", ephemeral = True)

    else:
      # permission overwrites for ticket channel
      overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
        interaction.user: discord.PermissionOverwrite(view_channel = True,
                                                      send_messages = True,
                                                      attach_files = True,
                                                      embed_links = True,
                                                      read_message_history = True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel = True,
                                                           send_messages = True,
                                                           read_message_history = True)
      }
      
      # create ticket channel
      category = discord.utils.get(interaction.guild.categories, name = "Tickets")
      if category is None:
        await interaction.guild.create_category("TICKETS", position = 0)
      channel = await interaction.guild.create_text_channel(name = f"ticket-for-{interaction.user.name}-{interaction.user.discriminator}",
                                                            category = category, overwrites = overwrites, reason = f"Ticket for {interaction.user}")
      await channel.send(f"{interaction.user.mention} created a ticket!", view = ticket_control())
      await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}!", ephemeral = True)

# ticket deletion confirmation button
class confirm(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout = None)

  @discord.ui.button(label = "Yes, I'm sure", style = discord.ButtonStyle.red, custom_id = "confirm")
  async def confirm_button(self, interaction, button):
    try:
      await interaction.channel.delete()
    except:
      await interaction.response.send_message("Channel could not be deleted, ensure 'manage_channels' permission is given!",
                                              ephemeral = True)
# ticket management
class ticket_control(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout = None)

  # close ticket embed
  @discord.ui.button(label = "Close this Ticket", style = discord.ButtonStyle.red, custom_id = "close")
  async def close(self, interaction, button):
    embed = discord.Embed(title = "Are you sure you want to close this ticket?", color = discord.Colour.brand_red())
    await interaction.response.send_message(embed = embed, view = confirm(), ephemeral = True)
