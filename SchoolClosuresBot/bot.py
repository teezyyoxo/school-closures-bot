# School Closures Bot
# Version 2.2.1
# Currently configured for NBC Connecticut and all districts within.
# Created by @PBandJamf

# CHANGELOG

# Version 2.2.1
# - Corrected issue with matching lookup results. I hope.

# Version 2.2.0
# - Moved from paginated alphabet to a search/lookup, since there are a million and a half districts that NBC Connecticut reports on.
# - /setalerts is now interactive, as a result.

# Version 2.1.0
# - Users can now choose districts by alphabet range (A-F, G-L, M-R, S-Z) when setting alerts.
# - The bot now displays district options within the selected alphabet range in a new select menu after choosing a letter range.
# - The `/setalerts` command now splits the list of valid districts into groups based on their first letter to make it easier to navigate.
# - Added buttons for selecting the alphabet range, which triggers a new select menu with relevant districts for the user to choose from.
# - Users now properly see and select districts instead of just seeing "Districts".
# - Fixed issue where selecting a district wasn't properly saving the user's alerts.

# Version 2.0.2
# - Fixed: Added functionality to properly handle saving and loading user alerts to/from user_alerts.json.
# - Improved: The bot now properly serializes user alert data, converting sets to lists before saving to JSON.
# - Added: The bot will now automatically create the user_alerts.json file if it doesn't exist and allow for persistent user alerts.
# - Updated: The `/setalerts` command and `!check` responses work with the new user_alerts.json file for alert persistence.

# Version 2.0.1
# - Fixed: Handled the error when creating the select menu in the `/setalerts` command.
# - Added: Added `on_message` event to handle `!check` and guide users to the `/setalerts` command in DMs.
# - Improved: Bot now responds to `!check` command in DMs and sends school closure updates directly to users.
# - Updated: DMs now prompt users to use the `/setalerts` slash command for setting up alerts.

# Version 2.0.0
# - Added: /setalerts slash command for users to configure their alerts privately.
# - Improved: Alerts are now sent in DMs rather than publicly to avoid privacy concerns.
# - Changed: Valid districts are now checked against the predefined list from districts.json before being accepted.
# - Updated: General updates about closures now tag everyone in the channel but instruct users to DM the bot for private alerts.
# - Fixed: User alert data is now saved and persisted in user_alerts.json.

# Version 1.0.0
# - Initial release.

import discord
from discord import app_commands
from discord.ui import Button, View
import os
import json
from dotenv import load_dotenv
from scraperNBC import fetch_school_closures

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Load school districts from JSON for validation
districts_file = "districts.json"
with open(districts_file, "r") as f:
    VALID_DISTRICTS = set(json.load(f))

# Use a JSON file for persistence of user alerts
user_alerts_file = "user_alerts.json"

def load_user_alerts():
    if os.path.exists(user_alerts_file):
        with open(user_alerts_file, "r") as f:
            return json.load(f)
    return {}

def save_user_alerts():
    with open(user_alerts_file, "w") as f:
        # Convert sets to lists
        json.dump({user_id: list(districts) for user_id, districts in user_alerts.items()}, f, indent=4)

user_alerts = load_user_alerts()

class SchoolClosuresBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user}!')
        print(f'Bot is ready and listening for commands.')
        await self.tree.sync()  # Sync slash commands

    async def send_school_closures(self, url):
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found. Check the CHANNEL_ID in your .env file.")
            return

        try:
            closures = fetch_school_closures(url)
            if not closures:
                await channel.send("@everyone No closures or delays at the moment.")
                return

            await channel.send("@everyone Closures detected! DM me `!setalerts [district]` to set up private alerts for specific districts.")
            
            for user_id, districts in user_alerts.items():
                user = await self.fetch_user(user_id)
                matching_closures = [c for c in closures if c['school'].lower() in districts]
                if matching_closures:
                    message = "\n".join([f"{c['school']}: {c['status']}" for c in matching_closures])
                    await user.send(f"Here are your school closure alerts:\n{message}")
        except Exception as e:
            await channel.send(f"An error occurred while fetching closures: {e}")

