import discord
import os
from dotenv import load_dotenv
from scraper import fetch_school_closures  # Assume the scraper is in a separate file

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
SEARCH_CRITERIA = os.getenv('SEARCH_CRITERIA', '').lower()

class SchoolClosuresBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def send_school_closures(self):
        channel = self.get_channel(CHANNEL_ID)
        closures = fetch_school_closures()
        for closure in closures:
            if SEARCH_CRITERIA in closure['school'].lower():
                await channel.send(f"{closure['school']}: {closure['status']}")

intents = discord.Intents.default()
bot = SchoolClosuresBot(intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == '!check':
        await bot.send_school_closures()

bot.run(TOKEN)
