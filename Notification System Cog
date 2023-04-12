# all the imports you could ever want
import selenium.webdriver.common.devtools.v85.css
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from discord.ui import Select, View
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio

client = discord.Client(intents=discord.Intents.all())

class webhookOption(Select):


    """Class for the select menu for the server state option"""
    def __init__(self) -> None:
        super().__init__(
            placeholder = 'Pick a notification source',
            options = [
                discord.SelectOption(
                    label = 'GitHub',
                    description = 'GitHub notifications'
                ),
                discord.SelectOption(
                    label = 'Google Drive',
                    description = 'Google Drive notifications'
                )
            ])


    async def callback(self, interaction):
        if self.values[0] == "GitHub":
            channel = interaction.channel
            web = await channel.create_webhook(name="GitHub Webhook")
            web_url = str(web.url) + '/github'
            await interaction.response.send_message(
                content="Navigate to '<repo url>/settings/hooks/new' and copy the below URL into the Add Webhook field " +
                        web_url, ephemeral=True)
        if self.values[0] == "Google Drive":
            channel = interaction.channel
            await interaction.response.send_message(
                content="We are still working on Google Drive Integrations.  Check back with us shortly." +
                        web_url, ephemeral=True)


class Notifier(commands.Cog, name="notifier"):
    def __init__(self,bot):
        self.bot = bot

    def create_web_driver(self, username, password):
        # Web Driver Options
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # make sure no window pops up
        #options.add_experimental_option("detach", True)  ## if you want the browser to stay open, uncomment

        # Initialize Web Driver
        driver = webdriver.Chrome(options=options)
        driver.get("https://github.com/login")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_field")))
        # find username/email field and send the username itself to the input field
        driver.find_element("id", "login_field").send_keys(username)
        # find password input field and insert password as well
        driver.find_element("id", "password").send_keys(password)
        # click login button
        driver.find_element("name", "commit").click()

        # wait for the ready state to be complete
        WebDriverWait(driver=driver, timeout=10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )
        error_message = "Incorrect username or password."
        # get the errors (if there are any)
        errors = driver.find_elements("css selector", ".flash-error")
        if any(error_message in e.text for e in errors):
            print("[!] Login failed")
        else:
            print("[+] Login successful")

        return driver

    def log_out(self, driver):
        WebDriverWait(driver=driver, timeout=5)
        driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/header/div[7]/details/summary').click()
        WebDriverWait(driver=driver, timeout=100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dropdown-item.dropdown-signout')))
        driver.find_element(By.CSS_SELECTOR, '.dropdown-item.dropdown-signout').click()

    def create_web_hook_github_everything(self, repository_url, username, password, web):
        # Create new web driver and log in
        print("Trying to Create Web Driver")
        driver = self.create_web_driver(username, password)
        print("Created Web Driver")
        web_hook_link = repository_url + '/settings/hooks/new'

        # retrieve GitHub web_hook link and open page
        driver.get(web_hook_link)
        print("Retrieved link properly")
        # Wait until web page is loaded before entering data
        WebDriverWait(driver=driver, timeout=1200).until(EC.presence_of_element_located((By.NAME, "hook[url]")))

        # enter Webhook URL into location
        driver.find_element(By.ID, "hook_url").send_keys(web)
        print("Sent Webhook URL into new piece.")

        # auto-fill selector and choose JSON
        selector = selenium.webdriver.support.ui.Select(driver.find_element(By.ID, "hook_content_type"))
        selector.select_by_value("json")

        driver.find_element(By.ID, "hook-event-choice-everything").click()

        # submit the form and finalize webhook
        driver.find_element(By.XPATH, '//*[@id="new_hook"]/p[3]/button').click()

        WebDriverWait(driver=driver, timeout=1200)
        print("Trying to log out")
        # log out of user-profile
        self.log_out(driver)
        print("Logged out")
        WebDriverWait(driver=driver, timeout=1200)

        # close the driver
        driver.close()

    def create_web_hook_github_push(self, repository_url, username, password, web):
        # Create new web driver and log in
        driver = self.create_web_driver(username, password)

        web_hook_link = repository_url + '/settings/hooks/new'

        # retrieve GitHub web_hook link and open page
        driver.get(web_hook_link)

        # Wait until web page is loaded before entering data
        WebDriverWait(driver=driver, timeout=1200).until(EC.presence_of_element_located((By.NAME, "hook[url]")))

        # enter Webhook URL into location
        driver.find_element(By.ID, "hook_url").send_keys(web)

        # auto-fill selector and choose JSON
        selector = selenium.webdriver.support.ui.Select(driver.find_element(By.ID, "hook_content_type"))
        selector.select_by_value("json")

        driver.find_element(By.ID, "hook-event-choice-push").click()

        # submit the form and finalize webhook
        driver.find_element(By.XPATH, '//*[@id="new_hook"]/p[3]/button').click()

        WebDriverWait(driver=driver, timeout=1200)

        # log out of user-profile
        self.log_out(driver)

        WebDriverWait(driver=driver, timeout=1200)

        # close the driver
        driver.close()

    @commands.hybrid_command(name='github', with_app_command=True, description="GitHub Notification System Setup.  Note: You must be the repository owner")
    @app_commands.describe(username='Enter a username',
                           password='Enter a password',
                           repository_url='Enter repo url',
                           event_choice='Enter "E" for everything or "P" for push notifications')
    async def github_setup(self, ctx, username, password, repository_url, event_choice):
        await ctx.send(content=f'Setting up your github system...', ephemeral=True, delete_after=5)
        channel = ctx.channel
        web = await channel.create_webhook(name="GitHub Webhook")
        web_url = str(web.url) + '/github'
        print (web_url)
        if event_choice == "E":
            self.create_web_hook_github_everything(repository_url, username, password, web_url)
        else:
            self.create_web_hook_github_push(repository_url, username, password, web_url)
        await ctx.send(content=f'Successfully set up your github system!', ephemeral=True, delete_after=5)

    @commands.hybrid_command(name='create_webhook', with_app_command=True,
                             description='Create a webhook for the channel.')
    async def create_channel_webhook(self, ctx):
        webhook = webhookOption()
        webhook_view = View()
        webhook_view.add_item(webhook)
        await ctx.send("Please select your notification source", view = webhook_view,
                       ephemeral=True)

    @commands.hybrid_command(name='github_repos', with_app_command=True, description='List your GitHub Repos')
    @app_commands.describe(username='Enter a username',
                           password='Enter a password',
                           type='Enter "PV" for your private repositories or "A" for all')
    async def github_login(self, ctx, username, password, type):
        # await ctx.send(f'You entered: {username} and {password}')
        test_login = self.create_web_driver(username, password)
        repos = test_login.find_element("css selector", ".js-repos-container")
        await ctx.defer()
        WebDriverWait(driver=test_login, timeout=2).until((lambda x: repos.text != "Loading..."))
        seperator = ", "
        repository_list = []
        if type == "PV":
        #await ctx.send(content="Here are a list of your repositories:")
            for repo in repos.find_elements("css selector", "li.private"):  # you can use "li.private" for private repos
                repository_list.append(str(repo.find_element("css selector", "a").get_attribute("href")))
                #await ctx.send(repo.find_element("css selector", "a").get_attribute("href"))
            await ctx.send("Here's a list of your private repositories: \n" + seperator.join(repository_list))
        elif type == "A":
            for repo in repos.find_elements("css selector", "li"):  # you can use "li.private" for private repos
                repository_list.append(str(repo.find_element("css selector", "a").get_attribute("href")))
                #await ctx.send(repo.find_element("css selector", "a").get_attribute("href"))
            await ctx.send("Here's a list of all of your repositories: \n" + seperator.join(repository_list))
        #print(repository_list)
        test_login.close()

    @commands.hybrid_command(name='delete_webhook', with_app_command=True,
                             description='Create a webhook for the channel.',
                             webhook_name= "Type the name of the Webhook you want to delete")
    async def delete_channel_webhook(self, ctx, webhook_name):
        channel_webhooks = await ctx.channel.webhooks()
        for webhook in channel_webhooks:  # iterate through the webhooks
            if webhook.name == webhook_name:
                await webhook.delete()
                #break
        await ctx.send(content=f'Successfully deleted webhook: ' + webhook_name, ephemeral=True, delete_after=5)


async def setup(bot):
    await bot.add_cog(Notifier(bot))
