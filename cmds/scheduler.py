# Imports
import discord
from discord import app_commands
from discord.ext import commands
import datetime
import pytz
import sqlite3
import re

# Initialize discord client.
client = discord.Client(intents=discord.Intents.all())
# Global time zone variable. Scheduler will still display your local timezone through Discord.
timezone = pytz.timezone('America/Denver')


# Scheduler class.
# Implements the schedule command.
class Scheduler(commands.Cog, name="scheduler"):

    # Constructor. The bot, buttons view, and check_time are initialized here.
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(self.NewView(self))
        self.check_time.start()
        print('Scheduler initialized!')

    # Connect to the SQLite database.
    db = sqlite3.connect("schedules.db")
    dba = db.cursor()

    # Checks the current time every minute, and compares it to existing schedules.
    # If the schedules are past the current time, their buttons are disabled and their data removed from the database.
    @discord.ext.tasks.loop(minutes=1)
    async def check_time(self):
        print('Checking time.')
        # Gets the current time every time the code is run, and converts it to same format as the schedules time.
        time_now = datetime.datetime.now()
        mst_now = time_now.astimezone(timezone)
        my_mst = datetime.datetime.strftime(mst_now, '%Y-%m-%d %I:%M %p')

        # Retrieve the list of all schedule times from the database.
        self.dba.execute("SELECT time FROM schedules_list")
        data = self.dba.fetchall()

        # Looping through the times of every schedule stored.
        for x in data:
            # Checks if the schedules time is before or equal to the current time. Proceeds if true.
            if x[0] <= my_mst:
                print('Event has passed! Removing...')

                # Retrieve the message id and channel id corresponding to the time.
                self.dba.execute("SELECT message_id FROM schedules_list WHERE time = ?", (x[0],))
                msg_id = self.dba.fetchone()
                msg_id = re.sub('\D', '', str(msg_id))
                msg_id = int(msg_id)
                self.dba.execute("SELECT channel_id FROM schedules_list WHERE time = ?", (x[0],))
                channel_id = self.dba.fetchone()
                channel_id = re.sub('\D', '', str(channel_id))
                channel_id = int(channel_id)

                # Retrieves the channel and message objects from Discord using their ID's.
                channel = self.bot.get_channel(channel_id)
                msg = await channel.fetch_message(msg_id)

                # Initializes a blank view, which is a single disabled button displaying the event is closed.
                view = self.BlankView(self)

                # Edits the view of the schedules message, replacing the buttons with the disabled one.
                await msg.edit(view=view)

                # Remove the schedule and all related signups from the database.
                self.dba.execute('DELETE FROM signups_list WHERE (message_id = ?)', (msg_id,))
                self.dba.execute('DELETE FROM absent_list WHERE (message_id = ?)', (msg_id,))
                self.dba.execute('DELETE FROM tentative_list WHERE (message_id = ?)', (msg_id,))
                self.dba.execute('DELETE FROM schedules_list WHERE (message_id = ?)', (msg_id,))
                self.db.commit()
                print('Deleted past event records.')

    # The swap function swaps users between different signup options, if needed.
    # If the user is not in any other signups for the schedule, they are added normally.
    # If the user is in another signup for the schedule, the original is removed,
    # and they are added to their new signup.
    # The option variable is an Integer representing which signup was chosen:
    # 1 for signup, 2 for absent, 3 for tentative.
    async def swap(self, option, interaction):

        # Retrieves the user ID and message ID from the button pressed.
        user_id = interaction.user.id
        msg_id = interaction.message.id

        # Checks if the user is already on the signup they chose. Returns if found.
        if option == 1:
            self.dba.execute("SELECT user_id FROM signups_list WHERE message_id = ?", (msg_id,))
            data = self.dba.fetchall()
        elif option == 2:
            self.dba.execute("SELECT user_id FROM absent_list WHERE message_id = ?", (msg_id,))
            data = self.dba.fetchall()
        elif option == 3:
            self.dba.execute("SELECT user_id FROM tentative_list WHERE message_id = ?", (msg_id,))
            data = self.dba.fetchall()

        for x in data:
            if x[0] == user_id:
                return

        # If the user is not already on their signup list, it deletes them from the other 2 lists they did not choose.
        # This is to ensure they do not exist on two lists at once: for example, signed up and absent at the same time.
        if option != 1:
            self.dba.execute('DELETE FROM signups_list WHERE (message_id = ? AND user_id = ?)', (msg_id, user_id))
        if option != 2:
            self.dba.execute('DELETE FROM absent_list WHERE (message_id = ? AND user_id = ?)', (msg_id, user_id))
        if option != 3:
            self.dba.execute('DELETE FROM tentative_list WHERE (message_id = ? AND user_id = ?)', (msg_id, user_id))

        # Once the user is removed from the lists they did not choose,
        # they are added to the list they did choose, completing the swap.
        if option == 1:
            self.dba.execute('INSERT INTO signups_list(message_id, user_id) VALUES(?, ?)', (msg_id, user_id))
        elif option == 2:
            self.dba.execute('INSERT INTO absent_list(message_id, user_id) VALUES(?, ?)', (msg_id, user_id))
        elif option == 3:
            self.dba.execute('INSERT INTO tentative_list(message_id, user_id) VALUES(?, ?)', (msg_id, user_id))

        # Changes are committed to database and function returns.
        self.db.commit()
        return

    # The update_embed function updates the embed that contains the schedules' information.
    # The function will retrieve the lists of users for each signup type, create the list, get the nicknames of each
    # user in their server, and replace the existing list with the new one.
    async def update_embed(self, embed: discord.Embed, interaction):
        msg_id = interaction.message.id

        # Unpacks the embed into a dict that can be iterated through and edited.
        dict_embed = embed.to_dict()

        # Creates lists for local use.
        signups = []
        absent = []
        tentative = []

        # Gets the list of users for each signup from the database.
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

        # Iterates through the fields of the embed, until the needed one is found.
        for field in dict_embed["fields"]:
            if field["name"] == "✅Signups:":
                newstr = ""
                # Gets the nickname of each user and creates a string from it, with a new line for each user.
                for x in signups:
                    y = await interaction.guild.fetch_member(x)
                    newstr += '\n' + str(y.nick)
                # Updates the existing list with the new one.
                field["value"] = newstr

        # Same as the above loop, but for absences instead of signups.
        for field in dict_embed["fields"]:
            if field["name"] == "❌Absences:":
                newstr = ""
                for x in absent:
                    y = await interaction.guild.fetch_member(x)
                    newstr += '\n' + str(y.nick)
                field["value"] = newstr

        # Same as the above loop, but for tentatives instead of absences.
        for field in dict_embed["fields"]:
            if field["name"] == "⚖️Tentative:":
                newstr = ""
                for x in tentative:
                    y = await interaction.guild.fetch_member(x)
                    newstr += '\n' + str(y.nick)
                field["value"] = newstr

        # Creates the new embed from the edited dict.
        embed = discord.Embed.from_dict(dict_embed)

        # Gets the number of users in the signups list for the attending value.
        embed.set_field_at(2, name=f'\U0001F465 Attending: {len(lista)}', value="")
        return embed

    # The schedule command itself is implemented here.
    # Parameters are:
    # Time - required, and in Y-M-D H:M AM/PM format.
    # Title - optional, the title of the schedule.
    # Description - optional, the description of the schedule.
    # Image - optional, display an image at the bottom of the schedule. URLs are accepted.
    # Thumbnail - optional, displays a small image at the top right of the schedule. URLs are accepted.

    # This header describes the command name and information.
    @commands.hybrid_command(name='schedule', with_app_command=True, description="A test scheduler.",
                             brief="Brief example.", usage="Usage example.")
    # This header adds descriptions to the command parameters as you are typing them.
    @app_commands.describe(title='Enter a title for the event.', description='Enter a description for the event.',
                           time='Enter time in the format: Y-M-D H:M AM/PM',
                           image='Enter an image URL for the event.',
                           thumbnail='Enter a image URL for the thumbnail.')
    @commands.has_permissions(administrator = True) # Checks if the user typing the command is an administrator - only admins can create schedules.
    async def scheduler(self, ctx, *, time: str = commands.parameter(description="Enter as Y-M-D Hour-Minute-AM/PM"),
                        title: str = commands.parameter(default="Default title.",
                                                        description='Title of the event.',
                                                        displayed_default='Displayed default'),
                        description: str = commands.parameter(default="Default description.",
                                                              description="Desc of the event."),
                        image: str = commands.parameter
                            (default=None, description="Image for the event"),
                        thumbnail: str = commands.parameter
                            (default=None, description="Thumbnail image for the event")):


        # Formats the inputted date and time into a datetime objects, and localizes it.
        try:
            date = datetime.datetime.strptime(time, '%Y-%m-%d %I:%M %p')
        except:
            await ctx.send(content='Time format is invalid! Check the description.', ephemeral=True, delete_after=5)
            return
        date1 = timezone.localize(date, is_dst=None)
        new_time = date.strftime("%Y-%m-%d %I:%M %p")

        # Gets the time when the command is run and localizes it.
        time_now = datetime.datetime.now()
        mst_now = time_now.astimezone(timezone)

        # Checks if the time given in the command parameter is in the past - if true, display error and return.
        if date1 < mst_now:
            await ctx.send(content='That time has already passed!', ephemeral=True, delete_after=5)
            return

        # Creates an embed to display the schedule information.
        signup = discord.Embed(timestamp=date)

        # Creates the view, which contains the buttons for our schedule.
        view = self.NewView(self)

        # Sets various fields, if an argument was given.
        signup.set_author(name=f'Created by {ctx.author.display_name}')
        signup.title = title
        signup.description = description
        signup.set_footer(text="\U0001F916 Bot by C&C")


        if image is not None:
            signup.set_image(url=image)

        if thumbnail is not None:
            signup.set_thumbnail(url=thumbnail)

        # Creates the default fields, using given time.
        signup.add_field(name=f'\U0001F4C5 ' + date.strftime("%Y-%m-%d"), value="", inline=True)
        signup.add_field(name=f'\U0000231A ' + date.strftime("%I:%M %p"), value="", inline=True)
        signup.add_field(name="\U0001F465 Attending:", value=0, inline=True)
        signup.add_field(name="✅Signups:", value="", inline=True)
        signup.add_field(name="❌Absences:", value="", inline=True)
        signup.add_field(name="⚖️Tentative:", value="", inline=True)

        # Checks for any incorrect inputs when attempting to make the embed.
        try:
            embed = await ctx.send(embed=signup, view=view)
        except:
            await ctx.send(content='Could not create event! Check that your inputs are valid!',
                           ephemeral=True, delete_after=5)
            return

        # Creates a database entry with the message id, the formatted time, and the channel id.
        msg_id = embed.id
        self.dba.execute('INSERT INTO schedules_list(message_id, time, channel_id) VALUES(?, ?, ?)',
                         (msg_id, new_time, ctx.message.channel.id))
        print('Schedule created!')
        self.db.commit()

        # Once schedules is successfully creates, creates a Discord scheduled event.
        await discord.Guild.create_scheduled_event(ctx.guild, name=title, start_time=date1,
        description=description, channel=ctx.guild.voice_channels[0], )

    @scheduler.error
    async def scheduler_error(cog, ctx, error):
        """Permissions fail response"""
        if isinstance(error, commands.MissingPermissions):
            msg = f"{ctx.message.author.mention} You lack the required permissions for this command"
            await ctx.send(msg)

    
    # This view creates the disabled button stating the event has passed.
    class BlankView(discord.ui.View):
        def __init__(self, scheduler):
            super().__init__(timeout=None)
            self.scheduler = scheduler

        @discord.ui.button(label="The event has already passed.", style=discord.ButtonStyle.secondary,
                           custom_id='blank',
                           disabled=True)
        async def blank_button(self):
            return

    # This view contains the buttons for an active schedule.
    # Their code is activated whenever they are pressed.
    class NewView(discord.ui.View):

        # Constructor initializes with no timeout so inputs are always accepted.
        def __init__(self, scheduler):
            super().__init__(timeout=None)
            self.scheduler = scheduler

        # Signup button.
        @discord.ui.button(label="Sign up", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_1',
                           emoji="✅")
        async def button_signup(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Defers the response, since none is needed.
            await interaction.response.defer()

            # Runs the swap command to add the user to their list, if possible.
            await self.scheduler.swap(1, interaction)

            # Edits the schedule embed with a new embed fetched from the update_embed function.
            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))

        # Same as signup button, but for absences.
        @discord.ui.button(label="Absent", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_2',
                           emoji="❌")
        async def button_absent(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()

            await self.scheduler.swap(2, interaction)

            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))


        # Same as signup button, but for tentatives.
        @discord.ui.button(label="Tentative", row=0, style=discord.ButtonStyle.secondary, custom_id='persistent_view_3',
                           emoji="⚖")
        async def button_tentative(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()

            await self.scheduler.swap(3, interaction)

            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))

        # Remove signup button. This button removes the users signup from any and all lists.
        @discord.ui.button(label="Remove Sign Up", row=1, style=discord.ButtonStyle.danger,
                           custom_id='persistent_view_4')
        async def button_remove(self, interaction: discord.Interaction, button: discord.ui.Button):

            # Removes the users database entry for the given schedule from every list.
            self.scheduler.dba.execute('DELETE FROM signups_list WHERE (message_id = ? AND user_id = ?)',
                                       (interaction.message.id, interaction.user.id))
            self.scheduler.dba.execute('DELETE FROM absent_list WHERE (message_id = ? AND user_id = ?)',
                                       (interaction.message.id, interaction.user.id))
            self.scheduler.dba.execute('DELETE FROM tentative_list WHERE (message_id = ? AND user_id = ?)',
                                       (interaction.message.id, interaction.user.id))
            self.scheduler.db.commit()

            # Updates the embed with the new changes.
            await interaction.message.edit(embed=await self.scheduler.update_embed(interaction.message.embeds[0],
                                                                                   interaction))
            await interaction.response.defer()

        # Remove schedule button. Allows admin to delete a schedule, and removes all its related info from the database.
        @discord.ui.button(label="Delete Event", row=1, style=discord.ButtonStyle.danger,
                           custom_id='persistent_view_5')
        async def button_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Checks that the user is an admin of the server.
            await interaction.response.defer()
            print('TESTING')
            if not interaction.user.guild_permissions.administrator:
                print('TESTING PART 2')
                return

            print('User deleted event, removing records....')

            # Removes everything related to the message id where the button is pressed.
            # This includes the schedule entry and all user signups.
            self.scheduler.dba.execute('DELETE FROM signups_list WHERE (message_id = ?)', (interaction.message.id,))
            self.scheduler.dba.execute('DELETE FROM absent_list WHERE (message_id = ?)', (interaction.message.id,))
            self.scheduler.dba.execute('DELETE FROM tentative_list WHERE (message_id = ?)', (interaction.message.id,))
            self.scheduler.dba.execute('DELETE FROM schedules_list WHERE (message_id = ?)', (interaction.message.id,))
            self.scheduler.db.commit()

            print('Records removed.')

            # Deletes the actual message itself once the database is updated.
            await interaction.message.delete()


# Discord Cog setup. Enables the schedule for use from the main file.
async def setup(bot):
    await bot.add_cog(Scheduler(bot))
