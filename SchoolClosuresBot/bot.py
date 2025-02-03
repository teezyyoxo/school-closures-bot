# School Closures Bot
# Created by @PBandJamf
# Version 2.3.2

# This bot is currently configured for use with NBC Connecticut and all districts within.
# See districts.json for the current list (parsed/scraped directly from the site around 7am EST on 3 Feb 2025 when most/all closures were posted.)
# Stay warm, drive safe, and remember: #BlackIceAintLoyal.

# CHANGELOG
# Version 2.3.2
# Significantly revised (sic: simplified) the /setalerts interaction.

# Version 2.3.1
# - Realized a lot of these issues were fixed just by re-inviting the bot to the server.
# - Fixed issue with 'unknown integration' error by ensuring proper sync of slash commands.
# - Re-added the `/check` slash command for manually checking school closures.
# - Removed redundant `!check` command support, keeping only slash commands.
# - Improved command handling and bot synchronization after startup.
# - Cleaned up command registration logic to avoid conflicts with existing commands.

# Version 2.3.0
# - Removed all "!check" commands and logic in favor of slash (/) commands only.
# - Removed the on_message event logic for "!check".
# - Streamlined bot to only use slash commands for interaction.

# Version 2.2.2
# - Added `message_content` intent to access message content in DMs.
# - This resolves the "Privileged Message Content Intent" warning.
# - Limited the number of school districts to 25 in the button-based interaction.
# - This prevents exceeding Discord's maximum of 25 options in interactive messages.
# - Refined the button callback logic to ensure users can set alerts for multiple districts.
# - Added follow-up prompts asking users if they want to configure additional alerts after making a selection.
# - Ensured user alerts are stored persistently in a `user_alerts.json` file, and changes are saved after each update.
# - Added feedback for users when configuring multiple district alerts.
# - Created additional buttons for users to decide whether they want to configure more alerts after setting their preferences.
# - Addressed the issue with multiple district alerts not being stored correctly.
# - Fixed issues related to sending too many interactive options in the message.
# - Improved the `/setalerts` command to handle district search and button-based selection more efficiently.

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

            await channel.send("@everyone Closures detected! DM me `/setalerts [district]` to set up private alerts for specific districts.")
            
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

# Slash command to check for closures (triggered manually)
@bot.tree.command(name="check", description="Check for current school closures.")
async def check(interaction: discord.Interaction):
    url = "https://www.nbcconnecticut.com/weather/school-closings/"
    await interaction.client.send_school_closures(url)
    await interaction.response.send_message("School closures have been checked and alerts have been sent.")

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
    await interaction.response.send_message(
        f"Alerts set for: {district}\n\nTo add more alerts, please run the `/setalerts` command again.",
        ephemeral=True
    )

async def finish_alerts_configuration(interaction: discord.Interaction):
    # If the user is done, let them know
    await interaction.response.send_message(
        "Your alert configuration is complete! Stay updated on school closures.",
        ephemeral=True
    )

# Send it.
bot.run(TOKEN)
