import discord
import os
from dotenv import load_dotenv
# Ensure scraper.py is in the same directory and up-to-date
from scraperNBC import fetch_school_closures

# MAKE SURE YOU HAVE A .ENV IN THE SAME FOLDER, BECAUSE WE'RE LOADING IT HERE:
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')  # Your bot token
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Discord channel ID
SEARCH_CRITERIA = [c.strip().lower() for c in os.getenv('SEARCH_CRITERIA', '').split(',')]  # Comma-separated list of criteria

class SchoolClosuresBot(discord.Client):
      async def on_ready(self):
        """Triggered when the bot connects to Discord."""
        print(f'Logged in as {self.user}!')
        print(f'Bot is ready and listening for commands.')

        # Debugging: Check if the bot can access the channel
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            print(f"Accessing channel: {channel.name} (ID: {CHANNEL_ID})")
        else:
            print(f"Failed to access channel: {CHANNEL_ID}. Ensure the channel ID is correct and the bot has permissions.")

      async def send_school_closures(self):
        """Fetch closures and send matching results to the Discord channel."""
        print("Fetching school closures...")  # Debugging line to ensure the function is called
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found. Check the CHANNEL_ID in your .env file.")
            return

        # Ensure the URL is passed to fetch_school_closures()
        url = "https://web.archive.org/web/20241212072827/https://www.nbcconnecticut.com/weather/school-closings/"
        closures = fetch_school_closures(url)  # Pass the URL here
        if not closures:
            await channel.send("No closures or delays at the moment.")
            return

        found_closures = False
        for closure in closures:
            if any(criteria in closure['school'].lower() for criteria in SEARCH_CRITERIA):
                await channel.send(f"{closure['school']}: {closure['status']}")
                found_closures = True

        if not found_closures:
            await channel.send("No closures match your criteria.")

intents = discord.Intents.default()  # Basic bot permissions
bot = SchoolClosuresBot(intents=intents)

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Debugging line to show exact content of the message (including any invisible characters)
    print(f"Received message: {repr(message.content)}")  # Debugging line with repr()
    print(f"Message length: {len(message.content)}")  # Check the length to ensure it's non-empty
    print(f"Channel ID: {message.channel.id}")  # Log the channel ID to verify
    print(f"Message Author: {message.author}")  # Log the message author

    # Check if the message is the !check command
    if message.content.strip().lower() == '!check':  # Strip whitespace and check lowercase
        print("Command !check detected.")  # Debugging line
        await bot.send_school_closures()  # Make sure this line is being called

# Start the bot
bot.run(TOKEN)
