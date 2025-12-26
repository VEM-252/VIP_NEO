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
import random
import string
from time import time

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS, lyrical
from VIPMUSIC import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from VIPMUSIC.core.call import VIP
from VIPMUSIC.utils import seconds_to_min, time_to_seconds
from VIPMUSIC.utils.channelplay import get_channeplayCB
from VIPMUSIC.utils.database import add_served_chat, get_assistant, is_video_allowed
from VIPMUSIC.utils.decorators.language import languageCB
from VIPMUSIC.utils.decorators.play import PlayWrapper
from VIPMUSIC.utils.formatters import formats
from VIPMUSIC.utils.inline.play import (
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from VIPMUSIC.utils.inline.playlist import botplaylist_markup
from VIPMUSIC.utils.logger import play_logs
from VIPMUSIC.utils.stream.stream import stream

user_last_message_time = {}
user_command_count = {}
SPAM_WINDOW_SECONDS = 5
SPAM_THRESHOLD = 2


@app.on_message(
    filters.command(
        [
            "play",
            "vplay",
            "cplay",
            "cvplay",
            "playforce",
            "vplayforce",
            "cplayforce",
            "cvplayforce",
        ],
        prefixes=["/", "!", "%", ",", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client, message: Message, _, chat_id, video, channel, playmode, url, fplay
):
    # --- FORCE AUDIO/VIDEO MODE LOGIC ---
    command_check = message.command[0].lower()
    if command_check.startswith("v") or command_check.startswith("cv"):
        video = True
    else:
        video = False
    # --- FIX END ---

    userbot = await get_assistant(message.chat.id)
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ sᴘᴀᴍ, ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄᴏɴᴅs.**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    await add_served_chat(message.chat.id)
    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    plist_id = None
    slider = None
    plist_type = None
    spotify = None
    user_name = message.from_user.first_name
    
    # Telegram Audio/Voice Logic (Video Tagging Block Removed)
    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )

    if audio_telegram:
        if audio_telegram.file_size > config.TG_AUDIO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_5"])
        duration_min = seconds_to_min(audio_telegram.duration)
        if (audio_telegram.duration) > config.DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, duration_min)
            )
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(audio_telegram, audio=True)
            dur = await Telegram.get_duration(audio_telegram)
            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": dur,
            }
            try:
                await stream(
                    _, mystic, user_id, details, chat_id, user_name,
                    message.chat.id, video=video, streamtype="telegram", forceplay=fplay,
                )
            except Exception as e:
                return await mystic.edit_text(f"Error: {e}")
            return await mystic.delete()
        return

    # URL Streaming Logic
    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, plist_type = "playlist", "yt"
                plist_id = (url.split("=")[1]).split("&")[0] if "&" in url else url.split("=")[1]
                img, cap = config.PLAYLIST_IMG_URL, _["play_10"]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, img = "youtube", details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
        
        elif await Spotify.valid(url):
            spotify = True
            if "track" in url:
                try: details, track_id = await Spotify.track(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, img = "youtube", details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                try: details, plist_id = await Spotify.playlist(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, plist_type, img = "playlist", "spplay", config.SPOTIFY_PLAYLIST_IMG_URL
                cap = _["play_12"].format(message.from_user.first_name)
            elif "album" in url:
                try: details, plist_id = await Spotify.album(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, plist_type, img = "playlist", "spalbum", config.SPOTIFY_ALBUM_IMG_URL
                cap = _["play_12"].format(message.from_user.first_name)
            else: return await mystic.edit_text(_["play_17"])

        elif await Apple.valid(url):
            if "album" in url or "track" in url:
                try: details, track_id = await Apple.track(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, img = "youtube", details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                spotify = True
                try: details, plist_id = await Apple.playlist(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype, plist_type, cap, img = "playlist", "apple", _["play_13"].format(message.from_user.first_name), url
            else: return await mystic.edit_text(_["play_17"])

        elif await Resso.valid(url):
            try: details, track_id = await Resso.track(url)
            except: return await mystic.edit_text(_["play_3"])
            streamtype, img = "youtube", details["thumb"]
            cap = _["play_11"].format(details["title"], details["duration_min"])

        elif await SoundCloud.valid(url):
            try: details, track_path = await SoundCloud.download(url)
            except: return await mystic.edit_text(_["play_3"])
            if details["duration_sec"] > config.DURATION_LIMIT:
                return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, details["duration_min"]))
            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype="soundcloud", forceplay=fplay)
            except Exception as e: return await mystic.edit_text(f"Error: {e}")
            return await mystic.delete()
        
        else:
            try:
                await stream(_, mystic, user_id, url, chat_id, user_name, message.chat.id, video=video, streamtype="index", forceplay=fplay)
            except Exception as e: return await mystic.edit_text(f"Error: {e}")
            return await mystic.delete()

    # Search Query Logic
    else:
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(_["playlist_1"], reply_markup=InlineKeyboardMarkup(buttons))
        slider = True
        query = message.text.split(None, 1)[1]
        if "-v" in query:
            query = query.replace("-v", "")
            video = True
        try:
            details, track_id = await YouTube.track(query)
        except: return await mystic.edit_text(_["play_3"])
        streamtype = "youtube"

    if str(playmode) == "Direct":
        if not plist_type:
            if details["duration_min"]:
                if time_to_seconds(details["duration_min"]) > config.DURATION_LIMIT:
                    return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, details["duration_min"]))
            else:
                buttons = livestream_markup(_, track_id, user_id, "v" if video else "a", "c" if channel else "g", "f" if fplay else "d")
                return await mystic.edit_text(_["play_15"], reply_markup=InlineKeyboardMarkup(buttons))
        try:
            await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype=streamtype, spotify=spotify, forceplay=fplay)
        except Exception as e: return await mystic.edit_text(f"Error: {e}")
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    else:
        if plist_type:
            ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(_, ran_hash, user_id, plist_type, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            return await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            if slider:
                buttons = slider_markup(_, track_id, user_id, query, 0, "c" if channel else "g", "f" if fplay else "d")
                await mystic.delete()
                return await message.reply_photo(photo=details["thumb"], caption=_["play_11"].format(details["title"].title(), details["duration_min"]), reply_markup=InlineKeyboardMarkup(buttons))
            else:
                buttons = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")
                await mystic.delete()
                return await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))

