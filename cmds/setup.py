import discord
from discord import app_commands
from discord.utils import get
from discord.ext import commands
from discord.ui import Select, View
import TicketSystem


client = discord.Client(intents = discord.Intents.all())

class doubleFreshConfirm(View):
    """Class for the double confirmation button"""
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label = "Yes, I'm REALLY sure", style = discord.ButtonStyle.red, custom_id = 'Double confirm')
    async def double_confirm_button(self, interaction, button):
        features = featureSelect('N')
        feature_view = View()
        feature_view.add_item(features)
        await interaction.response.send_message(
            "Alright then, select your features!", 
            view = feature_view,
            ephemeral = True
            )
    @discord.ui.button(label = "I've changed my mind", style = discord.ButtonStyle.blurple, custom_id = 'reject')
    async def reject_button(self, interaction, button):
        embed = discord.Embed(title = "Operation aborted, if you would like to attempt setup again run the command again", color = discord.Color.brand_green())
        await interaction.response.send_message(
            embed = embed,
            ephemeral = True
        )


class freshConfrim(View):
    """Class for the initial confirmation button"""
    def __init__(self) -> None:
        super().__init__(timeout = None)
    
    @discord.ui.button(label = "Yes, I'm sure", style = discord.ButtonStyle.red, custom_id = 'confirm')
    async def confirm_button(self, interaction, button):
        embed = discord.Embed(title = 'Are you really sure you want to have a fresh server setup?', color = discord.Color.brand_red())
        await interaction.response.send_message(
            embed = embed,
            view = doubleFreshConfirm(),
            ephemeral = True
        )
    @discord.ui.button(label = "I've changed my mind", style = discord.ButtonStyle.blurple, custom_id = 'reject')
    async def reject_button(self, interaction, button):
        embed = discord.Embed(title = "Operation aborted, if you would like to attempt setup again run the command again", color = discord.Color.brand_green())
        await interaction.response.send_message(
            embed = embed,
            ephemeral = True
        )


class serverOption(Select):
    """Class for the select menu for the server state option"""
    def __init__(self) -> None:
        super().__init__(
            placeholder = 'Is this a new server or an existing server?',
            options = [
                discord.SelectOption(
                    label = 'New',
                    description = 'Brand new server'
                ),
                discord.SelectOption(
                    label = 'Existing',
                    value = 'E',
                    description = 'A server that has been used before'
                )
            ])

    async def callback(self, interaction):
        if self.values[0] == 'E':
            features = featureSelect('E')
            feature_view = View()
            feature_view.add_item(features)
            await interaction.response.send_message(
                "You have stated you have a pre-existing server, no content will be deleted. Please selection your features",
                ephemeral = True,
                view = feature_view
            )
        else:
            await interaction.response.send_message(
                "You have stated this a brand new server, content will be deleted! Are you sure?",
                ephemeral = True,
                view = freshConfrim()
            )


class featureSelect(Select):
    """Class for the select menu for selecting the features"""
    def __init__(self, server_state = 'E'):
        super().__init__(
            min_values = 1,
            max_values = 3,
            placeholder = 'Select your features!',
            options = [
                discord.SelectOption(
                    label = 'Ticket system',
                    value = 1,
                    emoji = '🎫',
                    description = 'Implement our ticketing system'
                ),
                discord.SelectOption(
                    label = 'Notification system',
                    value = 2,
                    emoji = '📆',
                    description = 'Implement our notification system'
                ),
                discord.SelectOption(
                    label = 'ChatGPT Implemenation',
                    value = 3,
                    emoji = '🤖',
                    description = 'Implement our ChatGPT system (Currently not working/implemented)'
                )
        ])
        self.state = server_state

    async def callback(self, interaction):
        featuresDict = {'1': "Ticket system", '2': "Notification system", '3': "ChatGPT implementation"}
        values = self.values
        embed = discord.Embed(title = 'Features added:')
        for feature in values:
            embed.add_field(name = featuresDict[feature], value = 'Added')
        connections = connectionsSelect(values, self.state)
        connection_view = View()
        connection_view.add_item(connections)
        await interaction.response.send_message(
            "Please select your connections, if you are not using our notification system select any random connection",
            embed = embed,
            view = connection_view,
            ephemeral = True
        )


