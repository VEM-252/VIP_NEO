import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import config
from ..logging import LOGGER

class VIPBot(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            "VIPMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = f"{get_me.first_name} {get_me.last_name or ''}"
        self.mention = get_me.mention

        # Add Me Button
        button = InlineKeyboardMarkup([[
            InlineKeyboardButton("๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏", url=f"https://t.me/{self.username}?startgroup=true")
        ]])

        # Send Log Notification
        if config.LOG_GROUP_ID:
            try:
                log_text = (
                    f"✨ **{self.name} Sᴛᴀʀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
                    f"🆔 **ID:** `{self.id}`\n"
                    f"👤 **Usᴇʀɴᴀᴍᴇ:** @{self.username}\n"
                    f"💖 **Tʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ ᴍᴇ!**"
                )
                if config.START_IMG_URL:
                    await self.send_photo(config.LOG_GROUP_ID, photo=config.START_IMG_URL, caption=log_text, reply_markup=button)
                else:
                    await self.send_message(config.LOG_GROUP_ID, log_text, reply_markup=button)
            except Exception as e:
                LOGGER(__name__).error(f"Log Group Error: {e}")

        # Setting Bot Commands
        if config.SET_CMDS:
            try:
                # Commands for Private Chats
                await self.set_bot_commands(
                    [
                        BotCommand("start", "Start the bot"),
                        BotCommand("help", "Get help menu"),
                        BotCommand("ping", "Check bot status"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                # Commands for Groups
                await self.set_bot_commands(
                    [
                        BotCommand("play", "Play audio"),
                        BotCommand("vplay", "Play video"),
                        BotCommand("skip", "Skip current track"),
                        BotCommand("pause", "Pause track"),
                        BotCommand("resume", "Resume track"),
                        BotCommand("stop", "Stop music"),
                        BotCommand("queue", "Check music queue"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                # Commands for Admins (Full List)
                await self.set_bot_commands(
                    [
                        BotCommand("play", "Play audio"),
                        BotCommand("vplay", "Play video"),
                        BotCommand("settings", "Bot settings"),
                        BotCommand("reload", "Reload bot"),
                        BotCommand("end", "End stream"),
                        BotCommand("lyrics", "Get lyrics"),
                        BotCommand("playlist", "Your playlist"),
                        BotCommand("sudolist", "Sudo users list"),
                        BotCommand("gstats", "Global stats"),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )
            except Exception as e:
                LOGGER(__name__).error(f"Command Setup Error: {e}")

        LOGGER(__name__).info(f"MusicBot Started as {self.name}")

    async def stop(self):
        await super().stop()