# --- CALLBACKS ---

@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
    try: chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except: return
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    try: details, track_id = await YouTube.track(vidid, True)
    except: return await mystic.edit_text(_["play_3"])
    video = True if mode == "v" else False
    try:
        await stream(_, mystic, user_id, details, chat_id, user_name, CallbackQuery.message.chat.id, video, streamtype="youtube", forceplay=True if fplay == "f" else None)
    except Exception as e: return await mystic.edit_text(f"Error: {e}")
    await mystic.delete()

@app.on_callback_query(filters.regex("AnonymousAdmin") & ~BANNED_USERS)
async def anonymous_check(client, CallbackQuery):
    await CallbackQuery.answer("ʏᴏᴜ'ʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ. ᴜsᴇ ᴜsᴇʀ ᴀᴄᴄᴏᴜɴᴛ.", show_alert=True)

@app.on_callback_query(filters.regex("VIPPlaylists") & ~BANNED_USERS)
@languageCB
async def play_playlists_command(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, user_id, ptype, mode, cplay, fplay = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
    try: chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except: return
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    videoid = lyrical.get(videoid)
    video = True if mode == "v" else False
    spotify = False if ptype == "yt" else True
    try:
        if ptype == "yt": result = await YouTube.playlist(videoid, config.PLAYLIST_FETCH_LIMIT, user_id, True)
        elif ptype == "spplay": result, spotify_id = await Spotify.playlist(videoid)
        elif ptype == "spalbum": result, spotify_id = await Spotify.album(videoid)
        elif ptype == "spartist": result, spotify_id = await Spotify.artist(videoid)
        elif ptype == "apple": result, apple_id = await Apple.playlist(videoid, True)
        await stream(_, mystic, user_id, result, chat_id, user_name, CallbackQuery.message.chat.id, video, streamtype="playlist", spotify=spotify, forceplay=True if fplay == "f" else None)
    except Exception as e: return await mystic.edit_text(f"Error: {e}")
    await mystic.delete()

@app.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_queries(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, rtype, query, user_id, cplay, fplay = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
    rtype = int(rtype)
    query_type = (rtype + 1) if what == "F" else (rtype - 1)
    if query_type > 9: query_type = 0
    if query_type < 0: query_type = 9
    title, duration_min, thumbnail, vidid = await YouTube.slider(query, query_type)
    buttons = slider_markup(_, vidid, user_id, query, query_type, cplay, fplay)
    med = InputMediaPhoto(media=thumbnail, caption=_["play_11"].format(title.title(), duration_min))
    return await CallbackQuery.edit_message_media(media=med, reply_markup=InlineKeyboardMarkup(buttons))

__MODULE__ = "Plᴀʏ"
__HELP__ = """
<b>★ /play</b> [name] - Play Audio
<b>★ /vplay</b> [name] - Play Video
<b>★ /cplay</b> - Channel Play (Audio)
<b>★ /cvplay</b> - Channel Play (Video)
"""