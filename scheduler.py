import discord
from discord import app_commands
from discord.utils import get
from discord.ext import commands
import datetime
import pytz
from discord.components import *

# from discord.ui import Button, View

client = discord.Client(intents=discord.Intents.all())

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
mst_format = mst_now.strftime("%Y/%m/%d")
hour_format = mst_now.strftime("%H:%M:%S")


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sign up!", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_1',
                       emoji="✅")
    async def button_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message("You clicked the button!", ephemeral=True)
        embed = interaction.message.embeds[0]

        Scheduler.signups.append(interaction.user)

    @discord.ui.button(label="Absent!", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_2',
                       emoji="❌")
    async def button_absent(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)

    @discord.ui.button(label="Tentative!", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_3',
                       emoji="⚖")
    async def button_tentative(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)

    @discord.ui.button(label="Remove Sign Up!", row=1, style=discord.ButtonStyle.secondary,
                       custom_id='persistent_view_4',
                       emoji="❌")
    async def button_remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)


class Scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(MyView())

    perms = ""
    signups = []
    absences = []

    @commands.hybrid_command(name='event', with_app_command=True)
    async def event(self, ctx):
        await ctx.guild.create_scheduled_event(name="test", start_time=time, end_time=time)


    @commands.hybrid_command(name='schedule', with_app_command=True, description="A test scheduler.",
                             brief="Brief example.", usage="Usage example.")
    @app_commands.describe(title='Enter a title for the event.', description='Enter a description for the event.',
                           leader='Choose a user as the event leader.', role='Choose which roles can sign up for the event.',
                           time='Enter time in the format: Y-M-D H-M-AM/PM')
    async def scheduler(self, ctx, *, time: str = commands.parameter(description="Enter as Y-M-D Hour-Minute-AM/PM"),
                        title: str = commands.parameter(default="Default title.",
                                                        description='Title of the event.', displayed_default='Displayed default'),
                        description: str = commands.parameter(default="Default description.",
                                                              description="Desc of the event."),
                        leader: discord.User = None, role: discord.Role = None):

        if role is None:
            self.perms = ctx.guild.default_role
        else:
            self.perms = role

        signup = discord.Embed()
        view = MyView()

        # signup.set_author(name=f'Created by {ctx.author.display_name}')
        signup.title = title
        signup.description = description
        signup.set_footer(text="\U0001F916 Bot by C&C")
        # signup.set_image(url=ctx.message.attachments[0].url)
        signup.add_field(name=f'\U0001F4C5 ', value="", inline=True)
        signup.add_field(name=f'\U0000231A ', value="", inline=True)
        signup.add_field(name="\U0001F465 Attending:", value=0, inline=True)
        if leader is not None:
            signup.add_field(name="\U0001F5E3 Leaders:", value=leader.display_name, inline=True)
        else:
            signup.add_field(name="\U0001F5E3 Leaders:", value="None", inline=True)
        signup.add_field(name="✅Signups:", value="", inline=True)
        signup.add_field(name="❌Absences:", value="", inline=True)
        await ctx.send(view=TimeView(), ephemeral=True)
        await ctx.send(embed = signup, view=view)

        '''
        emojis = ['\U00002705','\U0000274C']
        for emoji in emojis:
            await msg.add_reaction(emoji)'''

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        guild = client.get_guild(payload.guild_id)
        emoji = payload.emoji
        embed = message.embeds[0]
        reaction = get(message.reactions, emoji='✅')
        perms = self.perms
        roles = get(payload.member.roles)

        if payload.member.bot:
            return

        if perms not in payload.member.roles:
            await channel.send("You do not have the role. Cannot sign up!")
            return

        dict_embed = embed.to_dict()

        for field in dict_embed["fields"]:
            if str(emoji) == "✅":
                if field["name"] == "✅Signups:":
                    self.signups.append(payload.member)
                    newstr = ""
                    for x in self.signups:
                        newstr += '\n' + x.display_name
                    field["value"] = newstr

            elif str(emoji) == "❌":
                if field["name"] == "❌Absences:":
                    self.absences.append(payload.member)
                    newstr = ""
                    for x in self.absences:
                        newstr += '\n' + x.display_name
                    field["value"] = newstr
                    embed = discord.Embed.from_dict(dict_embed)
                    await message.edit(embed=embed)

            else:
                await channel.send(f'Unknown reaction!')

        embed = discord.Embed.from_dict(dict_embed)
        embed.set_field_at(2, name=f'\U0001F465 Attending: {reaction.count}', value="")
        await message.edit(embed=embed)

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
                    if self.signups.__contains__(user):
                        self.signups.remove(user)
                    if len(self.signups):
                        for x in self.signups:
                            newstr = '\n' + x.display_name
                    else:
                        newstr = ""

                    field["value"] = newstr

            if str(emoji) == "❌":
                if field["name"] == "❌Absences:":
                    if self.absences.__contains__(user):
                        self.absences.remove(user)
                    if len(self.absences):
                        for x in self.absences:
                            newstr = '\n' + x.display_name
                    else:
                        newstr = ""

                    field["value"] = newstr

        embed.set_field_at(2, name=f'\U0001F465 Attending: {reaction.count}', value="")
        embed = discord.Embed.from_dict(dict_embed)
        await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