class connectionsSelect(Select):
    """Class for adding the connections requested by the user"""
    def __init__(self, server_features, server_state = 'E') -> None:
        super().__init__(
            min_values = 1,
            max_values = 3,
            placeholder = 'Choose your connections!',
            options = [
                discord.SelectOption(
                    label = 'GitHub', 
                    emoji = '🤖', 
                    description = 'GitHub connection'
                ),
                discord.SelectOption(
                    label = 'Trello',
                    emoji = '📆',
                    description = 'Trello connection'
                ),
                discord.SelectOption(
                    label = 'Microsoft Teams',
                    emoji = '🤝',
                    description = 'Microsoft Teams connection',
                )
            ])
        self.features = server_features
        self.state = server_state 

    async def callback(self, interaction):

        await interaction.response.send_message('Beginning your server setup!', ephemeral = True)
        
        # Delete all initial categories, then delete the remaining channels if the server is new
        if self.state != 'E':
            for channel in interaction.guild.channels:
                await channel.delete()
            for category in interaction.guild.categories:
                await category.delete()

        for feature in self.features:
            match feature:
                case '1': # Ticket feature is requested
                    ticket = await interaction.guild.create_category(name = 'Tickets', position = 2, reason = 'New ticketing channel')
                    ticket_channel = await ticket.create_text_channel(name = 'Submit-a-ticket')
                    embed = discord.Embed(title = "If you need support, click the button below to create a new ticket!",
                        color = discord.Colour.dark_teal())
                    await ticket_channel.send(embed = embed, view = TicketSystem.ticket_launcher())

                case '2': # Notification feature is requested
                    # Create the cataegories for the notification system
                    updates = await interaction.guild.create_category(name='Updates', position = 0, reason = 'New update channel')
                    tracker = await interaction.guild.create_category(name = 'Schedule/Calendar', position = 1, reason = 'New tracking channel')
                    # Create the text channels for the notifications system
                    await tracker.create_text_channel(name = 'Team-member-scheduler')
                    await tracker.create_text_channel(name = 'Upcoming meetings')
                    # Add the User's chosen connections
                    for connect in self.values:
                        await updates.create_text_channel(name = connect + '-updates')

                case '3': # ChatGPT feature is requested
                    pass # NOT IMPLEMENTED YET, NOTHING WILL BE ADDED

        if self.state != 'E': # Creating voice channels and a general channel if server is new
            voice = await interaction.guild.create_category(name = 'Voice Channels', position = 3, reason = 'New Voice Channels')
            for i in range(1, 4):
                await voice.create_voice_channel(name = 'Voice ' + str(i))
            discuss = await interaction.guild.create_category(name = 'Discussion', position = 0)
            general = await discuss.create_text_channel(name = 'General')
            await general.send('Your server is now setup!', delete_after = 10)
        else:
            await interaction.channel.send('Your server is now setup!', delete_after = 10)


class Setup(commands.Cog, name = "setup"):
    """Initial start for the setup command"""
    def __init__(self, bot):
        self.bot = bot

    text = 'A command to quickly set up your collabrative environment'
    @commands.hybrid_command(name = 'setup', with_app_command = True, description = text)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        state = serverOption()
        state_view = View()
        state_view.add_item(state)
        await ctx.send("Please select your server's state!", view=state_view, ephemeral = True)

    @setup.error
    async def setup_error(cog, ctx, error):
        """Permissions fail response"""
        if isinstance(error, commands.MissingPermissions):
            msg = f"{ctx.message.author.mention}, You lack the required permissions for this command."
            await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(Setup(bot))