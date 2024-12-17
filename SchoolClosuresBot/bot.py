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

    async def send_school_closures(self):
        """Fetch closures and send matching results to the Discord channel."""
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found. Check the CHANNEL_ID in your .env file.")
            return

        closures = fetch_school_closures()
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
    """Respond to user commands."""
    if message.author == bot.user:
        return
# because debugging
    print(f"Received message: {message.content}")  # Debugging line

    # User command: !check
    if message.content.lower() == '!check':
        await bot.send_school_closures()

# Start the bot
bot.run(TOKEN)
