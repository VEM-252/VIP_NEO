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

        # Button logic
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏", url=f"https://t.me/{self.username}?startgroup=true")]]
        )

        # Log Group ID ko integer mein convert karein
        if config.LOG_GROUP_ID:
            try:
                # YAHAN FIX HAI: ID ko hamesha integer hona chahiye
                log_chat_id = int(config.LOG_GROUP_ID)
                
                # Check karein ki kya bot group mein hai
                try:
                    await self.get_chat(log_chat_id)
                except Exception:
                    LOGGER(__name__).error(f"Bot ko Log Group ({log_chat_id}) mein add nahi kiya gaya hai!")
                    return

                if config.START_IMG_URL:
                    try:
                        await self.send_photo(
                            log_chat_id,
                            photo=config.START_IMG_URL,
                            caption=f"╔════❰𝐖𝐄𝐋𝐂𝐎𝐌𝐄❱════❍⊱❁۪۪\n║\n║┣⪼🥀𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐁𝐚𝐛𝐲🎉\n║\n║┣⪼ {self.name}\n║\n║┣⪼🎈𝐈𝐃:- `{self.id}` \n║\n║┣⪼🎄@{self.username} \n║ \n║┣⪼💖𝐓𝐡𝐚𝐧𝐤𝐬 𝐅𝐨𝐫 𝐔𝐬𝐢𝐧𝐠😍\n║\n╚════════════════❍⊱❁",
                            reply_markup=button,
                        )
                    except Exception:
                        await self.send_message(
                            log_chat_id,
                            f"╔═══❰𝐖𝐄𝐋𝐂𝐎𝐌𝐄❱═══❍⊱❁۪۪\n║\n║┣⪼🥀𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝 𝐁𝐚𝐛𝐲🎉\n║\n║◈ {self.name}\n║\n║┣⪼🎈𝐈𝐃:- `{self.id}` \n║\n║┣⪼🎄@{self.username} \n║ \n║┣⪼💖𝐓𝐡𝐚𝐧𝐤𝐬 𝐅𝐨𝐫 𝐔𝐬𝐢𝐧𝐠😍\n║\n╚══════════════❍⊱❁",
                            reply_markup=button,
                        )
                else:
                    await self.send_message(log_chat_id, "Bot Started!")
            except ValueError:
                LOGGER(__name__).error("LOG_GROUP_ID ek sahi number nahi hai. Check config file.")
            except pyrogram.errors.ChatWriteForbidden:
                LOGGER(__name__).error("Bot ko Log Group mein message bhejne ki permission nahi hai.")
            except Exception as e:
                LOGGER(__name__).error(f"Log Group Error: {e}")
        else:
            LOGGER(__name__).warning("LOG_GROUP_ID set nahi hai.")

        # Commands Setting
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
            except Exception as e:
                LOGGER(__name__).error(f"Failed to set commands: {e}")

        LOGGER(__name__).info(f"MusicBot Started as {self.username}")

    async def stop(self):
        await super().stop()
