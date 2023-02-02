import discord
import datetime
import pytz
import os
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
mst_format= mst_now.strftime("%Y/%m/%d %H:%M:%S")

intents = discord.Intents.all()
bot = Bot(command_prefix='.', intents = intents)
TOKEN = '[token here]'

@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game('ALL SYSTEMS GREEN'))
  print(f'Bot connected as {bot.user}')
  print(mst_format)

bot.run(TOKEN)
