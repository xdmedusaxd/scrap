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

# FIXED: Added api_id, api_hash and no_updates=True to prevent SESSION_REVOKED
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

@bot.on_message(filters.command(["scr"]))
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
        parsed = urlparse(channel_identifier)
        channel_username = parsed.path.lstrip('/') if not parsed.scheme else channel_identifier
        chat = await user.get_chat(channel_username)
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
    
    # FIXED: Added safer file path handling with temp directory
    safe_channel_name = ''.join(c if c.isalnum() else '_' for c in channel_name)
    filename = os.path.join('temp', f"Luis_{safe_channel_name}.txt")
    
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
    
    try:
        await message.reply_document(
            document=filename,
            caption=caption
        )
    except Exception as e:
        await message.reply_text(f"<b>❌ Error sending file: {e}</b>\n\n{caption}")
    
    await temp_msg.delete()
    
    # FIXED: Added error handling for file removal
    try:
        os.remove(filename)
    except Exception as e:
        pass

if __name__ == "__main__":
    user.start()
    bot.run()