intents = discord.Intents.default()
bot = SchoolClosuresBot(intents=intents)

# Event handler to listen for messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Handle commands in DMs
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith("!setalerts"):
            await message.channel.send("To set your alerts, use the `/setalerts` slash command.")
        elif message.content == "!check":
            url = "https://www.nbcconnecticut.com/weather/school-closings/"
            await bot.send_school_closures(url)
            await message.channel.send("School closures have been checked and alerts have been sent.")
    
    # Make sure to call the default on_message behavior for other commands
    await bot.process_commands(message)

from discord.ui import Button, View

# Slash command to set alerts with search
@bot.tree.command(name="setalerts", description="Set up your school closure alerts.")
async def setalerts(interaction: discord.Interaction, search: str):
    # Search for districts that match the search query (case-insensitive)
    matched_districts = [district for district in VALID_DISTRICTS if search.lower() in district.lower()]

    if not matched_districts:
        await interaction.response.send_message("No districts found matching your search.", ephemeral=True)
        return

    # If there are multiple matches, display the options with numbered buttons
    if len(matched_districts) > 1:
        await interaction.response.send_message(
            f"Did you mean one of the following districts?\n" +
            "\n".join([f"{i+1} - {district}" for i, district in enumerate(matched_districts)]),
            ephemeral=True
        )

        # Create buttons for each district
        view = View()
        for i, district in enumerate(matched_districts):
            button = Button(label=str(i+1), custom_id=str(i+1))
            button.callback = lambda interaction, district=district: button_callback(interaction, district)
            view.add_item(button)

        await interaction.followup.send(
            "Please select the number corresponding to the district you'd like to receive alerts for.",
            ephemeral=True, view=view
        )

    # If only one district matches, proceed with setting alerts immediately
    elif len(matched_districts) == 1:
        district = matched_districts[0]
        user_alerts[interaction.user.id] = user_alerts.get(interaction.user.id, set())
        user_alerts[interaction.user.id].add(district)
        save_user_alerts()
        await interaction.response.send_message(f"Alerts set for: {district}", ephemeral=True)

# Callback function to handle user selection
async def button_callback(interaction: discord.Interaction, district: str):
    user_alerts[interaction.user.id] = user_alerts.get(interaction.user.id, set())
    user_alerts[interaction.user.id].add(district)
    save_user_alerts()
    await interaction.response.send_message(f"Alerts set for: {district}", ephemeral=True)

    # Ask if the user wants to configure more alerts
    await interaction.followup.send(
        "Would you like to configure alerts for another district? (Yes/No)",
        ephemeral=True
    )

    # Here we can add buttons for 'Yes' and 'No' for additional configuration
    yes_button = Button(label="Yes", custom_id="yes")
    no_button = Button(label="No", custom_id="no")

    yes_button.callback = lambda interaction: prompt_for_more_alerts(interaction)
    no_button.callback = lambda interaction: finish_alerts_configuration(interaction)

    # Display the 'Yes' and 'No' buttons to the user
    view = View()
    view.add_item(yes_button)
    view.add_item(no_button)
    await interaction.followup.send("Would you like to configure alerts for more districts?", ephemeral=True, view=view)

async def prompt_for_more_alerts(interaction: discord.Interaction):
    # If the user wants more alerts, ask them to search again
    await interaction.response.send_message(
        "Please enter the name of another district you'd like to set alerts for.",
        ephemeral=True
    )

async def finish_alerts_configuration(interaction: discord.Interaction):
    # If the user is done, let them know
    await interaction.response.send_message(
        "Your alert configuration is complete! Stay updated on school closures.",
        ephemeral=True
    )
# Slash command to check for closures (for testing purposes)
@bot.tree.command(name="check", description="Check for current school closures.")
async def check(interaction: discord.Interaction):
    url = "https://www.nbcconnecticut.com/weather/school-closings/"
    await bot.send_school_closures(url)
    await interaction.response.send_message("School closures have been checked and alerts have been sent.")

# Send it.
bot.run(TOKEN)
