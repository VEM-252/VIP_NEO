import pyrogram
import pyromod.listen  # noqa
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
        LOGGER(__name__).info(f"Starting Bot...")
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
        self.name = get_me.first_name + " " + (get_me.last_name or "")
        self.mention = get_me.mention

        # Create the button
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏",
                        url=f"https://t.me/{self.username}?startgroup=true",
                    )
                ]
            ]
        )

        # Log Group Notification Logic
        if config.LOG_GROUP_ID:
            try:
                # Pehle check karein ki kya photo URL available hai
                if config.START_IMG_URL:
                    try:
                        await self.send_photo(
                            config.LOG_GROUP_ID,
                            photo=config.START_IMG_URL,
                            caption=f"╔════❰𝐖𝐄𝐋𝐂𝐎𝐌𝐄❱════❍⊱❁۪۪\n║\n║┣⪼🥀𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐁𝐚𝐛𝐲🎉\n║\n║┣⪼ {self.name}\n║\n║┣⪼🎈𝐈𝐃:- `{self.id}` \n║\n║┣⪼🎄@{self.username} \n║ \n║┣⪼💖𝐓𝐡𝐚𝐧𝐤𝐬 𝐅𝐨𝐫 𝐔𝐬𝐢𝐧𝐠😍\n║\n╚════════════════❍⊱❁",
                            reply_markup=button,
                        )
                    except Exception:
                        # Agar photo fail ho jaye toh text bhejien
                        await self.send_message(
                            config.LOG_GROUP_ID,
                            f"╔═══❰𝐖𝐄𝐋𝐂𝐎𝐌𝐄❱═══❍⊱❁۪۪\n║\n║┣⪼🥀𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐁𝐚𝐛𝐲🎉\n║\n║◈ {self.name}\n║\n║┣⪼🎈𝐈𝐃:- `{self.id}` \n║\n║┣⪼🎄@{self.username} \n║ \n║┣⪼💖𝐓𝐡𝐚𝐧𝐤𝐬 𝐅𝐨𝐫 𝐔𝐬𝐢𝐧𝐠😍\n║\n╚══════════════❍⊱❁",
                            reply_markup=button,
                        )
                else:
                    await self.send_message(config.LOG_GROUP_ID, "Bot Started!")
            except pyrogram.errors.ChatWriteForbidden:
                LOGGER(__name__).error("Bot ko Log Group mein message bhejne ki permission nahi hai (Add as Admin).")
            except Exception as e:
                LOGGER(__name__).error(f"Log Group Error: {e}")
        else:
            LOGGER(__name__).warning("LOG_GROUP_ID set nahi hai, skip kar raha hoon.")

        # Setting commands
        if config.SET_CMDS:
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "Start the bot"),
                        BotCommand("help", "Get the help menu"),
                        BotCommand("ping", "Check if the bot is alive"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing song"),
                        BotCommand("stop", "Stop the music"),
                        BotCommand("pause", "Pause the music"),
                        BotCommand("resume", "Resume the music"),
                        BotCommand("skip", "Skip current song"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
            except Exception as e:
                LOGGER(__name__).error(f"Failed to set commands: {e}")

        # Final Admin Check
        if config.LOG_GROUP_ID:
            try:
                m = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
                if m.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error("ADMIN BANAAO: Bot log group mein admin nahi hai.")
            except Exception:
                pass

        LOGGER(__name__).info(f"MusicBot Started as {self.username}")

    async def stop(self):
        await super().stop()
