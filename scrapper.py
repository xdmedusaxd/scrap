import re
import os
import asyncio
from urllib.parse import urlparse
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from config import (
    API_ID,
    API_HASH,
    SESSION_STRING,
    BOT_TOKEN,
    ADMIN_IDS,
    DEFAULT_LIMIT,
    ADMIN_LIMIT,
    USERNAME,
    NAME,
)

# Create temp directory if it doesn't exist
os.makedirs('temp', exist_ok=True)

bot = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1000,
    parse_mode=ParseMode.HTML
)

# Fixed to prevent SESSION_REVOKED error
user = Client(
    "user_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=1000,
    no_updates=True  # This prevents the SESSION_REVOKED error
)

def remove_duplicates(messages):
    unique_messages = list(set(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

async def scrape_messages(client, channel_id, limit, start_number=None):
    messages = []
    count = 0
    pattern = r'\d{16}\D*\d{2}\D*\d{2,4}\D*\d{3,4}'

    async for message in user.search_messages(channel_id):
        if count >= limit:
            break
        text = message.text or message.caption
        if not text:
            continue

        matched = re.findall(pattern, text)
        if not matched:
            continue

        formatted = []
        for match in matched:
            digits = re.findall(r'\d+', match)
            if len(digits) == 4:
                card, mo, year, cvv = digits
                year = year[-2:]
                formatted.append(f"{card}|{mo}|{year}|{cvv}")

        formatted = formatted[:limit - count]
        messages.extend(formatted)
        count += len(formatted)

    if start_number:
        messages = [msg for msg in messages if msg.startswith(start_number)]

    return messages[:limit]

@bot.on_message(filters.command(["scr", "src"]))  # Added "src" to handle typos
async def handle_scrape(client, message):
    args = message.text.split()[1:]

    if len(args) < 2 or len(args) > 3:
        await message.reply_text("<b>⚠️ Usage: /scr [channel] [amount]</b>")
        return

    channel_identifier = args[0]
    try:
        limit = int(args[1])
    except ValueError:
        await message.reply_text("<b>❌ Invalid amount specified</b>")
        return

    user_id = message.from_user.id
    max_limit = ADMIN_LIMIT if user_id in ADMIN_IDS else DEFAULT_LIMIT
    if limit > max_limit:
        await message.reply_text(f"<b>❌ Maximum allowed limit is {max_limit}</b>")
        return

    start_number = args[2] if len(args) == 3 else None

    try:
        # Handle channel IDs in various formats
        if channel_identifier.startswith('-100') and channel_identifier[1:].isdigit():
            channel_id = int(channel_identifier)
        elif channel_identifier.isdigit():
            # Handle shortened IDs without -100
            channel_id = int(f"-100{channel_identifier}")
        else:
            # It's a username or URL
            parsed = urlparse(channel_identifier)
            channel_username = parsed.path.lstrip('/') if not parsed.scheme else channel_identifier
            chat = await user.get_chat(channel_username)
            channel_id = chat.id

        chat = await user.get_chat(channel_id)
        channel_name = chat.title
    except Exception as e:
        await message.reply_text(f"<b>❌ Error accessing channel: {e}</b>")
        return

    temp_msg = await message.reply_text("<b>🔍 Scraping messages..!! Please wait</b>")

    try:
        results = await scrape_messages(user, chat.id, limit, start_number)
    except Exception as e:
        await temp_msg.edit_text(f"<b>❌ Scraping failed: {e}</b>")
        return

    unique_results, duplicates = remove_duplicates(results)

    if not unique_results:
        await temp_msg.edit_text("<b>❌ No valid cards found</b>")
        return

    # Use temp directory for file storage
    safe_channel_name = channel_name.replace(' ', '_').replace('/', '_')
    filename = os.path.join('temp', f"SwiftieXD_{safe_channel_name}.txt")

    with open(filename, "w") as f:
        f.write("\n".join(unique_results))

    caption = (
        f"<b>✅ Successfully Scraped Cards</b>\n"
        f"<b>━━━━━━━━━━━━━━━━</b>\n"
        f"<b>[ϟ] Source :</b> <code>{channel_name}</code>\n"
        f"<b>[ϟ] Amount :</b> <code>{len(unique_results)}</code>\n"
        f"<b>[ϟ] Duplicates :</b> <code>{duplicates}</code>\n"
        f"<b>━━━━━━━━━━━━━━━━</b>\n"
        f"<b>[ϟ] Dev :</b> <a href='https://t.me/{USERNAME}'>{NAME}</a>\n"
    )

    await message.reply_document(
        document=filename,
        caption=caption
    )
    await temp_msg.delete()

    # Clean up with error handling
    try:
        os.remove(filename)
    except Exception:
        pass

# Add a /start command for better user experience
@bot.on_message(filters.command(["start"]))
async def start_command(client, message):
    await message.reply_text(
        "<b>👋 Welcome to Card Scraper Bot!</b>\n\n"
        "<b>Commands:</b>\n"
        "• /scr [channel/ID] [amount] - Scrape cards from a channel\n"
        "• /scr [channel/ID] [amount] [prefix] - Filter by prefix\n\n"
        f"<b>Examples:</b>\n"
        f"• <code>/scr @channelname 50</code>\n"
        f"• <code>/scr -1001234567890 50</code>\n"
        f"• <code>/scr 1234567890 50</code>\n\n"
        f"<b>Developed by:</b> <a href='https://t.me/{USERNAME}'>{NAME}</a>"
    )

if __name__ == "__main__":
    user.start()
    bot.run()
