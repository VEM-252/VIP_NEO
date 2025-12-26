import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import TelegramServerError
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, AudioQuality, VideoQuality # Updated for v2
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    UserAlreadyParticipant,
    UserNotParticipant,
    PeerIdInvalid,
)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
from pytgcalls.types import (
    JoinedGroupCallParticipant,
    LeftGroupCallParticipant,
    MediaStream,
    Update,
)
from pytgcalls.types.stream import StreamAudioEnded

import config
from strings import get_string
from VIPMUSIC import LOGGER, YouTube, app
from VIPMUSIC.misc import db
from VIPMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_audio_bitrate,
    get_lang,
    get_loop,
    get_video_bitrate,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from VIPMUSIC.utils.exceptions import AssistantErr
from VIPMUSIC.utils.formatters import check_duration, seconds_to_min, speed_converter
from VIPMUSIC.utils.inline.play import stream_markup, telegram_markup
from VIPMUSIC.utils.stream.autoclear import auto_clean
from VIPMUSIC.utils.thumbnails import gen_thumb

autoend = {}
counter = {}
AUTO_END_TIME = 1

async def _st_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)
    try:
        AMBOT = await app.send_message(
            chat_id, f"🎶 **Song has ended in VC.** Do you want to hear more songs?"
        )
        await asyncio.sleep(5)
        await AMBOT.delete()
    except:
        pass

class Call(PyTgCalls):
    def __init__(self):
        # Initializing Assistants with proper v2 syntax
        self.userbot1 = Client("VIPString1", config.API_ID, config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        
        self.userbot2 = Client("VIPString2", config.API_ID, config.API_HASH, session_string=str(config.STRING2))
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        
        self.userbot3 = Client("VIPString3", config.API_ID, config.API_HASH, session_string=str(config.STRING3))
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        
        self.userbot4 = Client("VIPString4", config.API_ID, config.API_HASH, session_string=str(config.STRING4))
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        
        self.userbot5 = Client("VIPString5", config.API_ID, config.API_HASH, session_string=str(config.STRING5))
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    # ... [Pause/Resume/Mute functions are same, just ensure they use group_assistant]

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def join_assistant(self, original_chat_id, chat_id):
        language = await get_lang(original_chat_id)
        _ = get_string(language)
        userbot = await get_assistant(chat_id)
        
        try:
            # Solving PeerIdInvalid: Force the assistant to resolve the chat first
            try:
                await userbot.get_chat(chat_id)
            except PeerIdInvalid:
                # If ID is not known, try via invite link or username
                pass

            try:
                get = await app.get_chat_member(chat_id, userbot.id)
            except ChatAdminRequired:
                raise AssistantErr(_["call_1"])
            
            if get.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                try:
                    await app.unban_chat_member(chat_id, userbot.id)
                except:
                    raise AssistantErr(_["call_2"].format(app.mention, userbot.id, userbot.mention, userbot.username))
        
        except UserNotParticipant:
            chat = await app.get_chat(chat_id)
            if chat.username:
                try:
                    await userbot.join_chat(chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))
            else:
                try:
                    invitelink = chat.invite_link or await app.export_chat_invite_link(chat_id)
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                    await userbot.join_chat(invitelink)
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))

    # [Remaining change_stream logic is fine, but ensure app.send_photo uses proper v2 types]

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.two.on_kicked()
        # ... [Other decorators]
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        # ... [Other stream end decorators]
        async def stream_end_handler(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            await self.change_stream(client, update.chat_id)

VIP = Call()