# useful-discord-bots
these all probably exist in one way, shape, or form, but *these* are MINE.


# SchoolClosuresBot

A Discord bot to send school closure updates and alerts based on districts from NBC Connecticut. This bot allows users to set alerts for specific school districts and receive notifications when closures or delays are reported.

## Features

-   **/check**: Manually checks for school closures and sends the updates to the configured channel.
-   **/setalerts**: Allows users to configure alerts for specific school districts.
-   **User Alerts**: Configured alerts are saved in `user_alerts.json` and are persistent between bot restarts.

## Requirements

-   Python 3.9+
-   Required Python packages (install via `pip`):
    -   `discord.py` (for interacting with the Discord API)
    -   `python-dotenv` (for loading environment variables from `.env` file)
    -   `requests` (for making HTTP requests to fetch school closure data)
    -   `beautifulsoup4` (for parsing the webpage with school closures)

## Setup Instructions

### 1. Clone this repository

bash

CopyEdit

`git clone https://github.com/your-repo/SchoolClosuresBot.git
cd SchoolClosuresBot` 

### 2. Install the required Python packages

Create a virtual environment (optional but recommended):

bash

CopyEdit

`python3 -m venv venv
source venv/bin/activate  # On Windows use 'venv\Scripts\activate'` 

Install dependencies:

bash

CopyEdit

`pip install -r requirements.txt` 

### 3. Configure the `.env` file

Create a `.env` file in the root directory of the project, and include the following variables:

bash

CopyEdit

`DISCORD_TOKEN=your_discord_bot_token
CHANNEL_ID=your_discord_channel_id` 

-   **DISCORD_TOKEN**: You can get this token by creating a bot on the Discord Developer Portal and adding the bot to your server.
-   **CHANNEL_ID**: This is the ID of the channel where school closure alerts will be posted. You can get this by enabling "Developer Mode" in Discord and right-clicking on the channel to copy the ID.

### 4. Configure `districts.json`

Make sure that the `districts.json` file is updated with the valid school districts for your region. This is the list of districts that the bot can match with the closures reported by NBC Connecticut.

-   If you're using a different news site or scraping source, update the `districts.json` file accordingly.

### 5. Configure the Scraper (Optional)

The bot uses `scraperNBC.py` to fetch school closure data from NBC Connecticut. If you're using a different source or webpage for scraping, you may need to update the `fetch_school_closures` function in `scraperNBC.py` to match the structure of the website you want to scrape from. Make sure the URL used for scraping and the scraping logic are correctly aligned with the new source.

### 6. `user_alerts.json`

This file stores the alerts for each user, mapping their Discord user ID to a list of districts they have configured for alerts. The file is automatically created and updated when users set alerts using the `/setalerts` command.

### 7. Running the Bot

To start the bot, simply run:

bash

CopyEdit

`python bot.py` 

Once the bot is running, it will automatically sync slash commands and begin listening for user interactions. Make sure the bot is invited to your Discord server and has permissions to read and send messages in the appropriate channel.

### 8. Commands

-   `/setalerts [district]`: Sets up alerts for a specific district. Users can search for districts by name, and the bot will provide a list of matching districts to choose from.
-   `/check`: Manually checks for school closures and sends the updates to the configured channel. This can also be used by server administrators to check for closures on demand.

## Notes

-   **Customizing the Scraper**: The bot currently scrapes school closures from NBC Connecticut. If you are using a different news site, you'll need to adjust the scraping code in `scraperNBC.py` to match the HTML structure and data format of the new site. This may involve modifying the `fetch_school_closures` function to properly extract closure information.
    
-   **Error Handling**: If there are any issues with fetching closures (e.g., the website structure changes or the bot encounters a network error), the bot will print an error message to the console, and you may need to troubleshoot or update the scraper accordingly.
    

## Contribution

If you'd like to contribute to this project, feel free to fork the repository, create a pull request, and suggest any improvements. Bug reports and feature requests are always welcome!