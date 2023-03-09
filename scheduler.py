import discord
from discord import app_commands
from discord.ext import commands
import datetime
import pytz

client = discord.Client(intents=discord.Intents.all())

time = datetime.datetime.now()
mst_now = time.astimezone(pytz.timezone('America/Denver'))
date_format = mst_now.strftime("%Y/%m/%d")
hour_format = mst_now.strftime("%H:%M:%S")


class Scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(self.NewView(self))

    perms = ""
    signups = []
    absences = []
    tentative = []

    async def check_role(self, interaction):
        if self.perms not in interaction.user.roles:
            await interaction.response.send_message("You do not have the role. Cannot sign up!", ephemeral=True,
                                                    delete_after=2)
            return False
        else:
            return True

    def swap(self, option, user):
        if self.signups.__contains__(user) and option != 1:
            self.signups.remove(user)
        elif self.absences.__contains__(user) and option != 2:
            self.absences.remove(user)
        elif self.tentative.__contains__(user) and option != 3:
            self.tentative.remove(user)
        return

    def update_embed(self, embed: discord.Embed):

        dict_embed = embed.to_dict()

        for field in dict_embed["fields"]:
            if field["name"] == "✅Signups:":
                newstr = ""
                for x in self.signups:
                    newstr += '\n' + x.display_name
                field["value"] = newstr

        for field in dict_embed["fields"]:
            if field["name"] == "❌Absences:":
                newstr = ""
                for x in self.absences:
                    newstr += '\n' + x.display_name
                field["value"] = newstr

        for field in dict_embed["fields"]:
            if field["name"] == "⚖Tentative:":
                newstr = ""
                for x in self.tentative:
                    newstr += '\n' + x.display_name
                field["value"] = newstr

        embed = discord.Embed.from_dict(dict_embed)
        embed.set_field_at(2, name=f'\U0001F465 Attending: {len(self.signups)}', value="")
        return embed

    @commands.hybrid_command(name='event', with_app_command=True)
    async def event(self, ctx):
        await ctx.guild.create_scheduled_event(name="test", start_time=time, end_time=time)

    @commands.hybrid_command(name='schedule', with_app_command=True, description="A test scheduler.",
                             brief="Brief example.", usage="Usage example.")
    @app_commands.describe(title='Enter a title for the event.', description='Enter a description for the event.',
                           leader='Choose a user as the event leader.', role='Choose which roles can sign up for the event.',
                           time='Enter time in the format: Y-M-D H:M AM/PM')
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
        view = self.NewView(self)

        date = datetime.datetime.strptime(time, '%Y-%m-%d %I:%M %p')
        signup.set_author(name=f'Created by {ctx.author.display_name}')
        signup.title = title
        signup.description = description
        signup.set_footer(text="\U0001F916 Bot by C&C")
        # signup.set_image(url=ctx.message.attachments[0].url)
        signup.add_field(name=f'\U0001F4C5 ' + date.strftime("%Y-%m-%d"), value="", inline=True)
        signup.add_field(name=f'\U0000231A ' + date.strftime("%I:%M %p"), value="", inline=True)
        signup.add_field(name="\U0001F465 Attending:", value=0, inline=True)
        if leader is not None:
            signup.add_field(name="\U0001F5E3 Leaders:", value=leader.display_name, inline=True)
        else:
            signup.add_field(name="\U0001F5E3 Leaders:", value="None", inline=True)
        signup.add_field(name="✅Signups:", value="", inline=True)
        signup.add_field(name="❌Absences:", value="", inline=True)
        signup.add_field(name="⚖Tentative:", value="", inline=True)
        await ctx.send(embed = signup, view=view)

    class NewView(discord.ui.View):
        def __init__(self, scheduler):
            super().__init__(timeout=None)
            self.scheduler = scheduler

        @discord.ui.button(label="Sign up", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_1',
                           emoji="✅")
        async def button_signup(self, interaction: discord.Interaction, button: discord.ui.Button):

            if not await self.scheduler.check_role(interaction):
                return
            self.scheduler.swap(1, interaction.user)

            self.scheduler.signups.append(interaction.user)

            await interaction.message.edit(embed=self.scheduler.update_embed(interaction.message.embeds[0]))
            await interaction.response.defer()

        @discord.ui.button(label="Absent", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_2',
                           emoji="❌")
        async def button_absent(self, interaction: discord.Interaction, button: discord.ui.Button):

            if not await self.scheduler.check_role(interaction):
                return
            self.scheduler.swap(2, interaction.user)

            self.scheduler.absences.append(interaction.user)

            await interaction.message.edit(embed=self.scheduler.update_embed(interaction.message.embeds[0]))
            await interaction.response.defer()

        @discord.ui.button(label="Tentative", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_3',
                           emoji="⚖")
        async def button_tentative(self, interaction: discord.Interaction, button: discord.ui.Button):

            if not await self.scheduler.check_role(interaction):
                return
            self.scheduler.swap(3, interaction.user)

            self.scheduler.tentative.append(interaction.user)

            await interaction.message.edit(embed=self.scheduler.update_embed(interaction.message.embeds[0]))
            await interaction.response.defer()

        @discord.ui.button(label="Remove Sign Up", row=1, style=discord.ButtonStyle.danger,
                           custom_id='persistent_view_4')
        async def button_remove(self, interaction: discord.Interaction, button: discord.ui.Button):

            if not await self.scheduler.check_role(interaction):
                return
            self.scheduler.swap(0, interaction.user)

            await interaction.message.edit(embed=self.scheduler.update_embed(interaction.message.embeds[0]))
            await interaction.response.defer()


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
