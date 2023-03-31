import discord
from CONFIG import token, CMDS_DIR
import datetime
import pytz
import os
import pathlib
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot
from TicketSystem import ticket_control, ticket_launcher

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
mst_format= mst_now.strftime("%Y/%m/%d %H:%M:%S")

TOKEN = token

class aclient(commands.Bot):

  # sync slash commands
  def __init__(self):
    super().__init__(command_prefix='!', intents = discord.Intents.all())
    self.synced = False
    self.added = False
    
  # check if slash commands synced
  async def on_ready(self):
    await self.wait_until_ready()

    # make ticket button persist over restarts  
    if not self.added:
      self.add_view(ticket_launcher())
      self.add_view(ticket_control())
      self.added = True

    # print ready message and set bot status  
    await bot.change_presence(activity=discord.Game('TICKET SYSTEM'))
    print(f'Bot connected as {bot.user}')
    print(mst_format)
    for cmd_file in CMDS_DIR.glob('*.py'):
      if cmd_file.name != '__BotTemplate__.py':
        await bot.load_extension(f'cmds.{cmd_file.name[:-3]}')

    if not self.synced:
      await bot.tree.sync()
      self.synced = True

bot = aclient()

@bot.tree.command(name = 'help', description = 'Help Command')
async def help(interaction: discord.Interaction):
  embed = discord.Embed(title="DPBs Help", description="Help command for the discord productivity bot")
  treeCommands = await bot.tree.fetch_commands()
  for command in treeCommands:
    description = command.description
    if not description or description is None or description =="":
      description = "No description found/provided"
    embed.add_field(name=f"`/{command.name}`", value=description)
  await interaction.response.send_message(embed=embed)

bot.run(TOKEN)