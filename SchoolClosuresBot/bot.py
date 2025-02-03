# School Closures Bot
# Version 2.1.0
# Currently configured for NBC Connecticut and all districts within.
# Created by @PBandJamf

# CHANGELOG
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
from discord import app_commands, Button, View
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

@bot.tree.command(name="setalerts", description="Set up your school closure alerts.")
async def setalerts(interaction: discord.Interaction):
    # Load the districts from the file
    districts_file = "districts.json"
    with open(districts_file, "r") as f:
        VALID_DISTRICTS = json.load(f)  # Assuming it's just a list

    # Sort districts alphabetically
    VALID_DISTRICTS.sort()

    # Split districts into chunks based on the first letter
    # A-F, G-L, M-R, S-Z
    ranges = [
        ("A-F", [district for district in VALID_DISTRICTS if district[0].upper() in "ABCDEF"]),
        ("G-L", [district for district in VALID_DISTRICTS if district[0].upper() in "GHIJKL"]),
        ("M-R", [district for district in VALID_DISTRICTS if district[0].upper() in "MNOPQR"]),
        ("S-Z", [district for district in VALID_DISTRICTS if district[0].upper() in "STUVWXYZ"]),
    ]
    
    # Create the pagination buttons for the user
    button_labels = [r[0] for r in ranges]
    buttons = [discord.ui.Button(label=label, custom_id=label) for label in button_labels]

    # Create a view for pagination
    view = discord.ui.View()

    # Add buttons to the view
    for button in buttons:
        view.add_item(button)

    # Define what happens when a button is clicked
    async def button_callback(interaction: discord.Interaction):
        selected_range = next((r for r in ranges if r[0] == interaction.data["custom_id"]), None)
        if selected_range:
            range_name, districts_in_range = selected_range
            # If the user clicked a range, display a new select menu with the districts in that range
            options = [discord.SelectOption(label=district) for district in districts_in_range]

            # Create select menu for the user
            select = discord.ui.Select(placeholder=f"Choose a district from {range_name}", options=options)

            async def select_callback(interaction: discord.Interaction):
                district = select.values[0]
                user_alerts[interaction.user.id] = user_alerts.get(interaction.user.id, set())
                user_alerts[interaction.user.id].add(district)
                save_user_alerts()
                await interaction.response.send_message(f"Alerts set for: {district}", ephemeral=True)

            select.callback = select_callback

            # Create the view for the select menu and add the select item
            select_view = discord.ui.View()
            select_view.add_item(select)

            await interaction.response.send_message(
                f"Please select a district from {range_name}.", ephemeral=True, view=select_view
            )

    # Assign the button callback to the buttons
    for button in buttons:
        button.callback = button_callback

    # Send the initial message with buttons
    await interaction.response.send_message(
        "Please choose a letter range to select your district:", ephemeral=True, view=view
    )

# Slash command to check for closures (for testing purposes)
@bot.tree.command(name="check", description="Check for current school closures.")
async def check(interaction: discord.Interaction):
    url = "https://www.nbcconnecticut.com/weather/school-closings/"
    await bot.send_school_closures(url)
    await interaction.response.send_message("School closures have been checked and alerts have been sent.")

# Send it.
bot.run(TOKEN)
