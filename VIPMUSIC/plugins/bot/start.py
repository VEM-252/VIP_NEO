#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import time

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_string
from VIPMUSIC import HELPABLE, Telegram, YouTube, app, userbot
from VIPMUSIC.misc import SUDOERS, _boot_
from VIPMUSIC.plugins.play.playlist import del_plist_msg
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


@app.on_message(group=-1)
async def ban_new(client, message):
    user_id = message.from_user.id if message.from_user else 777000
    if await is_banned_user(user_id):
        try:
            await message.chat.ban_member(user_id)
            await message.reply_text("😳")
        except:
            pass


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    
    # Personal Chat Reaction (🕊️ Emoji)
    try:
        await message.react("🕊️")
    except:
        pass

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
            return await message.reply_photo(photo=START_IMG_URL, caption=_["help_1"], reply_markup=keyboard)
            
        if name[0:4] == "song":
            return await message.reply_text(_["song_2"])
            
        if name == "mkdwn_help":
            return await message.reply(MARKDOWN, parse_mode=ParseMode.HTML)
            
        if name == "greetings":
            return await message.reply(WELCOMEHELP, parse_mode=ParseMode.HTML)

        if name[0:3] == "sta":
            m = await message.reply_text("🔎 ғᴇᴛᴄʜɪɴɢ sᴛᴀᴛs...")
            stats = await get_userss(message.from_user.id)
            if not stats:
                return await m.edit(_["ustats_1"])

            def get_stats():
                msg = ""
                limit = 0
                results = {}
                for i in stats:
                    top_list = stats[i]["spot"]
                    results[str(i)] = top_list
                list_arranged = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
                tota = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10: continue
                    if limit == 0: videoid = vidid
                    limit += 1
                    details = stats.get(vidid)
                    title = (details["title"][:35]).title()
                    if vidid == "telegram":
                        msg += f"🔗[ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇs]({config.SUPPORT_GROUP}) ** played {count} ᴛɪᴍᴇs**\n\n"
                    else:
                        msg += f"🔗 [{title}](https://www.youtube.com/watch?v={vidid}) ** played {count} times**\n\n"
                return videoid, _["ustats_2"].format(len(stats), tota, limit) + msg

            try:
                videoid, msg = await loop.run_in_executor(None, get_stats)
                thumbnail = await YouTube.thumbnail(videoid, True)
                await m.delete()
                await message.reply_photo(photo=thumbnail, caption=msg)
            except:
                pass
            return

        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            return

        if name[0:3] == "inf":
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                link = result["link"]
            
            key = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 ᴡᴀᴛᴄʜ", url=link), InlineKeyboardButton("🔄 ᴄʟᴏsᴇ", callback_data="close")]])
            await message.reply_photo(photo=thumbnail, caption=f"❇️**ᴛɪᴛʟᴇ:** {title}\n⏳**ᴅᴜʀᴀᴛɪᴏɴ:** {duration} Mins", reply_markup=key)
            return

    else:
        out = private_panel(_)
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
        
        # --- LOGGER GROUP LOG (BY ASSISTANT) ---
        if await is_on_off(config.LOG):
            try:
                # Assistant ID (Userbot) message bhejegi
                await userbot.one.send_message(
                    config.LOG_GROUP_ID,
                    f"👤 {message.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                    f"**Usᴇʀ ID:** `{message.from_user.id}`\n"
                    f"**Usᴇʀɴᴀᴍᴇ:** @{message.from_user.username}"
                )
            except:
                # Fallback: Agar assistant nahi bhej payi toh Bot bhej dega
                try:
                    await app.send_message(config.LOG_GROUP_ID, f"👤 {message.from_user.mention} started the bot.")
                except:
                    pass


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    out = alive_panel(_)
    uptime = get_readable_time(int(time.time() - _boot_))
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_7"].format(app.mention, uptime),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(chat_id):
            await message.reply_text("ᴛʜɪs ʙᴏᴛ's ᴘʀɪᴠᴀᴛᴇ ᴍᴏᴅᴇ ɪs ᴇɴᴀʙʟᴇᴅ.")
            return await app.leave_chat(chat_id)
    else:
        await add_served_chat(chat_id)
        
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_5"])
                    return await app.leave_chat(chat_id)
                if chat_id in await blacklisted_chats():
                    await message.reply_text(_["start_6"].format(f"https://t.me/{app.username}?start=sudolist"))
                    return await app.leave_chat(chat_id)
                
                userbot_id = await get_assistant(chat_id)
                out = start_pannel(_)
                await message.reply_text(_["start_2"].format(app.mention, userbot_id.username, userbot_id.id), reply_markup=InlineKeyboardMarkup(out))
            
            if member.id in config.OWNER_ID:
                await message.reply_text(_["start_3"].format(app.mention, member.mention))
            if member.id in SUDOERS:
                await message.reply_text(_["start_4"].format(app.mention, member.mention))
        except:
            pass

__MODULE__ = "Boᴛ"
__HELP__ = "★ /start - Start the bot\n★ /stats - Check global stats\n★ /lyrics - Search lyrics"
