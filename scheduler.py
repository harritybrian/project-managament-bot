import discord
from discord.utils import get
from discord.ext import commands
import datetime
import pytz

client = discord.Client(intents = discord.Intents.all())

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
mst_format= mst_now.strftime("%Y/%m/%d")
hour_format = mst_now.strftime("%H:%M:%S")

class Scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = 'event', with_app_command = True)
    async def event(self, ctx):
        await ctx.guild.create_scheduled_event(name="test", start_time=time, end_time=time)

    @commands.hybrid_command(name = 'schedule', with_app_command = True, description = "A test scheduler.")
    async def schedule1(self, ctx, *, title, description, leader: discord.User):
        signup = discord.Embed()

        #signup.set_author(name=f'Created by {ctx.author.display_name}')
        signup.title = title
        signup.description = description
        signup.set_footer(text="\U0001F916 Bot by C&C")
        #signup.set_image(url=ctx.message.attachments[0].url)
        signup.add_field(name=f'\U0001F4C5 {time.strftime(mst_format)}', value="", inline=True)
        signup.add_field(name=f'\U0000231A {time.strftime(hour_format)}', value="", inline=True)
        signup.add_field(name="\U0001F465 Attending:", value=0, inline=True)
        signup.add_field(name="\U0001F5E3 Leaders:", value=leader.display_name, inline=True)
        signup.add_field(name="✅Signups:", value="", inline=True)
        signup.add_field(name="❌Absences:", value="", inline=True)
        msg = await ctx.send(embed = signup)

        emojis = ['\U00002705','\U0000274C']
        for emoji in emojis:
            await msg.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji
        embed = message.embeds[0]
        reaction = get(message.reactions, emoji='✅')

        if payload.member.bot:
            return

        dict_embed = embed.to_dict()

        for field in dict_embed["fields"]:
            if str(emoji) == "✅":
                if field["name"] == "✅Signups:":
                    field["value"] += f'\n{payload.member.nick}'
                embed = discord.Embed.from_dict(dict_embed)
                embed.set_field_at(2, name=f'\U0001F465 Attending: {reaction.count}', value="")
                await message.edit(embed=embed)

            elif str(emoji) == "❌":
                if field["name"] == "❌Absences:":
                    field["value"] += f'\n{payload.member.nick}'
                embed = discord.Embed.from_dict(dict_embed)
                await message.edit(embed=embed)

            else:
                await channel.send(f'Unknown reaction!')



    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji
        embed = message.embeds[0]
        reaction = get(message.reactions, emoji='✅')

        dict_embed = embed.to_dict()

        for field in dict_embed["fields"]:
            if str(emoji) == "✅":
                if field["name"] == "✅Signups:":
                    newval = ""
                    val = field["value"]
                    vallines = val.splitlines(False)
                    for lines in vallines:
                        if not lines.__contains__(str(payload.member.nick)):
                            newval += lines
                    field["value"] = newval

            if str(emoji) == "❌":
                if field["name"] == "❌Absences:":
                    newval = ""
                    val = field["value"]
                    vallines = val.splitlines(False)
                    for lines in vallines:
                        if not lines.__contains__(str(payload.member.nick)):
                            newval += lines
                    field["value"] = newval

            embed.set_field_at(2, name=f'\U0001F465 Attending: {reaction.count}', value="")
            embed = discord.Embed.from_dict(dict_embed)
            await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
