# Telegram CC Scraper Bot

A powerful Telegram bot designed to extract and organize credit card information from Telegram channels. Built with Pyrogram and optimized for deployment on Render.com.

## Features

- **Channel Scraping**: Extract credit card information from any accessible Telegram channel
- **Customizable Limits**: Set different extraction limits for regular users and administrators
- **BIN Filtering**: Filter cards starting with specific numbers (BINs)
- **Duplicate Removal**: Automatically detects and removes duplicate entries
- **Formatted Output**: Delivers results as a formatted text file
- **Deployment Ready**: Configured for easy deployment on Render.com

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Telegram API credentials (API ID and API Hash) from [my.telegram.org](https://my.telegram.org)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Pyrogram session string for a user account

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/telegram-cc-scraper.git
   cd telegram-cc-scraper
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a config.py file with your credentials:
   ```python
   # API Credentials
   API_ID = 12345                  # Your API ID from my.telegram.org
   API_HASH = "your_api_hash"      # Your API Hash from my.telegram.org
   BOT_TOKEN = "your_bot_token"    # Your bot token from @BotFather
   SESSION_STRING = "your_session_string"  # Your Pyrogram session string

   # Admin Settings
   ADMIN_IDS = [12345678, 87654321]  # List of admin user IDs
   DEFAULT_LIMIT = 50                # Default card limit for regular users
   ADMIN_LIMIT = 500                 # Card limit for admins

   # User Info
   USERNAME = "your_username"        # Your Telegram username (without @)
   NAME = "Your Name"                # Your display name
   ```

### Generating a Session String

To generate a Pyrogram session string for the user account:

1. Create a file named `get_session.py`:
   ```python
   from pyrogram import Client

   print("Pyrogram Session String Generator")
   print("--------------------------------\n")

   API_ID = input("Enter your API ID: ")
   API_HASH = input("Enter your API HASH: ")

   with Client(
       "my_account",
       api_id=API_ID,
       api_hash=API_HASH,
       in_memory=True
   ) as app:
       print("\nYour SESSION_STRING is:")
       print(app.export_session_string())
       print("\nKeep this string secret!")
   ```

2. Run the script and follow the prompts:
   ```
   python get_session.py
   ```

3. Enter your phone number and verification code when prompted.

### Running the Bot

1. Start the bot:
   ```
   python scrapper.py
   ```

2. Open your Telegram bot and start using the commands.

## Usage

- `/scr [channel] [amount]` - Scrape cards from a channel (up to the limit)
- `/scr [channel] [amount] [prefix]` - Scrape cards that start with a specific prefix

Examples:
```
/scr @channel_name 50
/scr https://t.me/channel_name 100
/scr @channel_name 30 45678
```

## Deploying to Render.com

This bot is optimized for deployment on Render.com as a background worker.

1. Create a new repository with your code.

2. Sign up for a Render account and create a new Background Worker.

3. Connect to your GitHub repository.

4. Set up the following environment variables:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
   - `SESSION_STRING`
   - `ADMIN_IDS` (comma-separated)
   - `DEFAULT_LIMIT`
   - `ADMIN_LIMIT`
   - `USERNAME`
   - `NAME`

5. Set the build command: `pip install -r requirements.txt`

6. Set the start command: `python scrapper.py`

## Important Changes for Production

Before deploying to Render.com, make the following changes to `scrapper.py` to prevent SESSION_REVOKED errors:

1. Create a temp directory for file operations:
   ```python
   # Create temp directory if it doesn't exist
   os.makedirs('temp', exist_ok=True)
   ```

2. Update the user client initialization:
   ```python
   user = Client(
       "user_session",
       api_id=API_ID,  # Add these two lines
       api_hash=API_HASH,  # Add these two lines
       session_string=SESSION_STRING,
       workers=1000,
       no_updates=True  # Add this to prevent SESSION_REVOKED error
   )
   ```

3. Update file paths to use the temp directory:
   ```python
   safe_channel_name = ''.join(c if c.isalnum() else '_' for c in channel_name)
   filename = os.path.join('temp', f"Luis_{safe_channel_name}.txt")
   ```

4. Add error handling for file operations.

## Troubleshooting

- **SESSION_REVOKED Error**: If you see this error, generate a new session string and update your config.
- **Bot Not Responding**: Make sure your bot token is correct and the bot is running.
- **Channel Access Errors**: Ensure the user account has access to the target channel.

## Requirements

Create a `requirements.txt` file containing:
```
pyrogram>=2.0.0
tgcrypto
python-dotenv
```

## License

This project is for educational purposes only. Use responsibly and ethically.

## Disclaimer

This tool is provided for educational purposes only. Users are responsible for ensuring their use complies with Telegram's Terms of Service and all applicable laws.
