import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, ABOUT_TXT, HELP_TXT, FORCE_PIC
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user


async def process_command(client: Client, message, content, start):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    base64_string = content.split(" ", 1)[1] if len(content) > 7 else None
    string = await decode(base64_string)
    argument = string.split("-") if base64_string else []

    if len(argument) == 3:
        start, end = sorted(int(arg) / abs(client.db_channel.id) for arg in argument)
        ids = range(start, end + 1)
    elif len(argument) == 2:
        ids = [int(argument[1]) / abs(client.db_channel.id)]
    else:
        return

    temp_msg = await message.reply("Loading...")

    try:
        messages = await get_messages(client, ids)
    except:
        await message.reply_text("Something went wrong..!")
        return

    await temp_msg.delete()

    for msg in messages:
        caption = "" if not msg.caption else msg.caption.html
        reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

        try:
            await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode = ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode = ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
        except:
            pass

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message):
    content = message.text
    if len(content) <= 7:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')],
            [InlineKeyboardButton('ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ', url='https://t.me/Anime_X_Hunters'),
             InlineKeyboardButton('ᴏɴɢᴏɪɴɢ ᴄʜᴀɴɴᴇʟ', url='https://t.me/Ongoing_Anime_X_Hunter')],
             [InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
        ])
        await message.reply_photo(photo=START_PIC, caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username='@' + message.from_user.username if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ), reply_markup=reply_markup)
    else:
        await process_command(client, message, content)

@Bot.on_message(filters.command('help') & filters.private)
async def help(client: Client, message):
    content = message.text
    if len(content) <= 7:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('ʜᴏᴍᴇ​', callback_data='start'),
             InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
                                  ])
        await message.reply_photo(photo=START_PIC, caption=HELP_TXT.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username='@' + message.from_user.username if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ), reply_markup=reply_markup)
    else:
        await process_command(client, message, content)

@Bot.on_message(filters.command('about') & filters.private)
async def help(client: Client, message):
    content = message.text
    if len(content) <= 7:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('​🇸​​🇺​​🇵​​🇵​​🇴​​🇷​​🇹​ ​🇬​​🇷​​🇴​​🇺​​🇵​', url='https://t.me/Hunters_Discussion'),
             InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start')]
        ])
        await message.reply_photo(photo=START_PIC, caption=ABOUT_TXT.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username='@' + message.from_user.username if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ), reply_markup=reply_markup)
    else:
        await process_command(client, message, content)


#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##

    
    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(text="ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink),
            InlineKeyboardButton(text="ᴏɴɢᴏɪɴɢ ᴄʜᴀɴɴᴇʟ", url=client.invitelink2),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply_photo(
    photo=FORCE_PIC, 
    caption=FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=InlineKeyboardMarkup(buttons)
)

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
