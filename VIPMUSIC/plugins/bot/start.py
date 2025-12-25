import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_string
from VIPMUSIC import HELPABLE, YouTube, app
from VIPMUSIC.misc import SUDOERS, _boot_
from VIPMUSIC.plugins.sudo.sudoers import sudoers_list
from VIPMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_assistant,
    get_lang,
    get_userss,
    is_banned_user,
    is_on_off,
    is_served_private_chat,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
from VIPMUSIC.utils.functions import MARKDOWN, WELCOMEHELP
from VIPMUSIC.utils.inline import alive_panel, private_panel, start_pannel

from .help import paginate_modules

loop = asyncio.get_running_loop()

# --- Auto Ban Logic ---
@app.on_message(group=-1)
async def ban_new(client, message):
    user_id = message.from_user.id if message.from_user else 777000
    if await is_banned_user(user_id):
        try:
            await message.chat.ban_member(user_id)
        except:
            pass

# --- Private Start Handler ---
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    
    # Deep Linking Logic
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        
        # Help Menu
        if name.startswith("help"):
            keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
            return await (message.reply_photo(photo=START_IMG_URL, caption=_["help_1"], reply_markup=keyboard) 
                          if START_IMG_URL else message.reply_text(text=_["help_1"], reply_markup=keyboard))

        # Song Command Info
        if name.startswith("song"):
            return await message.reply_text(_["song_2"])

        # Markdown & Greetings Help
        if name == "mkdwn_help":
            return await message.reply(MARKDOWN, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        if name == "greetings":
            return await message.reply(WELCOMEHELP, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        # Personal Stats
        if name.startswith("sta"):
            m = await message.reply_text("✨ `Fetching your stats...`")
            stats = await get_userss(message.from_user.id)
            if not stats:
                return await m.edit(_["ustats_1"])

            async def get_stats_data():
                results = {str(i): stats[i]["spot"] for i in stats}
                list_arranged = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
                msg, limit, tota, videoid = "", 0, 0, None
                
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit < 10:
                        if limit == 0: videoid = vidid
                        limit += 1
                        title = (stats[vidid]["title"][:30]).title() if vidid != "telegram" else "Telegram Files"
                        link = f"https://www.youtube.com/watch?v={vidid}" if vidid != "telegram" else config.SUPPORT_GROUP
                        msg += f"🔹 [{title}]({link}) | Played: `{count}`\n"
                
                return videoid, _["ustats_2"].format(len(stats), tota, limit) + "\n" + msg

            try:
                videoid, stats_msg = await get_stats_data()
                thumbnail = await YouTube.thumbnail(videoid, True)
                await m.delete()
                await message.reply_photo(photo=thumbnail, caption=stats_msg)
            except:
                await m.edit("❌ Failed to load stats.")
            return

        # Sudoers List
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return

        # Video Information
        if name.startswith("inf"):
            query = name.replace("info_", "", 1)
            m = await message.reply_text("🔎 `Searching Video Info...`")
            try:
                results = VideosSearch(f"https://www.youtube.com/watch?v={query}", limit=1)
                res = await results.next()
                result = res["result"][0]
                title, thumb, link = result["title"], result["thumbnails"][0]["url"].split("?")[0], result["link"]
                key = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 Watch Now", url=link), InlineKeyboardButton("🗑 Close", callback_data="close")]])
                await m.delete()
                await message.reply_photo(photo=thumb, caption=f"**📌 Title:** {title}\n**🔗 Link:** [Click Here]({link})", reply_markup=key)
            except:
                await m.edit("❌ Info not found.")
            return

    # Normal Start (No Deep Link)
    out = private_panel(_)
    await message.reply_photo(
        photo=START_IMG_URL,
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
    )
    if await is_on_off(config.LOG):
        try:
            await app.send_message(config.LOG_GROUP_ID, f"👤 {message.from_user.mention} Started the bot.\n🆔 ID: `{message.from_user.id}`")
        except: pass

# --- Group Start Handler ---
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def group_start(client, message: Message, _):
    uptime = get_readable_time(int(time.time() - _boot_))
    out = alive_panel(_)
    await message.reply_photo(
        photo=START_IMG_URL,
        caption=_["start_7"].format(app.mention, uptime),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)

# --- Welcome & Private Mode Handler ---
@app.on_message(filters.new_chat_members, group=-1)
async def welcome_handler(client, message: Message):
    chat_id = message.chat.id
    
    # Private Bot Mode Check
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(chat_id):
            await message.reply_text("🔒 **Bot Private Mode Enabled.**\nOnly authorized groups can use me.")
            return await app.leave_chat(chat_id)
    else:
        await add_served_chat(chat_id)
        
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)
            
            # If Bot joined
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_5"])
                    return await app.leave_chat(chat_id)
                
                if chat_id in await blacklisted_chats():
                    await message.reply_text(_["start_6"].format(f"https://t.me/{app.username}?start=sudolist"))
                    return await app.leave_chat(chat_id)
                
                userbot = await get_assistant(chat_id)
                await message.reply_text(
                    _["start_2"].format(app.mention, userbot.username, userbot.id), 
                    reply_markup=InlineKeyboardMarkup(start_pannel(_))
                )
            
            # Special Mentions
            if member.id in config.OWNER_ID:
                await message.reply_text(_["start_3"].format(app.mention, member.mention))
            elif member.id in SUDOERS:
                await message.reply_text(_["start_4"].format(app.mention, member.mention))
        except:
            pass

__MODULE__ = "Bot"
__HELP__ = """
✨ **Comfort Music Bot Commands** ✨

📊 `/stats` - Check global music stats.
👑 `/sudolist` - View bot managers.
📝 `/lyrics [Name]` - Get song lyrics instantly.
📥 `/song [Name]` - Download any track/video.
🎵 `/player` - Control the music panel.
📜 `/queue` - Check upcoming songs.
"""
