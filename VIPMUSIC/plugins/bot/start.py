import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from VIPMUSIC import app
from VIPMUSIC.utils.database import add_served_chat, add_served_user
from config import START_IMG_URL, SUPPORT_CHAT, SUPPORT_CHANNEL
from VIPMUSIC.misc import _boot_
from pyrogram.errors import FloodWait

# Reaction Function
async def bot_reaction(message):
    try:
        await message.react("🕊️")
    except:
        pass

@app.on_message(filters.command(["start"]) & filters.private)
async def start_pm(client, message: Message):
    # --- Line 67 Fix Logic ---
    await bot_reaction(message)
    
    await add_served_user(message.from_user.id)
    
    # Welcome Text
    caption = f"👋 ʜᴇʟʟᴏ {message.from_user.mention},\n\n🕊️ ɪ ᴀᴍ ᴠɪᴘ ᴍᴜsɪᴄ ʙᴏᴛ, ɪ ᴄᴀɴ ᴘʟᴀʏ ᴍᴜsɪᴄ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs.\n\n✨ ᴛʜᴀɴᴋs ꜰᴏʀ sᴛᴀʀᴛɪɴɢ ᴍᴇ ʙᴀʙʏ!"
    
    # Inline Buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🕊️ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ 🕊️",
                    url=f"https://t.me/{client.username}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(text="ʜᴇʟᴘ", callback_data="settings_back_helper"),
                InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT),
            ],
            [
                InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇs", url=SUPPORT_CHANNEL),
            ],
        ]
    )

    await message.reply_photo(
        photo=START_IMG_URL,
        caption=caption,
        reply_markup=keyboard,
    )

@app.on_message(filters.command(["start"]) & filters.group)
async def start_gp(client, message: Message):
    # Group Start Reaction
    await bot_reaction(message)
    
    await add_served_chat(message.chat.id)
    
    await message.reply_text(
        text=f"🕊️ ʜᴇʟʟᴏ {message.from_user.mention}!\n\nɪ ᴀᴍ ᴀʟɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ ᴍᴜsɪᴄ.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT),
                    InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇs", url=SUPPORT_CHANNEL),
                ]
            ]
        ),
    )
