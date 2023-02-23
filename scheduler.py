import discord
from discord.utils import get
from discord.ext import commands


client = discord.Client(intents = discord.Intents.all())


class Scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = 'schedule', with_app_command = True, description = "A test scheduler.")
    async def schedule1(self, msg):
        signup = discord.Embed()
        signup.title = "Users added title!"
        signup.add_field(name="✅Signups:", value="", inline=True)
        signup.add_field(name="❌Absences:", value="", inline=True)
        msg = await msg.send(embed = signup)

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

        if payload.member.bot:
            return

        dict_embed = embed.to_dict()

        for field in dict_embed["fields"]:
            if str(emoji) == "✅":
                if field["name"] == "✅Signups:":
                    field["value"] += f'\n{user}'
                embed = discord.Embed.from_dict(dict_embed)
                await message.edit(embed=embed)

            elif str(emoji) == "❌":
                if field["name"] == "❌Absences:":
                    field["value"] += f'\n{user}'
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

        dict_embed = embed.to_dict()

        for field in dict_embed["fields"]:
            if str(emoji) == "✅":
                if field["name"] == "✅Signups:":
                    newval = ""
                    val = field["value"]
                    vallines = val.splitlines(False)
                    for lines in vallines:
                        if not lines.__contains__(str(user)):
                            newval += lines
                    field["value"] = newval

            if str(emoji) == "❌":
                if field["name"] == "❌Absences:":
                    newval = ""
                    val = field["value"]
                    vallines = val.splitlines(False)
                    for lines in vallines:
                        if not lines.__contains__(str(user)):
                            newval += lines
                    field["value"] = newval

            embed = discord.Embed.from_dict(dict_embed)
            await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
