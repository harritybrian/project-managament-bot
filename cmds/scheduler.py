# all the imports you could ever want
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import datetime
import requests
import discord
import pytz
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot
from discord import app_commands

client = discord.Client(intents=discord.Intents.all())


class Notifier(commands.Cog, name="notifier"):
    def __init__(self, bot):
        self.bot = bot

    link_prefix = "https://github.com"


    # channel = '1070473541495029800'

    # The on_ready() function will be used to grab the first date.  The notify() function will be used to
    # periodically check to make sure updates are reported to the client
    def create_web_driver(self, username, password):
        # Web Driver Options
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # make sure no window pops up
        # options.add_experimental_option("detach", True)  ## if you want the browser to stay open, uncomment

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

    def create_web_hook_github(self, repository_url, username, password):
        # Create new web driver and log in
        driver = self.create_web_driver(username, password)

        web_hook_link = repository_url + '/settings/hooks/new'

        # retrieve GitHub web_hook link and open page
        driver.get(web_hook_link)

        # Wait until web page is loaded before entering data
        WebDriverWait(driver=driver, timeout=1200).until(EC.presence_of_element_located((By.NAME, "hook[url]")))

        # enter Webhook URL into location
        driver.find_element(By.ID, "hook_url").send_keys(self.web_hook_discord_full)

        # auto-fill selector and choose JSON
        selector = Select(driver.find_element(By.ID, "hook_content_type"))
        selector.select_by_value("json")

        # Select a radio button for all events  -- again, will change once discord commands aren't ugly and disgusting
        driver.find_element(By.ID, "hook-event-choice-everything").click()

        # submit the form and finalize webhook
        driver.find_element(By.XPATH, '//*[@id="new_hook"]/p[3]/button').click()

        WebDriverWait(driver=driver, timeout=1200)

        # log out of user-profile
        self.log_out(driver)

        WebDriverWait(driver=driver, timeout=1200)

        # close the driver
        driver.close()

    @commands.hybrid_command(name='notification', with_app_command=True, description="Notification Setup")
    @app_commands.describe(username='Enter a username',
                           password='Enter a password',
                           repository_url='Enter repo url')
    async def github_setup(self, ctx, username, password, repository_url):
        await ctx.send(content=f'Setting up your github system...', ephemeral=True, delete_after=5)
        self.create_web_hook_github(repository_url, username, password)
        await ctx.send(content=f'Successfully set up your github system!', ephemeral=True, delete_after=5)

    @commands.hybrid_command(name='create_webhook', with_app_command=True,
                             description='Create a webhook for the channel.')
    async def create_channel_webhook(self, ctx):
        channel = ctx.channel
        web = await channel.create_webhook(name="GitHub WebHook")
        web_url = str(web.url) + '/github'
        await ctx.send(content="Navigate to '<repo url>/settings/hooks/new' and copy the below URL into the Add Webhook field "  +
                               web_url, ephemeral=True)

        

    @commands.hybrid_command(name='github_login', with_app_command=True, description='Login to GitHub.')
    async def github_login(self, ctx, username, password):
        # await ctx.send(f'You entered: {username} and {password}')
        test_login = self.create_web_driver(username, password)

        repos = test_login.find_element("css selector", ".js-repos-container")
        # wait for the repos container to be loaded
        WebDriverWait(driver=test_login, timeout=10).until((lambda x: repos.text != "Loading..."))
        # iterate over the repos and print their names
        await ctx.send("Here are a list of your repositories:")
        for repo in repos.find_elements("css selector", "li.private"):  # you can use "li.private" for private repos
            await ctx.send(repo.find_element("css selector", "a").get_attribute("href"))
        test_login.close()


async def setup(bot):
    await bot.add_cog(Notifier(bot))
