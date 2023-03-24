import discord
from discord import app_commands
from discord.ext import commands
import datetime
import pytz
import sqlite3

client = discord.Client(intents=discord.Intents.all())

timenow = datetime.datetime.now()
mst_now = timenow.astimezone(pytz.timezone('America/Denver'))
timezone = pytz.timezone('America/Denver')
date_format = mst_now.strftime("%Y/%m/%d")
hour_format = mst_now.strftime("%H:%M:%S")

#async def startup():


class Scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(self.NewView(self))
        print('Scheduler initialized!')

    db = sqlite3.connect("schedules.db")
    dba = db.cursor()

    perms = ""
    signups = []
    absences = []
    tentative = []
    msg_id = ""

    async def get_user(self, id):
        x = await self.bot.fetch_user(id)
        x = x.display_name
        return x

    async def setup_hook(self) -> None:
        self.bot.add_view(self.NewView(self))

    async def check_role(self, interaction):
        if self.perms not in interaction.user.roles:
            await interaction.response.send_message("You do not have the role. Cannot sign up!", ephemeral=True,
                                                    delete_after=2)
            return False
        else:
            return True

    async def swap(self, option, interaction):
        user_id = interaction.user.id
        user = interaction.user
        msg_id = interaction.message.id

        if option == 1:
            self.dba.execute("SELECT ? FROM signups_list WHERE message_id = ?", (user_id, msg_id))
            data = self.dba.fetchone()
        elif option == 2:
            self.dba.execute("SELECT ? FROM absent_list WHERE message_id = ?", (user_id, msg_id))
            data = self.dba.fetchone()
        elif option == 3:
            self.dba.execute("SELECT ? FROM tentative_list WHERE message_id = ?", (user_id, msg_id))
            data = self.dba.fetchone()

        if data is not None:
            return

        if option != 1:
            self.dba.execute('DELETE FROM signups_list WHERE (message_id = ? AND user_id = ?)', (msg_id, user_id))
        if option != 2:
            self.dba.execute('DELETE FROM absent_list WHERE (message_id = ? AND user_id = ?)', (msg_id, user_id))
        if option != 3:
            self.dba.execute('DELETE FROM tentative_list WHERE (message_id = ? AND user_id = ?)', (msg_id, user_id))

        if option == 1:
            self.dba.execute('INSERT INTO signups_list(message_id, user_id) VALUES(?, ?)', (msg_id, user_id))
        elif option == 2:
            self.dba.execute('INSERT INTO absent_list(message_id, user_id) VALUES(?, ?)', (msg_id, user_id))
        elif option == 3:
            self.dba.execute('INSERT INTO tentative_list(message_id, user_id) VALUES(?, ?)', (msg_id, user_id))

        self.db.commit()
        return

    async def update_embed(self, embed: discord.Embed, interaction):
        msg_id = interaction.message.id

        dict_embed = embed.to_dict()
        signups = []
        absent = []
        tentative = []
        self.dba.execute('SELECT user_id FROM signups_list WHERE message_id = ?', (msg_id,))
        lista = self.dba.fetchall()
        for a in lista:
            signups += a
        self.dba.execute('SELECT user_id FROM absent_list WHERE message_id = ?', (msg_id,))
        listb = self.dba.fetchall()
        for b in listb:
            absent += b
        self.dba.execute('SELECT user_id FROM tentative_list WHERE message_id = ?', (msg_id,))
        listc = self.dba.fetchall()
        for c in listc:
            tentative += c

        for field in dict_embed["fields"]:
            if field["name"] == "✅Signups:":
                newstr = ""
                for x in signups:
                    y = await interaction.guild.fetch_member(x)
                    newstr += '\n' + str(y.nick)
                field["value"] = newstr

        for field in dict_embed["fields"]:
            if field["name"] == "❌Absences:":
                newstr = ""
                for x in absent:
                    y = await interaction.guild.fetch_member(x)
                    newstr += '\n' + str(y.nick)
                field["value"] = newstr

        for field in dict_embed["fields"]:
            if field["name"] == "⚖Tentative:":
                newstr = ""
                for x in tentative:
                    y = await interaction.guild.fetch_member(x)
                    newstr += '\n' + str(y.nick)
                field["value"] = newstr

        embed = discord.Embed.from_dict(dict_embed)
        embed.set_field_at(2, name=f'\U0001F465 Attending: {len(lista)}', value="")
        return embed

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

        date = datetime.datetime.strptime(time, '%Y-%m-%d %I:%M %p')
        date1 = timezone.localize(date, is_dst=None)

        signup = discord.Embed(timestamp=date)
        view = self.NewView(self)

        signup.set_author(name=f'Created by {ctx.author.display_name}')
        signup.title = title
        signup.description = description
        signup.set_footer(text="\U0001F916 Bot by C&C")
        # signup.set_image(url=ctx.message.attachments[0].url)
        signup.add_field(name=f'\U0001F4C5 ' + date.strftime("%Y-%m-%d"), value="", inline=True)
        signup.add_field(name=f'\U0000231A ' + date.strftime("%I:%M %p"), value="", inline=True)
        signup.add_field(name="\U0001F465 Attending:", value=0, inline=True)
       # if leader is not None:
           # signup.add_field(name="\U0001F5E3 Leaders:", value=leader.display_name, inline=True)
        #else:
            #signup.add_field(name="\U0001F5E3 Leaders:", value="None", inline=True)
        signup.add_field(name="✅Signups:", value="", inline=True)
        signup.add_field(name="❌Absences:", value="", inline=True)
        signup.add_field(name="⚖Tentative:", value="", inline=True)
        embed = await ctx.send(embed=signup, view=view)
        self.msg_id = embed.id
        self.dba.execute('INSERT INTO schedules_list(message_id, time) VALUES(?, ?)', (str(self.msg_id), time))
        print('Initial insert')
        self.db.commit()

        guild = ctx.guild
        #await discord.Guild.create_scheduled_event(guild, name=title, start_time=date1,
        #                                           description=description, channel=ctx.guild.voice_channels[0],)

    class BlankView(discord.ui.View):
        def __init__(self, scheduler):
            super().__init__(timeout=None)
            self.scheduler = scheduler

        @discord.ui.button(label="The event has already passed.", style=discord.ButtonStyle.secondary, custom_id='blank',
                           disabled=True)
        async def blank_button(self):
            return

    class NewView(discord.ui.View):
        def __init__(self, scheduler):
            super().__init__(timeout=None)
            self.scheduler = scheduler

        @discord.ui.button(label="Sign up", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_1',
                           emoji="✅")
        async def button_signup(self, interaction: discord.Interaction, button: discord.ui.Button):

            #if not await self.scheduler.check_role(interaction):
                #return

            await self.scheduler.swap(1, interaction)

            #self.scheduler.signups.append(interaction.user)

            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))
            await interaction.response.defer()

        @discord.ui.button(label="Absent", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_2',
                           emoji="❌")
        async def button_absent(self, interaction: discord.Interaction, button: discord.ui.Button):

            #if not await self.scheduler.check_role(interaction):
                #return
            await self.scheduler.swap(2, interaction)

            #self.scheduler.absences.append(interaction.user)

            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))
            await interaction.response.defer()

        @discord.ui.button(label="Tentative", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_3',
                           emoji="⚖")
        async def button_tentative(self, interaction: discord.Interaction, button: discord.ui.Button):

            #if not await self.scheduler.check_role(interaction):
               #return
            await self.scheduler.swap(3, interaction)

            #self.scheduler.tentative.append(interaction.user)

            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))
            await interaction.response.defer()

        @discord.ui.button(label="Remove Sign Up", row=1, style=discord.ButtonStyle.danger,
                           custom_id='persistent_view_4')
        async def button_remove(self, interaction: discord.Interaction, button: discord.ui.Button):

            #if not await self.scheduler.check_role(interaction):
                #return
            # self.scheduler.swap(0, interaction.user)

            self.scheduler.dba.execute('DELETE FROM signups_list WHERE (message_id = ? AND user_id = ?)',
                                       (interaction.message.id, interaction.user.id))
            self.scheduler.dba.execute('DELETE FROM absent_list WHERE (message_id = ? AND user_id = ?)',
                                       (interaction.message.id, interaction.user.id))
            self.scheduler.dba.execute('DELETE FROM tentative_list WHERE (message_id = ? AND user_id = ?)',
                                       (interaction.message.id, interaction.user.id))
            self.scheduler.db.commit()

            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))
            await interaction.response.defer()

        @discord.ui.button(label="Delete Event", row=1, style=discord.ButtonStyle.danger,
                           custom_id='persistent_view_5')
        async def button_delete(self, interaction: discord.Interaction, button: discord.ui.Button):

            if not interaction.message.author.guild_permissions.administrator:
                return

            self.scheduler.dba.execute('DELETE FROM signups_list WHERE (message_id = ?)', (interaction.message.id, ))
            self.scheduler.dba.execute('DELETE FROM absent_list WHERE (message_id = ?)', (interaction.message.id, ))
            self.scheduler.dba.execute('DELETE FROM tentative_list WHERE (message_id = ?)', (interaction.message.id, ))
            self.scheduler.dba.execute("DELETE FROM schedules_list WHERE message_id = ?", (interaction.message.id, ))
            self.scheduler.db.commit()

            await interaction.message.delete()
            await interaction.response.defer()


async def setup(bot):
    await bot.add_cog(Scheduler(bot))

