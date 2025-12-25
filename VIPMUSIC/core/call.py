# Copyright (C) 2024 by VISHAL-PANDEY@Github, < https://github.com/vishalpandeynkp1 >.
#
# This file is part of < https://github.com/vishalpandeynkp1/VIPNOBITAMUSIC_REPO > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/vishalpandeynkp1/VIPNOBITAMUSIC_REPO/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import TelegramServerError
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls

# --- ERROR FIX START (Compatibility for all pytgcalls versions) ---
try:
    from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
except ImportError:
    # This handles newer versions where names have changed
    from pytgcalls.exceptions import CallError as AlreadyJoinedError
    from pytgcalls.exceptions import GroupCallNotFound as NoActiveGroupCall
# --- ERROR FIX END ---

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

    AMBOT = await app.send_message(
        chat_id, f"🎶 **ꜱᴏɴɢ ʜᴀꜱ ᴇɴᴅᴇᴅ ɪɴ ᴠᴄ.** ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʜᴇᴀʀ ᴍᴏʀᴇ sᴏɴɢs?"
    )
    await asyncio.sleep(5)
    await AMBOT.delete()


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="VIPString1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        self.userbot2 = Client(
            name="VIPString2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )
        self.userbot3 = Client(
            name="VIPString3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )
        self.userbot4 = Client(
            name="VIPString4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )
        self.userbot5 = Client(
            name="VIPString5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.mute_stream(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.unmute_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def st_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _st_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def set_volume(self, chat_id: int, volume: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.change_volume_call(chat_id, volume)

    async def get_participant(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.get_participants(chat_id)

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int, link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
            )
        else:
            if image and config.PRIVATE_BOT_MODE == str(True):
                stream = MediaStream(
                    link,
                    image,
                    audio_parameters=audio_stream_quality,
                    video_parameters=video_stream_quality,
                )
            else:
                stream = MediaStream(link, audio_parameters=audio_stream_quality)
        await assistant.change_stream(
            chat_id,
            stream,
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            MediaStream(
                file_path,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else MediaStream(
                file_path,
                audio_parameters=audio_stream_quality,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
                video_flags=MediaStream.IGNORE,
            )
        )
        await assistant.change_stream(chat_id, stream)

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                vs = 1.0
                if str(speed) == "0.5": vs = 2.0
                if str(speed) == "0.75": vs = 1.35
                if str(speed) == "1.5": vs = 0.68
                if str(speed) == "2.0": vs = 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
        
        loop = asyncio.get_event_loop()
        dur = await loop.run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = (
            MediaStream(
                out,
                audio_parameters=audio_stream_quality,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0]["streamtype"] == "video"
            else MediaStream(
                out,
                audio_parameters=audio_stream_quality,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
                video_flags=MediaStream.IGNORE,
            )
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.change_stream(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOG_GROUP_ID)
        await assistant.join_group_call(
            config.LOG_GROUP_ID,
            MediaStream(link),
        )
        await asyncio.sleep(0.5)
        await assistant.leave_group_call(config.LOG_GROUP_ID)

    async def join_assistant(self, original_chat_id, chat_id):
        language = await get_lang(original_chat_id)
        _ = get_string(language)
        userbot = await get_assistant(chat_id)
        try:
            try:
                get = await app.get_chat_member(chat_id, userbot.id)
            except ChatAdminRequired:
                raise AssistantErr(_["call_1"])
            if (
                get.status == ChatMemberStatus.BANNED
                or get.status == ChatMemberStatus.RESTRICTED
            ):
                try:
                    await app.unban_chat_member(chat_id, userbot.id)
                except:
                    raise AssistantErr(
                        _["call_2"].format(
                            app.mention,
                            userbot.id,
                            userbot.mention,
                            userbot.username,
                        ),
                    )
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
                    try:
                        invitelink = chat.invite_link
                        if invitelink is None:
                            invitelink = await app.export_chat_invite_link(chat_id)
                    except:
                        invitelink = await app.export_chat_invite_link(chat_id)
                    m = await app.send_message(
                        original_chat_id, _["call_5"].format(userbot.name, chat.title)
                    )
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace(
                            "https://t.me/+", "https://t.me/joinchat/"
                        )
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)
                    await m.edit_text(_["call_6"].format(app.mention))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
            )
        else:
            if image and config.PRIVATE_BOT_MODE == str(True):
                stream = MediaStream(
                    link,
                    image,
                    audio_parameters=audio_stream_quality,
                    video_parameters=video_stream_quality,
                )
            else:
                stream = MediaStream(link, audio_parameters=audio_stream_quality)
        try:
            await assistant.join_group_call(chat_id, stream)
        except NoActiveGroupCall:
            try:
                await self.join_assistant(original_chat_id, chat_id)
            except Exception as e:
                raise e
            try:
                await assistant.join_group_call(chat_id, stream)
            except Exception:
                raise AssistantErr("**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ғᴏᴜɴᴅ**")
        except AlreadyJoinedError:
            raise AssistantErr("**ᴀssɪsᴛᴀɴᴛ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ**")
        except Exception as e:
            raise AssistantErr(f"Error: {e}")

        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop_val = await get_loop(chat_id)
        try:
            if loop_val == 0:
                popped = check.pop(0)
            else:
                loop_val = loop_val - 1
                await set_loop(chat_id, loop_val)
            if popped:
                await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
        except:
            return

        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        videoid = check[0]["vidid"]
        check[0]["played"] = 0
        video = True if str(streamtype) == "video" else False

        if "live_" in queued or "vid_" in queued or "index_" in queued:
            # Simplified for speed - assuming standard YouTube/Index handling
            stream = MediaStream(queued, audio_parameters=audio_stream_quality)
            await client.change_stream(chat_id, stream)
        else:
            stream = MediaStream(queued, audio_parameters=audio_stream_quality)
            await client.change_stream(chat_id, stream)

    async def ping(self):
        pings = []
        if config.STRING1: pings.append(await self.one.ping)
        if config.STRING2: pings.append(await self.two.ping)
        return str(round(sum(pings) / len(pings), 3)) if pings else "0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.one.on_closed_voice_chat()
        @self.one.on_left()
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        async def stream_end_handler(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            await self.change_stream(client, update.chat_id)

VIP = Call()