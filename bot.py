import os
import re
import io
import sys
import html
import time
import pickle
import random
import asyncio
import signal
import getpass
import speedtest
import logging
import aiohttp
import chess
import chess.svg

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from shlex import split as shlex_split
from datetime import datetime, timedelta
from collections import defaultdict

from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    MessageEntity,
    ChatPermissions,
    ChatMemberUpdated,
    ChatMemberAdministrator,
    ChatMemberOwner,
)

from telegram.constants import (
    ParseMode,
    ChatType,
)

from telegram.error import (
    BadRequest,
    Forbidden,
    TimedOut,
    NetworkError,
    TelegramError,
)

from telegram.helpers import (
    escape_markdown,
    mention_markdown,
)

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
)


# --- Config ---
BOT_TOKEN = 'loda loge?'
SUPPORT_LINK = "https://t.me/+D2dATbDtZbNiNGJl"
OWNER_ID = 7819315360




# --- Helper Functions ---
async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get the target user by:
    - Reply (preferred)
    - User ID (digits)
    - Username (@username or username)
    """
    chat_id = update.effective_chat.id
    # 1. If reply, return that user
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        return update.message.reply_to_message.from_user

    # 2. If argument is present, try to resolve as user_id or username
    if context.args and context.args[0]:
        arg = context.args[0]
        # Try user ID
        if arg.isdigit():
            try:
                member = await context.bot.get_chat_member(chat_id, int(arg))
                return member.user
            except Exception:
                pass
        # Try @username or username
        username = arg
        if username.startswith("@"):
            username = username[1:]
        # Try to get user from chat by username
        try:
            members = await context.bot.get_chat_administrators(chat_id)
            for m in members:
                if m.user.username and m.user.username.lower() == username.lower():
                    return m.user
        except Exception:
            pass
        try:
            member = await context.bot.get_chat_member(chat_id, username)
            return member.user
        except Exception:
            pass
        # Try to get user from chat admins
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            for m in admins:
                if m.user.username and m.user.username.lower() == username.lower():
                    return m.user
        except Exception:
            pass
        # Try get_chat with @username and username
        for uname in ("@" + username, username):
            try:
                user_obj = await context.bot.get_chat(uname)
                if user_obj:
                    return user_obj
            except Exception:
                continue
        # Try get_chat_member with username (rarely works)
        try:
            member = await context.bot.get_chat_member(chat_id, username)
            return member.user
        except Exception:
            pass

    await update.message.reply_text(
        "❌ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>",
        parse_mode="HTML"
    )
    return None

def is_admin(member):
    return isinstance(member, ChatMemberAdministrator) or isinstance(member, ChatMemberOwner)
CHANNEL_USERNAME = "@fos_bots"
# --- Command Handlers ---
async def is_user_in_channel(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logging.error(f"Error checking channel membership: {e}")
        return False

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        is_member = await is_user_in_channel(user.id, context.bot)
    except Exception as e:
        logging.error(f"start_handler: channel check failed: {e}")
        is_member = True  # fallback: allow

    if is_member:
        bot_me = await context.bot.get_me()
        processing_msg = await update.message.reply_text(
            "<b>⏳ Please wait while we process your request...</b>\n"
            "<i>Step 1: Initializing system modules...</i>",
            parse_mode="HTML"
        )
        await asyncio.sleep(0.8)
        try:
            await processing_msg.edit_text(
                "<b>⏳ Please wait while we process your request...</b>\n"
                "<i>Step 2: Verifying channel membership...</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(0.8)
        try:
            await processing_msg.edit_text(
                "<b>⏳ Please wait while we process your request...</b>\n"
                "<i>Step 3: Preparing your personalized welcome...</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(0.8)
        try:
            await processing_msg.edit_text(
                "<b>⏳ Please wait while we process your request...</b>\n"
                "<i>Step 4: Finalizing setup...</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(0.6)
        welcome_text = (
            f"<b>👋 Welcome, {user.mention_html()}!</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<b>🤖 {bot_me.mention_html()} — Professional Group Management Suite</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"• 🚫 Advanced Anti-Spam, Anti-Raid, Anti-Link Protection\n"
            f"• 🛡 Automated Warnings, Temporary & Permanent Bans\n"
            f"• 👮‍♂️ Powerful Admin Tools & Role Management\n"
            f"• 📌 Pinning, Rules, Custom Welcome/Goodbye Messages\n"
            f"• ⚡️ Fast, Secure, Reliable, and User-Friendly\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<i>Type <code>/help</code> to view all available commands and features.</i>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_me.username}?startgroup=true")],
            [
                InlineKeyboardButton("👑 Owner", url="https://t.me/FOS_FOUNDER"),
                InlineKeyboardButton("💬 Support", url=SUPPORT_LINK),
            ]
        ])
        try:
            with open("C:/Users/Anirudh/Desktop/ichizen.mp4", "rb") as video_file:
                await processing_msg.delete()
                await update.message.reply_video(
                    video=video_file,
                    caption=welcome_text,
                    parse_mode="HTML",
                    reply_markup=kb
                )
        except Exception:
            await processing_msg.edit_text(
                welcome_text,
                parse_mode="HTML",
                reply_markup=kb
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"<b>Access Restricted</b>\n"
            f"Hello {user.mention_html()},\n\n"
            "To access the full features of this bot, please join our official channel first.\n"
            "Once you have joined, use /start again.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    if not is_admin(member):
        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
        return
    bot_id = (await context.bot.get_me()).id
    bot_member = await context.bot.get_chat_member(chat_id, bot_id)
    if not is_admin(bot_member):
        await update.message.reply_text("🤖 <b>I need to be an admin to ban users!</b>", parse_mode="HTML")
        return

    # Try to get target user by reply, user ID, or username
    target_user = await get_target_user(update, context)
    if not target_user or target_user.id == user_id:
        await update.message.reply_text("🙅‍♂️ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>", parse_mode="HTML")
        return
    # Prevent banning sudo users, lord, or substitute lords
    if is_sudo(target_user.id) or target_user.id == sudo_users["lord"] or target_user.id in sudo_users.get("substitute_lords", set()):
        await update.message.reply_text("🚫 <b>You cannot ban a sudo user, the Lord, or the Substitute Lord!</b>", parse_mode="HTML")
        return
    try:
        target_member = await context.bot.get_chat_member(chat_id, target_user.id)
        if is_admin(target_member):
            await update.message.reply_text("🚫 <b>I can't ban admins or the group owner!</b>", parse_mode="HTML")
            return
    except Exception:
        # If user is not in group, still allow ban (Telegram allows banning by user_id)
        pass
    await context.bot.ban_chat_member(chat_id, target_user.id)
    user_display = target_user.mention_html()
    if getattr(target_user, "username", None):
        user_display += f" (@{target_user.username})"
    # Check for reason in command arguments (after user mention/ID)
    reason = ""
    if context.args:
        # If reply: all args are reason; if not, skip first arg (user)
        if update.message.reply_to_message:
            reason = " ".join(context.args)
        elif len(context.args) > 1:
            reason = " ".join(context.args[1:])
    text = (
        f"🔨 <b>User Banned</b>\n"
        f"👤 <b>User:</b> {user_display}\n"
        f"👮 <b>By:</b> {update.effective_user.mention_html()}\n"
    )
    if reason:
        text += f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
    text += f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"
    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )
    # --- tban command ---
async def tban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    if not is_admin(member):
        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
        return
    bot_id = (await context.bot.get_me()).id
    bot_member = await context.bot.get_chat_member(chat_id, bot_id)
    if not is_admin(bot_member):
        await update.message.reply_text("🤖 <b>I need to be an admin to ban users!</b>", parse_mode="HTML")
        return
    target_user = await get_target_user(update, context)
    if not target_user or target_user.id == user_id:
        await update.message.reply_text("🙅‍♂️ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>", parse_mode="HTML")
        return
    if is_sudo(target_user.id) or target_user.id == sudo_users["lord"] or target_user.id in sudo_users.get("substitute_lords", set()):
        await update.message.reply_text("🚫 <b>You cannot ban a sudo user, the Lord, or the Substitute Lord!</b>", parse_mode="HTML")
        return
    try:
        target_member = await context.bot.get_chat_member(chat_id, target_user.id)
        if is_admin(target_member):
            await update.message.reply_text("🚫 <b>I can't ban admins or the group owner!</b>", parse_mode="HTML")
            return
    except Exception:
        pass
    # Parse duration
    if update.message.reply_to_message:
        if len(context.args) < 1:
            await update.message.reply_text("⏳ <b>Please specify a duration (e.g. 10m, 2h, 1d).</b>", parse_mode="HTML")
            return
        duration_str = context.args[0]
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    else:
        if len(context.args) < 2:
            await update.message.reply_text("⏳ <b>Please specify a user and a duration (e.g. /tban @user 10m).</b>", parse_mode="HTML")
            return
        duration_str = context.args[1]
        reason = " ".join(context.args[2:]) if len(context.args) > 2 else ""
    match = re.match(r"^(\d+)([smhd])$", duration_str)
    if not match:
        await update.message.reply_text("⏳ <b>Invalid duration format! Use like 10m, 2h, 1d, 30s.</b>", parse_mode="HTML")
        return
    value, unit = int(match.group(1)), match.group(2)
    delta = timedelta(seconds=value) if unit == "s" else \
            timedelta(minutes=value) if unit == "m" else \
            timedelta(hours=value) if unit == "h" else \
            timedelta(days=value)
    until_date = datetime.now() + delta
    await context.bot.ban_chat_member(chat_id, target_user.id, until_date=until_date)
    text = (
        f"⏳🔨 <b>User Temporarily Banned!</b>\n"
        f"👤 <b>User:</b> {target_user.mention_html()}\n"
        f"⏳ <b>Duration:</b> <code>{duration_str}</code>\n"
        f"👮 <b>By:</b> {update.effective_user.mention_html()}\n"
    )
    if reason:
        text += f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
    text += f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"
    await update.message.reply_text(text, parse_mode="HTML")

    async def unban_later():
        await asyncio.sleep(delta.total_seconds())
        try:
            await context.bot.unban_chat_member(chat_id, target_user.id)
            await context.bot.send_message(
                chat_id,
                f"✅ <b>User unbanned after temporary ban:</b> {target_user.mention_html()}",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Error auto-unbanning user after tban: {e}")

    asyncio.create_task(unban_later())

    # --- unban command ---
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user:
            await update.message.reply_text("🙅‍♂️ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>", parse_mode="HTML")
            return
        try:
            await context.bot.unban_chat_member(chat_id, target_user.id)
            await update.message.reply_text(
                f"✅ <b>User unbanned:</b> {target_user.mention_html()}",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>Failed to unban user:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )

    # --- warn/unwarn/warns_command ---
MAX_WARNS = 3
warns = defaultdict(lambda: defaultdict(int))

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user or target_user.id == user_id:
            await update.message.reply_text("🙅‍♂️ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>", parse_mode="HTML")
            return
        warns[chat_id][target_user.id] += 1
        count = warns[chat_id][target_user.id]
        warn_bar = "🟩" * count + "⬜" * (MAX_WARNS - count)
        reason = ""
        if update.message.reply_to_message:
            reason = " ".join(context.args) if context.args else ""
        elif len(context.args) > 1:
            reason = " ".join(context.args[1:])
        text = (
            f"⚠️ <b>User warned!</b>\n"
            f"👤 <b>User:</b> {target_user.mention_html()}\n"
            f"{warn_bar}\n"
            f"👮 <b>By:</b> {update.effective_user.mention_html()}\n"
        )
        if reason:
            text += f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
        if count >= MAX_WARNS:
            await context.bot.ban_chat_member(chat_id, target_user.id)
            warns[chat_id][target_user.id] = 0
            text += f"🔨 <b>User banned after max warns.</b>\n"
        text += f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"
        await update.message.reply_text(text, parse_mode="HTML")

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user:
            await update.message.reply_text("🙅‍♂️ <b>Couldn't find the user. Please reply or provide a valid user ID/username.</b>", parse_mode="HTML")
            return
        if warns[chat_id][target_user.id] > 0:
            warns[chat_id][target_user.id] -= 1
        count = warns[chat_id][target_user.id]
        warn_bar = "🟩" * count + "⬜" * (MAX_WARNS - count)
        await update.message.reply_text(
            f"✅ <b>Warning removed for {target_user.mention_html()}.</b>\n{warn_bar}",
            parse_mode="HTML"
        )

async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            user = update.message.reply_to_message.from_user
        elif context.args and context.args[0]:
            arg = context.args[0]
            if arg.isdigit():
                user = (await context.bot.get_chat_member(chat_id, int(arg))).user
            elif arg.startswith("@"):
                admins = await context.bot.get_chat_administrators(chat_id)
                user = None
                for m in admins:
                    if m.user.username and m.user.username.lower() == arg[1:].lower():
                        user = m.user
                        break
                if not user:
                    try:
                        user = (await context.bot.get_chat_member(chat_id, arg)).user
                    except Exception:
                        await update.message.reply_text("❌ <b>Could not find user by username in this chat.</b>", parse_mode="HTML")
                        return
            else:
                await update.message.reply_text("❌ <b>Invalid username or user ID.</b>", parse_mode="HTML")
                return
        else:
            user = update.effective_user
        count = warns[chat_id][user.id]
        warn_bar = "🟩" * count + "⬜" * (MAX_WARNS - count)
        await update.message.reply_text(
            f"⚠️ <b>{user.mention_html()} has {count} warning(s).</b>\n{warn_bar}",
            parse_mode="HTML"
        )
from telegram.error import RetryAfter

async def speedtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs a speedtest and sends a stylish summary with a progress animation and the official Speedtest by Ookla result image.
    Uses a separate thread for speedtest to avoid blocking the event loop.
    Stops editing the progress message after 10 edits to avoid flood control.
    """
    progress_frames = [
        "🚀", "🌐", "⚡️", "💫", "🔮", "🛰️", "🦾", "🧬", "🪐", "🌟"
    ]
    progress_texts = [
        "Igniting boosters...",
        "Connecting to hyperspace...",
        "Contacting Ookla mothership...",
        "Warping download speed...",
        "Warping upload speed...",
        "Measuring quantum ping...",
        "Locating best galaxy server...",
        "Finalizing cosmic results...",
        "Rendering speed nebula...",
        "Almost at light speed!"
    ]
    msg = await update.message.reply_text(
        "<b>🚀 Initiating Speedtest...</b>\n<i>Preparing for launch...</i>",
        parse_mode="HTML"
    )

    async def animate_progress():
        idx = 0
        max_edits = 10
        while idx < max_edits:
            await asyncio.sleep(0.7)
            try:
                frame = progress_frames[idx % len(progress_frames)]
                text = progress_texts[idx % len(progress_texts)]
                await msg.edit_text(
                    f"{frame} <b>{text}</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            idx += 1

    progress_task = asyncio.create_task(animate_progress())

    def run_speedtest():
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download()
        upload = st.upload()
        ping = st.results.ping
        server = st.results.server
        isp = st.results.client.get("isp", "Unknown")
        country = st.results.client.get("country", "Unknown")
        st.results.share()  # This generates the result image and sets st.results.share()
        image_url = st.results.share()
        return download, upload, ping, server, isp, country, image_url

    try:
        loop = asyncio.get_running_loop()
        download, upload, ping, server, isp, country, image_url = await loop.run_in_executor(None, run_speedtest)
        progress_task.cancel()
        await asyncio.sleep(0.2)
        download_mbps = download / 1_000_000
        upload_mbps = upload / 1_000_000
        server_name = server.get("sponsor", "Unknown") if server else "Unknown"
        server_country = server.get("country", "Unknown") if server else "Unknown"
        summary = (
            "<b>🌌 Speedtest Results</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⬇️ <b>Download:</b> <code>{download_mbps:.2f} Mbps</code>\n"
            f"⬆️ <b>Upload:</b> <code>{upload_mbps:.2f} Mbps</code>\n"
            f"🛰️ <b>Ping:</b> <code>{ping:.2f} ms</code>\n"
            f"🌍 <b>Server:</b> <code>{server_name} ({server_country})</code>\n"
            f"🏢 <b>ISP:</b> <code>{isp}</code>\n"
            f"🌎 <b>Location:</b> <code>{country}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Tested by:</i> {update.effective_user.mention_html()}"
        )
        await msg.edit_text("🪐 <b>Speedtest complete! Sending results...</b>",
            parse_mode="HTML"
        )
        await update.message.reply_photo(
            photo=image_url,
            caption=summary,
            parse_mode="HTML"
        )
        await msg.delete()
    except RetryAfter as e:
        try:
            progress_task.cancel()
        except Exception:
            pass
        await msg.edit_text(
            f"❌ <b>Flood control exceeded.</b>\n"
            f"Please wait <b>{e.retry_after}</b> seconds before trying again.",
            parse_mode="HTML"
        )
    except Exception as e:
        try:
            progress_task.cancel()
        except Exception:
            pass
        if "HTTP Error 403" in str(e) or "403: Forbidden" in str(e):
            await msg.edit_text(
                "❌ <b>Speedtest failed.</b>\n"
                "Speedtest.net is blocking requests from this server (HTTP 403 Forbidden). Try again later or from a different server.",
                parse_mode="HTML"
            )
        else:
            await msg.edit_text(
                "❌ <b>Speedtest failed.</b>\n"
                f"<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    if not is_admin(member):
        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
        return
    bot_id = (await context.bot.get_me()).id
    bot_member = await context.bot.get_chat_member(chat_id, bot_id)
    if not is_admin(bot_member):
        await update.message.reply_text("🤖 <b>I need to be an admin to mute users!</b>", parse_mode="HTML")
        return
    target_user = await get_target_user(update, context)
    if not target_user or target_user.id == user_id:
        await update.message.reply_text("🙅‍♂️ <b>You can't mute yourself!</b>", parse_mode="HTML")
        return
    target_member = await context.bot.get_chat_member(chat_id, target_user.id)
    if is_admin(target_member):
        await update.message.reply_text("🚫 <b>I can't mute admins or the group owner!</b>", parse_mode="HTML")
        return

    until_date = datetime.now() + timedelta(days=365*10)
    try:
        await context.bot.restrict_chat_member(
            chat_id,
            target_user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        await update.message.reply_text(
            (
                f"🔇 <b>User Muted</b>\n"
                f"👤 <b>User:</b> {target_user.mention_html()}\n"
                f"👮 <b>Actioned By:</b> {update.effective_user.mention_html()}\n"
                f"⏳ <i>User has been muted indefinitely. To unmute, use <code>/unmute</code>.</i>\n"
                f"💡 <i>“Silence is sometimes the best answer.”</i>\n"
                f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>Failed to mute user:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

async def tmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    if not is_admin(member):
        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
        return
    bot_id = (await context.bot.get_me()).id
    bot_member = await context.bot.get_chat_member(chat_id, bot_id)
    if not is_admin(bot_member):
        await update.message.reply_text("🤖 <b>I need to be an admin to mute users!</b>", parse_mode="HTML")
        return
    target_user = await get_target_user(update, context)
    if not target_user or target_user.id == user_id:
        await update.message.reply_text("🙅‍♂️ <b>You can't mute yourself!</b>", parse_mode="HTML")
        return
    target_member = await context.bot.get_chat_member(chat_id, target_user.id)
    if is_admin(target_member):
        await update.message.reply_text("🚫 <b>I can't mute admins or the group owner!</b>", parse_mode="HTML")
        return
    if update.message.reply_to_message:
        if len(context.args) < 1:
            await update.message.reply_text("⏳ <b>Please specify a duration (e.g. 10m, 2h, 1d).</b>", parse_mode="HTML")
            return
        duration_str = context.args[0]
    else:
        if len(context.args) < 2:
            await update.message.reply_text("⏳ <b>Please specify a user and a duration (e.g. /tmute @user 10m).</b>", parse_mode="HTML")
            return
        duration_str = context.args[1]
    match = re.match(r"^(\d+)([smhd])$", duration_str)
    if not match:
        await update.message.reply_text("⏳ <b>Invalid duration format! Use like 10m, 2h, 1d, 30s.</b>", parse_mode="HTML")
        return
    value, unit = int(match.group(1)), match.group(2)
    delta = timedelta(seconds=value) if unit == "s" else \
            timedelta(minutes=value) if unit == "m" else \
            timedelta(hours=value) if unit == "h" else \
            timedelta(days=value)
    until_date = datetime.now() + delta
    await context.bot.restrict_chat_member(
        chat_id,
        target_user.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_date
    )
    # No GIF, just send a professional text message
    text = (
        f"🔇 <b>Temporarily Muted!</b>\n"
        f"👤 <b>User:</b> {target_user.mention_html()}\n"
        f"⏳ <b>Duration:</b> <code>{duration_str}</code>\n"
        f"👮 <b>By:</b> {update.effective_user.mention_html()}\n"
    )
    # Add reason if present
    if update.message.reply_to_message:
        reason = " ".join(context.args)
    elif len(context.args) > 2:
        reason = " ".join(context.args[2:])
    elif len(context.args) > 1:
        reason = " ".join(context.args[1:])
    else:
        reason = ""
    if reason:
        text += f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
    text += f"🤫 <i>Silence is golden!</i>\n"
    text += f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

    async def unmute_later():
        await asyncio.sleep(delta.total_seconds())
        try:
            # Check if user is still muted before unmuting and sending message
            member = await context.bot.get_chat_member(chat_id, target_user.id)
            if getattr(member, "can_send_messages", True):
                # Already unmuted, do nothing
                return
            # Restore only "Send Messages" and "Send Stickers" permissions
            await context.bot.restrict_chat_member(
                chat_id,
                target_user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_stickers=True,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_animations=False,
                    can_send_games=False,
                    can_send_audios=False,
                    can_send_documents=False,
                    can_send_photos=False,
                    can_send_videos=False,
                    can_send_video_notes=False,
                    can_send_voice_notes=False,
                    can_invite_users=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_pin_messages=False,
                )
            )
            # Send a stylish unmute notification
            await context.bot.send_animation(
                chat_id,
                animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                caption=(
                    f"🔊 <b>Temporary Mute Expired!</b>\n"
                    f"👤 <b>User:</b> {target_user.mention_html()}\n"
                    f"⏰ <b>Mute Duration Ended.</b>\n"
                    f"✅ <b>Restored:</b> <i>Send Messages</i> & <i>Send Stickers</i>\n"
                    f"<i>Welcome back to the conversation!</i>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Error auto-unmuting user: {e}")

    asyncio.create_task(unmute_later())

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    # Allow Lord, Substitute Lords, and Descendants to use this command
    if not (is_admin(member) or is_sudo(user_id)):
        await update.message.reply_text("👮 <b>You must be an admin or sudo user to use this command!</b>", parse_mode="HTML")
        return
    bot_id = (await context.bot.get_me()).id
    bot_member = await context.bot.get_chat_member(chat_id, bot_id)
    if not is_admin(bot_member):
        await update.message.reply_text("🤖 <b>I need to be an admin to unmute users!</b>", parse_mode="HTML")
        return
    target_user = await get_target_user(update, context)
    if not target_user:
        return
    try:
        await context.bot.restrict_chat_member(
            chat_id,
            target_user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text(
            (
                f"🔊 <b>User Unmuted</b>\n"
                f"👤 <b>User:</b> {target_user.mention_html()}\n"
                f"👮 <b>Actioned By:</b> {update.effective_user.mention_html()}\n"
                f"✅ <i>User can now send messages in this group.</i>\n"
                f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>Failed to unmute user:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        user = None

        if update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
            if user is None:
                await update.message.reply_text(
                    "❌ <b>Could not retrieve the user from the replied message.</b>",
                    parse_mode="HTML"
                )
                return
        elif context.args and context.args[0]:
            arg = context.args[0]
            try:
                if arg.isdigit():
                    # Try as user ID in group
                    try:
                        member = await context.bot.get_chat_member(chat_id, int(arg))
                        user = member.user
                    except Exception:
                        # Try as global user
                        user = await context.bot.get_chat(int(arg))
                elif arg.startswith("@"):
                    username = arg if arg.startswith("@") else f"@{arg}"
                    try:
                        user = await context.bot.get_chat(username)
                    except Exception as e:
                        if "Chat not found" in str(e):
                            await update.message.reply_text(
                                f"❌ <b>User not found by username:</b> <code>{html.escape(arg)}</code>\n"
                                "Please make sure the username is correct and the user has started the bot or is a member of this chat.",
                                parse_mode="HTML"
                            )
                        else:
                            await update.message.reply_text(
                                f"❌ <b>Could not find user by username:</b> <code>{html.escape(str(e))}</code>",
                                parse_mode="HTML"
                            )
                        return
                else:
                    await update.message.reply_text(
                        "❌ <b>Invalid username or user ID.</b>",
                        parse_mode="HTML"
                    )
                    return
            except Exception as e:
                await update.message.reply_text(
                    f"❌ <b>Could not find user:</b> <code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
                return

        if user:
            await update.message.reply_text(
                f"<b>User:</b> {user.mention_html()} (<code>{user.first_name}</code>)\n"
                f"<b>User ID:</b> <code>{user.id}</code>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                (
                    f"<b>This chat's ID is: </b> <code>{chat_id}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"<i>Reply to a user's message or provide a username/user ID to get their user ID.</i>"
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"Error in id_command: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>An unexpected error occurred:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def base_promote_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Performs all necessary checks before promoting a user.
    Returns (chat_id, target_user, is_owner) if checks pass, else None.
    """
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
        return None

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Lord or Substitute Lord bypass admin checks
    if user_id == sudo_users.get("lord") or user_id in sudo_users.get("substitute_lords", set()):
        bot_id = (await context.bot.get_me()).id
        bot_member = await context.bot.get_chat_member(chat_id, bot_id)
        if not is_admin(bot_member):
            await update.message.reply_text("🤖 <b>I need to be an admin to promote users!</b>", parse_mode="HTML")
            return None
        if not getattr(bot_member, "can_promote_members", False):
            await update.message.reply_text("❌ <b>I do not have the 'Add New Admins' permission.</b>", parse_mode="HTML")
            return None
        target_user = await get_target_user(update, context)
        if not target_user:
            return None
        try:
            target_member = await context.bot.get_chat_member(chat_id, target_user.id)
            if is_admin(target_member):
                await update.message.reply_text("⚠️ <b>This user is already an admin!</b>", parse_mode="HTML")
                return None
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>User not found in this chat or not a member.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
            return None
        return (chat_id, target_user, True)  # Treat as owner for full rights

    # Standard admin checks
    member = await context.bot.get_chat_member(chat_id, user_id)
    if not is_admin(member):
        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
        return None

    bot_id = (await context.bot.get_me()).id
    bot_member = await context.bot.get_chat_member(chat_id, bot_id)
    if not is_admin(bot_member):
        await update.message.reply_text("🤖 <b>I need to be an admin to promote users!</b>", parse_mode="HTML")
        return None
    if not getattr(bot_member, "can_promote_members", False):
        await update.message.reply_text("❌ <b>I do not have the 'Add New Admins' permission.</b>", parse_mode="HTML")
        return None

    target_user = await get_target_user(update, context)
    if not target_user:
        return None
    if target_user.id == user_id and member.status != "creator":
        await update.message.reply_text("🙅‍♂️ <b>You can't promote yourself!</b>", parse_mode="HTML")
        return None
    try:
        target_member = await context.bot.get_chat_member(chat_id, target_user.id)
        if is_admin(target_member):
            await update.message.reply_text("⚠️ <b>This user is already an admin!</b>", parse_mode="HTML")
            return None
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>User not found in this chat or not a member.</b>\n<code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )
        return None

    return (chat_id, target_user, member.status == "creator")

async def lowpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Support promotion by reply, user ID, or username
    result = await base_promote_check(update, context)
    if not result:
        return
    chat_id, target_user, is_owner = result
    user_id = update.effective_user.id

    # Get the current user's admin status
    try:
        current_user_member = await context.bot.get_chat_member(chat_id, user_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to check your admin status:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
        return

    # Check if user is either:
    # 1. Sudo user (global admin)
    # 2. Chat admin with can_promote_members privilege
    if not (is_sudo(user_id) or
            (current_user_member.status in ["administrator", "creator"] and
             getattr(current_user_member, 'can_promote_members', False))):
        await update.message.reply_text(
            "👮 <b>You must be an admin with 'add admins' permission to use this command!</b>",
            parse_mode="HTML"
        )
        return

    # Only use "Junior Admin" as default if no custom title is given
    if len(context.args) > 1:
        title = " ".join(context.args[1:])
    else:
        title = "Junior Admin"

    try:
        await context.bot.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=False,
            can_pin_messages=True,
            can_promote_members=False,
            can_manage_video_chats=True,
        )
        try:
            await context.bot.set_chat_administrator_custom_title(chat_id, target_user.id, title)
        except Exception:
            pass
        await update.message.reply_text(
            f"🆙 {target_user.mention_html()} promoted to <b>{html.escape(title)}</b>!\n"
            f"🏷️ Title: <code>{html.escape(title)}</code>\n"
            f"Rights: Delete messages, pin messages, invite users",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to promote user:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def midpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Support promotion by reply, user ID, or username
    result = await base_promote_check(update, context)
    if not result:
        return
    chat_id, target_user, is_owner = result
    user_id = update.effective_user.id

    # Get the current user's admin status
    try:
        current_user_member = await context.bot.get_chat_member(chat_id, user_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to check your admin status:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
        return

    # Check if user is either:
    # 1. Sudo user (lord or substitute lords)
    # 2. Chat owner
    # 3. Chat admin with can_promote_members privilege
    if not (user_id == sudo_users["lord"] or
            user_id in sudo_users.get("substitute_lords", set()) or
            is_owner or
            (current_user_member.status in ["administrator", "creator"] and
             getattr(current_user_member, 'can_promote_members', False))):
        await update.message.reply_text(
            "🔒 <b>You need promotion privileges to assign this level!</b>\n"
            "Only Lords, Substitute Lords, chat owners, or admins with 'add admins' permission can use this command!",
            parse_mode="HTML"
        )
        return

    # Only use "Senior Admin" as default if no custom title is given
    if len(context.args) > 1:
        title = " ".join(context.args[1:])
    else:
        title = "Senior Admin"

    try:
        await context.bot.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,
            can_manage_video_chats=True,
            is_anonymous=False
        )
        try:
            await context.bot.set_chat_administrator_custom_title(chat_id, target_user.id, title)
        except Exception:
            pass
        await update.message.reply_text(
            f"🛡 {target_user.mention_html()} promoted to <b>{html.escape(title)}</b>!\n"
            f"🏷 Title: <code>{html.escape(title)}</code>\n"
            f"Rights: Manage chat info, restrict, pin, topics, video chats",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to promote user:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")


async def fullpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Support promotion by reply, user ID, or username
    result = await base_promote_check(update, context)
    if not result:
        return
    chat_id, target_user, is_owner = result
    user_id = update.effective_user.id

    # Get the current user's admin status
    try:
        current_user_member = await context.bot.get_chat_member(chat_id, user_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to check your admin status:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
        return

    # Check if user is either:
    # 1. Sudo user (lord or substitute lords)
    # 2. Chat owner
    # 3. Chat admin with can_promote_members privilege AND is_owner status
    if not (user_id == sudo_users["lord"] or
            user_id in sudo_users.get("substitute_lords", set()) or
            is_owner or
            (current_user_member.status == "creator")):
        await update.message.reply_text(
            "👑 <b>Only the group owner, Lord, or Substitute Lord can assign Head Admin status!</b>\n"
            "This power cannot be delegated to other admins.",
            parse_mode="HTML"
        )
        return

    # Only use "Head Admin" as default if no custom title is given
    if len(context.args) > 1:
        title = " ".join(context.args[1:])
    else:
        title = "Head Admin"

    try:
        await context.bot.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,
            can_manage_video_chats=True,
            can_manage_chat=True,
            is_anonymous=False
        )
        try:
            await context.bot.set_chat_administrator_custom_title(chat_id, target_user.id, title)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ Couldn't set custom title (but promotion succeeded):\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )

        await update.message.reply_text(
            f"👑 {target_user.mention_html()} promoted to <b>{html.escape(title)}</b>!\n"
            f"🏷️ Title: <code>{html.escape(title)}</code>\n"
            f"🔱 Rights: <b>FULL ADMIN RIGHTS</b> (can promote others)",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to promote user:\n<code>{html.escape(str(e))}</code>\n"
            "Please ensure I have proper admin privileges to perform this action.",
            parse_mode="HTML"
        )

# Define sudo_users at the top of your file or before this function
sudo_users = {
    "lord": 123456789,  # Replace with the actual Lord user ID
    "substitute_lord": 987654321  # Replace with the actual Substitute Lord user ID, or remove if not needed
}

async def sudo_join_announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.new_chat_members:
            return
        chat = update.effective_chat
        for user in update.message.new_chat_members:
            # Determine sudo title
            if user.id == sudo_users.get("lord"):
                title = "👑 The Lord"
                line = "All rise! The supreme Lord has entered the chat. Show your respect!"
            elif user.id in sudo_users.get("substitute_lords", set()):
                title = "🦸 The Substitute Lord"
                line = "A Substitute Lord has arrived! The backup hero is here. Bow down!"
            elif user.id in sudo_users.get("descendants", set()):
                title = "🧬 A Descendant"
                line = "A Sudo Descendant has joined! The legacy continues. Salute!"
            else:
                continue
            await context.bot.send_message(
                chat.id,
                f"<b>{title} {user.mention_html()} has joined!</b>\n{line}",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"sudo_join_announce error: {e}")

async def check_rights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bot_id = (await context.bot.get_me()).id
    try:
        bot_member = await context.bot.get_chat_member(chat_id, bot_id)
        if not is_admin(bot_member):
            await update.message.reply_text(
                "🚫 <b>I am <u>not</u> an admin in this group.</b>\n"
                "<i>Please promote me to admin for full functionality.</i>",
                parse_mode="HTML"
            )
            return

        rights = [
            ("✅" if getattr(bot_member, "can_promote_members", False) else "❌") + " <b>Add New Admins</b>",
            ("✅" if getattr(bot_member, "is_anonymous", False) else "❌") + " <b>Remain Anonymous</b>",
            ("✅" if getattr(bot_member, "can_change_info", False) else "❌") + " <b>Change Group Info</b>",
            ("✅" if getattr(bot_member, "can_delete_messages", False) else "❌") + " <b>Delete Messages</b>",
            ("✅" if getattr(bot_member, "can_restrict_members", False) else "❌") + " <b>Restrict Members</b>",
            ("✅" if getattr(bot_member, "can_pin_messages", False) else "❌") + " <b>Pin Messages</b>",
            ("✅" if getattr(bot_member, "can_manage_video_chats", False) else "❌") + " <b>Manage Video Chats</b>",
        ]
        text = (
            "<b>🤖 My Current Admin Permissions</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(rights) +
            "\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>For full admin features, please ensure all permissions are enabled.</i>"
        )
        await update.message.reply_text(
            text,
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>Error checking permissions:</b>\n<code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Demote a user from admin status. Supports reply, user ID, or username.
    Prevents demoting Lord, Substitute Lords, and the group owner.
    Only admins with promote_members permission or sudo users can use this command.
    """
    try:
        # Check if command is used in private chat
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return

        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Get the current user's admin status
        try:
            current_member = await context.bot.get_chat_member(chat_id, user_id)
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to check your admin status:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
            return

        # Check if user has permission to demote (sudo or admin with promote_members right)
        if not (is_sudo(user_id) or
                (current_member.status in ["administrator", "creator"] and
                 getattr(current_member, 'can_promote_members', False))):
            await update.message.reply_text(
                "👮 <b>You must be an admin with 'add admins' permission or sudo user to use this command!</b>",
                parse_mode="HTML"
            )
            return

        # Check bot's permissions
        bot_id = (await context.bot.get_me()).id
        try:
            bot_member = await context.bot.get_chat_member(chat_id, bot_id)
            if not (is_admin(bot_member) and getattr(bot_member, 'can_promote_members', False)):
                await update.message.reply_text(
                    "🤖 <b>I need to be admin with 'Add New Admins' permission to demote users!</b>",
                    parse_mode="HTML"
                )
                return
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to check my admin status:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
            return

        # Get target user
        target_user = await get_target_user(update, context)
        if not target_user:
            return

        # Prevent demoting protected users
        if target_user.id == sudo_users["lord"] or target_user.id in sudo_users.get("substitute_lords", set()):
            await update.message.reply_text(
                "👑 <b>You cannot demote the Lord or Substitute Lords with this command!</b>",
                parse_mode="HTML"
            )
            return

        # Get target member status
        try:
            target_member = await context.bot.get_chat_member(chat_id, target_user.id)
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to check target user status:\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")
            return

        # Check if target is admin
        if not is_admin(target_member):
            await update.message.reply_text("⚠️ <b>This user is not an admin!</b>", parse_mode="HTML")
            return

        # Prevent demoting the group owner
        if target_member.status == "creator":
            await update.message.reply_text("👑 <b>You can't demote the group owner!</b>", parse_mode="HTML")
            return

        # Special handling for bot demotion
        if target_user.id == bot_id:
            if not is_sudo(user_id):
                await update.message.reply_text(
                    "🤖 <b>Only my sudo users can demote me. Your action is blocked!</b>",
                    parse_mode="HTML"
                )
                return
            else:
                # Log sudo user demoting the bot
                logging.warning(f"Sudo user {user_id} is demoting the bot in chat {chat_id}")

        # Perform demotion
        try:
            await context.bot.promote_chat_member(
                chat_id=chat_id,
                user_id=target_user.id,
                can_change_info=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_video_chats=False,
                can_manage_topics=False,
                is_anonymous=False
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>Failed to demote user:</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
            return

        # Success message
        await update.message.reply_text(
            f"⬇️ <b>{target_user.mention_html()} has been demoted from admin status.</b>",
            parse_mode="HTML"
        )

        # Auto re-promote if bot itself was demoted by sudo user
        if target_user.id == bot_id and is_sudo(user_id):
            try:
                await context.bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=bot_id,
                    can_change_info=True,
                    can_post_messages=True,
                    can_edit_messages=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    can_manage_video_chats=True,
                    is_anonymous=False
                )
                logging.info(f"Bot auto-repromoted itself in chat {chat_id} after sudo demotion")
            except Exception as e:
                logging.error(f"Failed to auto-repromote bot in chat {chat_id}: {str(e)}")

    except Exception as e:
        logging.error(f"Error in demote command: {str(e)}")
        try:
            await update.message.reply_text(
                f"❌ <b>Unexpected error occurred:</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass


async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
                try:
                    if update.message.chat.type == "private":
                        await update.message.reply_text("🚫 This command can only be used in groups!", parse_mode="HTML")
                        return
                    user_id = update.effective_user.id
                    chat_id = update.effective_chat.id
                    try:
                        member = await context.bot.get_chat_member(chat_id, user_id)
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return
                    if not is_admin(member):
                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                        return
                    bot_id = (await context.bot.get_me()).id
                    try:
                        bot_member = await context.bot.get_chat_member(chat_id, bot_id)
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to fetch my admin status:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return
                    if not is_admin(bot_member):
                        await update.message.reply_text("🤖 <b>I need to be an admin to pin messages!</b>", parse_mode="HTML")
                        return
                    if not getattr(bot_member, "can_pin_messages", False):
                        await update.message.reply_text("❌ <b>I do not have the 'Pin Messages' permission.</b>", parse_mode="HTML")
                        return
                    if not update.message.reply_to_message:
                        await update.message.reply_text("📌 <b>Reply to the message you want to pin.</b>", parse_mode="HTML")
                        return
                    try:
                        await context.bot.pin_chat_message(chat_id, update.message.reply_to_message.message_id)
                        await update.message.reply_text("📌 <b>Message pinned successfully!</b>", parse_mode="HTML")
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to pin message:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                except Exception as e:
                    try:
                        await update.message.reply_text(
                            f"❌ <b>Unexpected error in pin command:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
async def lgc(update: Update, context: ContextTypes.DEFAULT_TYPE):
                            user_id = update.effective_user.id
                            chat_id = update.effective_chat.id
                            if user_id != sudo_users["lord"]:
                                await update.message.reply_text("🚫 <b>Only the Lord can use /lgc!</b>", parse_mode="HTML")
                                return
                            await update.message.reply_text("👋 <b>Leaving this chat as requested by the Lord.</b>", parse_mode="HTML")
                            try:
                                await context.bot.leave_chat(chat_id)
                            except Exception as e:
                                await update.message.reply_text(f"❌ <b>Failed to leave chat:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")
async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
                try:
                    if update.message.chat.type == "private":
                        await update.message.reply_text("🚫 This command can only be used in groups!", parse_mode="HTML")
                        return
                    user_id = update.effective_user.id
                    chat_id = update.effective_chat.id
                    try:
                        member = await context.bot.get_chat_member(chat_id, user_id)
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return
                    if not is_admin(member):
                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                        return
                    bot_id = (await context.bot.get_me()).id
                    try:
                        bot_member = await context.bot.get_chat_member(chat_id, bot_id)
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to fetch my admin status:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return
                    if not is_admin(bot_member):
                        await update.message.reply_text("🤖 <b>I need to be an admin to unpin messages!</b>", parse_mode="HTML")
                        return
                    if not getattr(bot_member, "can_pin_messages", False):
                        await update.message.reply_text("❌ <b>I do not have the 'Pin Messages' permission.</b>", parse_mode="HTML")
                        return
                    if update.message.reply_to_message:
                        try:
                            await context.bot.unpin_chat_message(chat_id, update.message.reply_to_message.message_id)
                            await update.message.reply_text("📍 <b>Message unpinned successfully!</b>", parse_mode="HTML")
                        except Exception as e:
                            await update.message.reply_text(
                                f"❌ <b>Failed to unpin message:</b>\n<code>{html.escape(str(e))}</code>",
                                parse_mode="HTML"
                            )
                    else:
                        try:
                            await context.bot.unpin_all_chat_messages(chat_id)
                            await update.message.reply_text("📍 <b>All pinned messages have been unpinned!</b>", parse_mode="HTML")
                        except Exception as e:
                            await update.message.reply_text(
                                f"❌ <b>Failed to unpin all messages:</b>\n<code>{html.escape(str(e))}</code>",
                                parse_mode="HTML"
                            )
                except Exception as e:
                    try:
                        await update.message.reply_text(
                            f"❌ <b>Unexpected error in unpin command:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass

async def tpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
                try:
                    if update.message.chat.type == "private":
                        await update.message.reply_text("🚫 This command can only be used in groups!", parse_mode="HTML")
                        return
                    user_id = update.effective_user.id
                    chat_id = update.effective_chat.id
                    try:
                        member = await context.bot.get_chat_member(chat_id, user_id)
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return
                    if not is_admin(member):
                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                        return
                    bot_id = (await context.bot.get_me()).id
                    try:
                        bot_member = await context.bot.get_chat_member(chat_id, bot_id)
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to fetch my admin status:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return
                    if not is_admin(bot_member):
                        await update.message.reply_text("🤖 <b>I need to be an admin to pin messages!</b>", parse_mode="HTML")
                        return
                    if not getattr(bot_member, "can_pin_messages", False):
                        await update.message.reply_text("❌ <b>I do not have the 'Pin Messages' permission.</b>", parse_mode="HTML")
                        return
                    if not update.message.reply_to_message:
                        await update.message.reply_text("📌 <b>Reply to the message you want to temporarily pin.</b>", parse_mode="HTML")
                        return
                    if not context.args or len(context.args) < 1:
                        await update.message.reply_text("⏳ <b>Please specify a duration (e.g. 10m, 2h, 1d, 30s).</b>", parse_mode="HTML")
                        return
                    duration_str = context.args[0]
                    match = re.match(r"^(\d+)([smhd])$", duration_str)
                    if not match:
                        await update.message.reply_text("⏳ <b>Invalid duration format! Use like 10m, 2h, 1d, 30s.</b>", parse_mode="HTML")
                        return
                    value, unit = int(match.group(1)), match.group(2)
                    delta = timedelta(seconds=value) if unit == "s" else \
                            timedelta(minutes=value) if unit == "m" else \
                            timedelta(hours=value) if unit == "h" else \
                            timedelta(days=value)
                    try:
                        await context.bot.pin_chat_message(chat_id, update.message.reply_to_message.message_id)
                        await update.message.reply_text(
                            f"📌 <b>Message pinned for {duration_str}!</b>", parse_mode="HTML"
                        )
                    except Exception as e:
                        await update.message.reply_text(
                            f"❌ <b>Failed to pin message:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                        return

                    async def unpin_later():
                        await asyncio.sleep(delta.total_seconds())
                        try:
                            await context.bot.unpin_chat_message(chat_id, update.message.reply_to_message.message_id)
                            await context.bot.send_message(
                                chat_id,
                                f"📍 <b>Message automatically unpinned after {duration_str}.</b>",
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            logging.error(f"Error auto-unpinning message: {e}")

                    asyncio.create_task(unpin_later())
                except Exception as e:
                    try:
                        await update.message.reply_text(
                            f"❌ <b>Unexpected error in tpin command:</b>\n<code>{html.escape(str(e))}</code>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                        # --- Admin Module Commands (Stylish) ---

admin_cache = defaultdict(list)
anon_admin_enabled = defaultdict(lambda: False)
admin_error_enabled = defaultdict(lambda: True)

async def update_admin_cache(chat_id, context):
                            try:
                                admins = await context.bot.get_chat_administrators(chat_id)
                                admin_cache[chat_id] = [admin.user.id for admin in admins]
                            except Exception as e:
                                logging.error(f"Failed to update admin cache: {e}")

async def adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        admins = await context.bot.get_chat_administrators(chat_id)

        # Separate owner and human admins (ignore bots)
        owner = None
        human_admins = []
        for admin in admins:
            if admin.status == "creator":
                owner = admin
            elif not admin.user.is_bot:
                human_admins.append(admin)

        text = "<b>👮 <u>Group Administration Panel</u></b>\n"
        text += "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"

        # Owner section
        text += "<b>👑 Owner:</b>\n"
        if owner:
            user = owner.user
            custom_title = f" <i>({html.escape(owner.custom_title)})</i>" if getattr(owner, "custom_title", None) else ""
            text += f"👑 <a href='tg://user?id={user.id}'>{html.escape(user.full_name)}</a>{custom_title}\n"
        else:
            text += "<i>Unknown</i>\n"

        text += "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        text += "<b>🛡 Admins:</b>\n"
        if human_admins:
            for admin in human_admins:
                user = admin.user
                custom_title = f" <i>({html.escape(admin.custom_title)})</i>" if getattr(admin, "custom_title", None) else ""
                text += f"🛡 <a href='tg://user?id={user.id}'>{html.escape(user.full_name)}</a>{custom_title}\n"
        else:
            text += "<i>None</i>\n"

        text += "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        text += "<i>This list shows the owner and all human admins for professional group management.</i>"

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>Failed to fetch admin list:</b>\n<code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

async def admincache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update_admin_cache(chat_id, context)
    await update.message.reply_text(
        "✅ <b>Admin cache updated!</b>\n<b>All hail the fresh admins!</b>",
        parse_mode="HTML"
    )


flood_settings = defaultdict(lambda: {
                            "limit": 5,  # default: 5 messages in a row
                            "mode": ("mute", None),  # ("action", duration) e.g. ("tban", "3d")
                            "clear": False,
                            "timer": None,  # (count, duration_in_seconds)
                        })
user_flood_data = defaultdict(lambda: defaultdict(lambda: {"count": 0, "last_time": None, "timer_msgs": []}))

def parse_duration(duration_str):
                            try:
                                match = re.match(r"^(\d+)([smhd])$", duration_str)
                                if not match:
                                    return None
                                value, unit = int(match.group(1)), match.group(2)
                                return value * (1 if unit == "s" else 60 if unit == "m" else 3600 if unit == "h" else 86400)
                            except Exception as e:
                                logging.error(f"parse_duration error: {e}")
                                return None

def parse_mode_args(args):
                            try:
                                if not args:
                                    return None, None
                                action = args[0].lower()
                                duration = args[1] if len(args) > 1 else None
                                if action in ("ban", "mute", "kick"):
                                    return (action, None)
                                if action in ("tban", "tmute") and duration:
                                    return (action, duration)
                                return None, None
                            except Exception as e:
                                logging.error(f"parse_mode_args error: {e}")
                                return None, None

# --- Antiflood (Flood Control) ---



                            # --- AntiRaid Settings ---
antiraid_settings = defaultdict(lambda: {
                                "enabled": False,
                                "until": None,
                                "duration": 6 * 3600,      # Default: 6h (in seconds)
                                "action_time": 3600,       # Default: 1h tempban (in seconds)
                                "auto": 0,                 # 0 = off
                                "auto_triggered": False,
                                "join_times": [],
                            })

def parse_time_arg(arg, default=None):
                                try:
                                    match = re.match(r"^(\d+)([smhd])$", arg)
                                    if not match:
                                        return default
                                    value, unit = int(match.group(1)), match.group(2)
                                    return value * (1 if unit == "s" else 60 if unit == "m" else 3600 if unit == "h" else 86400)
                                except Exception as e:
                                    logging.error(f"parse_time_arg error: {e}")
                                    return default

async def antiraid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                try:
                                    chat_id = update.effective_chat.id
                                    user_id = update.effective_user.id
                                    try:
                                        member = await context.bot.get_chat_member(chat_id, user_id)
                                    except Exception as e:
                                        await update.message.reply_text(
                                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                                            parse_mode="HTML"
                                        )
                                        return
                                    if not is_admin(member):
                                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                                        return
                                    settings = antiraid_settings[chat_id]
                                    now = datetime.now()
                                    if not context.args:
                                        if settings["enabled"] and settings["until"] and now < settings["until"]:
                                            left = settings["until"] - now
                                            await update.message.reply_text(
                                                f"🛡️ <b>Antiraid is currently <u>ENABLED</u> for another <code>{str(left).split('.')[0]}</code>.</b>",
                                                parse_mode="HTML"
                                            )
                                        else:
                                            await update.message.reply_text(
                                                "🛡️ <b>Antiraid is currently <u>DISABLED</u>.</b>",
                                                parse_mode="HTML"
                                            )
                                        return
                                    arg = context.args[0].lower()
                                    if arg in ("off", "no", "disable"):
                                        settings["enabled"] = False
                                        settings["until"] = None
                                        settings["auto_triggered"] = False
                                        try:
                                            await update.message.reply_animation(
                                                animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                                                caption="🛡️ <b>Antiraid disabled.</b>",
                                                parse_mode="HTML"
                                            )
                                        except Exception as e:
                                            logging.error(f"Failed to send antiraid disabled animation: {e}")
                                    else:
                                        duration = parse_time_arg(arg, settings["duration"])
                                        settings["enabled"] = True
                                        settings["until"] = datetime.now() + timedelta(seconds=duration)
                                        settings["auto_triggered"] = False
                                        try:
                                            await update.message.reply_animation(
                                                animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                                                caption=f"🛡️ <b>Antiraid enabled for <code>{arg}</code>!</b>\n"
                                                        f"All new joins will be tempbanned for {settings['action_time']//60} minutes.",
                                                parse_mode="HTML"
                                            )
                                        except Exception as e:
                                            logging.error(f"Failed to send antiraid enabled animation: {e}")
                                except Exception as e:
                                    logging.error(f"antiraid_command error: {e}")
                                    try:
                                        await update.message.reply_text(f"❌ <b>Error in antiraid command:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")
                                    except Exception:
                                        pass

async def raidtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                try:
                                    chat_id = update.effective_chat.id
                                    user_id = update.effective_user.id
                                    try:
                                        member = await context.bot.get_chat_member(chat_id, user_id)
                                    except Exception as e:
                                        await update.message.reply_text(
                                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                                            parse_mode="HTML"
                                        )
                                        return
                                    if not is_admin(member):
                                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                                        return
                                    settings = antiraid_settings[chat_id]
                                    if not context.args:
                                        await update.message.reply_text(
                                            f"⏳ <b>Current antiraid duration:</b> <code>{settings['duration']//3600}h</code>",
                                            parse_mode="HTML"
                                        )
                                        return
                                    arg = context.args[0].lower()
                                    duration = parse_time_arg(arg)
                                    if not duration:
                                        await update.message.reply_text("❓ <b>Usage:</b> /raidtime <duration> (e.g. 3h, 45m)", parse_mode="HTML")
                                        return
                                    settings["duration"] = duration
                                    try:
                                        await update.message.reply_animation(
                                            animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                                            caption=f"⏳ <b>Antiraid duration set to <code>{arg}</code>.</b>",
                                            parse_mode="HTML"
                                        )
                                    except Exception as e:
                                        logging.error(f"Failed to send raidtime animation: {e}")
                                except Exception as e:
                                    logging.error(f"raidtime_command error: {e}")
                                    try:
                                        await update.message.reply_text(f"❌ <b>Error in raidtime command:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")
                                    except Exception:
                                        pass

async def raidactiontime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                try:
                                    chat_id = update.effective_chat.id
                                    user_id = update.effective_user.id
                                    try:
                                        member = await context.bot.get_chat_member(chat_id, user_id)
                                    except Exception as e:
                                        await update.message.reply_text(
                                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                                            parse_mode="HTML"
                                        )
                                        return
                                    if not is_admin(member):
                                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                                        return
                                    settings = antiraid_settings[chat_id]
                                    if not context.args:
                                        await update.message.reply_text(
                                            f"⏳ <b>Current antiraid tempban time:</b> <code>{settings['action_time']//60}m</code>",
                                            parse_mode="HTML"
                                        )
                                        return
                                    arg = context.args[0].lower()
                                    duration = parse_time_arg(arg)
                                    if not duration:
                                        await update.message.reply_text("❓ <b>Usage:</b> /raidactiontime <duration> (e.g. 1h, 30m)", parse_mode="HTML")
                                        return
                                    settings["action_time"] = duration
                                    try:
                                        await update.message.reply_animation(
                                            animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                                            caption=f"⏳ <b>Antiraid tempban time set to <code>{arg}</code>.</b>",
                                            parse_mode="HTML"
                                        )
                                    except Exception as e:
                                        logging.error(f"Failed to send raidactiontime animation: {e}")
                                except Exception as e:
                                    logging.error(f"raidactiontime_command error: {e}")
                                    try:
                                        await update.message.reply_text(f"❌ <b>Error in raidactiontime command:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")
                                    except Exception:
                                        pass

async def autoantiraid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                try:
                                    chat_id = update.effective_chat.id
                                    user_id = update.effective_user.id
                                    try:
                                        member = await context.bot.get_chat_member(chat_id, user_id)
                                    except Exception as e:
                                        await update.message.reply_text(
                                            f"❌ <b>Failed to fetch your admin status:</b>\n<code>{html.escape(str(e))}</code>",
                                            parse_mode="HTML"
                                        )
                                        return
                                    if not is_admin(member):
                                        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                                        return
                                    settings = antiraid_settings[chat_id]
                                    if not context.args:
                                        if settings["auto"]:
                                            await update.message.reply_text(
                                                f"🤖 <b>Auto-antiraid is enabled:</b> triggers if <code>{settings['auto']}</code> users join in 1 minute.",
                                                parse_mode="HTML"
                                            )
                                        else:
                                            await update.message.reply_text(
                                                "🤖 <b>Auto-antiraid is <u>disabled</u>.</b>",
                                                parse_mode="HTML"
                                            )
                                        return
                                    arg = context.args[0].lower()
                                    if arg in ("off", "no", "0", "disable"):
                                        settings["auto"] = 0
                                        try:
                                            await update.message.reply_animation(
                                                animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                                                caption="🤖 <b>Auto-antiraid disabled.</b>",
                                                parse_mode="HTML"
                                            )
                                        except Exception as e:
                                            logging.error(f"Failed to send autoantiraid disabled animation: {e}")
                                    else:
                                        try:
                                            count = int(arg)
                                            if count < 2:
                                                await update.message.reply_text("❌ <b>Auto-antiraid threshold must be at least 2.</b>", parse_mode="HTML")
                                                return
                                            settings["auto"] = count
                                            try:
                                                await update.message.reply_animation(
                                                    animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                                                    caption=f"🤖 <b>Auto-antiraid enabled:</b> triggers if <code>{count}</code> users join in 1 minute.",
                                                    parse_mode="HTML"
                                                )
                                            except Exception as e:
                                                logging.error(f"Failed to send autoantiraid enabled animation: {e}")
                                        except Exception as e:
                                            logging.error(f"autoantiraid_command parse error: {e}")
                                            await update.message.reply_text("❓ <b>Usage:</b> /autoantiraid <number/off/no>", parse_mode="HTML")
                                except Exception as e:
                                    logging.error(f"autoantiraid_command error: {e}")
                                    try:
                                        await update.message.reply_text(f"❌ <b>Error in autoantiraid command:</b> <code>{html.escape(str(e))}</code>", parse_mode="HTML")
                                    except Exception:
                                        pass

async def antiraid_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                try:
                                    if not update.message or not update.message.new_chat_members:
                                        return
                                    chat_id = update.effective_chat.id
                                    settings = antiraid_settings[chat_id]
                                    now = datetime.now()
                                    # --- Auto-antiraid logic ---
                                    if settings["auto"]:
                                        try:
                                            # Clean up join_times older than 60s
                                            settings["join_times"] = [t for t in settings["join_times"] if (now - t).total_seconds() < 60]
                                            settings["join_times"].append(now)
                                            if not settings["enabled"] and len(settings["join_times"]) >= settings["auto"]:
                                                # Trigger antiraid automatically
                                                settings["enabled"] = True
                                                settings["until"] = now + timedelta(seconds=settings["duration"])
                                                settings["auto_triggered"] = True
                                                try:
                                                    await context.bot.send_message(
                                                        chat_id,
                                                        f"🚨 <b>Auto-antiraid triggered!</b>\n"
                                                        f"Too many users joined in a short time. Antiraid enabled for <code>{settings['duration']//3600}h</code>.",
                                                        parse_mode="HTML"
                                                    )
                                                except Exception as e:
                                                    logging.error(f"Failed to send auto-antiraid triggered message: {e}")
                                        except Exception as e:
                                            logging.error(f"Auto-antiraid join_times error: {e}")
                                    # --- Antiraid enforcement ---
                                    if settings["enabled"] and settings["until"] and now < settings["until"]:
                                        for user in update.message.new_chat_members:
                                            try:
                                                until = now + timedelta(seconds=settings["action_time"])
                                                try:
                                                    await context.bot.ban_chat_member(chat_id, user.id, until_date=until)
                                                    await context.bot.send_message(
                                                        chat_id,
                                                        f"🚫 <b>Antiraid:</b> {user.mention_html()} was tempbanned for {settings['action_time']//60}m.",
                                                        parse_mode="HTML"
                                                    )
                                                except Exception as e:
                                                    logging.error(f"Antiraid ban failed for user {user.id}: {e}")
                                            except Exception as e:
                                                logging.error(f"Antiraid enforcement error: {e}")
                                except Exception as e:
                                    logging.error(f"antiraid_join_handler error: {e}")

async def antiraid_cleanup_task(app):
                                try:
                                    while True:
                                        now = datetime.now()
                                        for chat_id, settings in list(antiraid_settings.items()):
                                            try:
                                                if settings["enabled"] and settings["until"] and now >= settings["until"]:
                                                    settings["enabled"] = False
                                                    settings["until"] = None
                                                    settings["auto_triggered"] = False
                                                    try:
                                                        await app.bot.send_message(
                                                            chat_id,
                                                            "🛡️ <b>Antiraid period ended. New users can join again.</b>",
                                                            parse_mode="HTML"
                                                        )
                                                    except Exception as e:
                                                        logging.error(f"Failed to send antiraid period ended message: {e}")
                                            except Exception as e:
                                                logging.error(f"antiraid_cleanup_task chat loop error: {e}")
                                        await asyncio.sleep(30)
                                except Exception as e:
                                    logging.error(f"antiraid_cleanup_task main error: {e}")



HELP_PAGES = [
    [
        [
            InlineKeyboardButton("Ban", callback_data="help_ban"),
            InlineKeyboardButton("Unban", callback_data="help_unban"),
            InlineKeyboardButton("Warn", callback_data="help_warn"),
        ],
        [
            InlineKeyboardButton("Mute", callback_data="help_mute"),
            InlineKeyboardButton("Unmute", callback_data="help_unmute"),
            InlineKeyboardButton("Tmute", callback_data="help_tmute"),
        ],
        [
            InlineKeyboardButton("Pin", callback_data="help_pin"),
            InlineKeyboardButton("Unpin", callback_data="help_unpin"),
            InlineKeyboardButton("Tpin", callback_data="help_tpin"),
        ],
        [
            InlineKeyboardButton("Promote", callback_data="help_lowpromote"),
            InlineKeyboardButton("Demote", callback_data="help_demote"),
            InlineKeyboardButton("Adminlist", callback_data="help_adminlist"),
        ],
        [
            InlineKeyboardButton("Antiraid", callback_data="help_antiraid"),
            InlineKeyboardButton("Speedtest", callback_data="help_speedtest"),
            InlineKeyboardButton("ID", callback_data="help_id"),
        ],
        [
            InlineKeyboardButton("XO", callback_data="help_xo"),
            InlineKeyboardButton("RPS", callback_data="help_rps"),
            InlineKeyboardButton("Connect4", callback_data="help_connect4"),
        ],
        [
            InlineKeyboardButton("Wordgame", callback_data="help_wordgame"),
            InlineKeyboardButton("Explainword", callback_data="help_explainword"),
            InlineKeyboardButton("Chess", callback_data="help_chess"),
        ],
        [
            InlineKeyboardButton("Blocklist", callback_data="help_blocklist"),
            InlineKeyboardButton("Lock", callback_data="help_lock"),
            InlineKeyboardButton("Unlock", callback_data="help_unlock"),
        ],
        [
            InlineKeyboardButton("Rules", callback_data="help_rules"),
            InlineKeyboardButton("Welcome", callback_data="help_welcome"),
            InlineKeyboardButton("Goodbye", callback_data="help_goodbye"),
        ],
        [
            InlineKeyboardButton("Stats", callback_data="help_stats"),
            InlineKeyboardButton("Sudo", callback_data="help_addsudo"),
            InlineKeyboardButton("Restart", callback_data="help_restart"),
        ],
    ]
]

def get_help_page(page: int):
    page = max(1, min(page, len(HELP_PAGES)))
    rows = [row[:] for row in HELP_PAGES[page - 1] if row]
    close_btn = InlineKeyboardButton("❌ Close", callback_data="help_close")
    if page == 1:
        nav_row = [close_btn, InlineKeyboardButton("➡️ Next", callback_data="help_page_2")]
    elif page == len(HELP_PAGES):
        nav_row = [InlineKeyboardButton("⬅️ Back", callback_data=f"help_page_{page-1}"), close_btn]
    else:
        nav_row = [
            InlineKeyboardButton("⬅️ Back", callback_data=f"help_page_{page-1}"),
            close_btn,
            InlineKeyboardButton("➡️ Next", callback_data=f"help_page_{page+1}")
        ]
    rows.append(nav_row)
    return rows

# Store help message IDs per user (for deletion)
help_msg_ids = defaultdict(list)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    help_text = (
        "<b>🆘 MonarchX Help Center</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Select a command below to view detailed usage and professional guidance.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )
    if chat.type in ("group", "supergroup"):
        bot_me = await context.bot.get_me()
        pm_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("📬 Contact me in PM for help!", url=f"https://t.me/{bot_me.username}?start=help")]
        ])
        msg = await update.message.reply_text(
            "ℹ️ <b>Contact me in PM for help!</b>\n"
            "Press the button below to get the full help menu in private chat.\n"
            "Or simply send <code>/help</code> in my PM.",
            parse_mode="HTML",
            reply_markup=pm_button
        )
        help_msg_ids[user.id] = [msg.message_id]
        try:
            await context.bot.send_message(
                user.id,
                "Type <code>/help</code> here to get the full help menu.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return
    msg = await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(get_help_page(1))
    )
    help_msg_ids[user.id] = [msg.message_id]

async def help_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id if query else update.effective_user.id
    chat_id = query.message.chat.id if query else update.effective_chat.id
    arg = query.data if query else (context.args[0].lower() if context.args else "")
    old_msg_id = query.message.message_id if query else None

    async def send_new_help(text, reply_markup=None):
        # Delete all previous help messages for this user in this chat
        for mid in help_msg_ids[user_id]:
            try:
                await context.bot.delete_message(chat_id, mid)
            except Exception:
                pass
        msg = await context.bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        help_msg_ids[user_id] = [msg.message_id]

    if arg.startswith("help_page_"):
        try:
            page = int(arg.split("_")[-1])
        except Exception:
            page = 1
        help_text = (
            "<b>🆘 MonarchX Help Center</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Select a command below to view detailed usage and professional guidance.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await send_new_help(
            help_text,
            reply_markup=InlineKeyboardMarkup(get_help_page(page))
        )
        return
    if arg == "help_back":
        help_text = (
            "<b>🆘 MonarchX Help Center</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Select a command below to view detailed usage and professional guidance.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await send_new_help(
            help_text,
            reply_markup=InlineKeyboardMarkup(get_help_page(1))
        )
        return
    if arg == "help_close":
        # Delete all help messages for this user in this chat
        for mid in help_msg_ids[user_id]:
            try:
                await context.bot.delete_message(chat_id, mid)
            except Exception:
                pass
        help_msg_ids[user_id] = []
        return

    # --- Help details ---
    text = ""
    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="help_back")]])
    if arg == "help_ban":
        text = (
            "<b>Ban Commands</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>/ban</b> — Ban a user from the group.\n"
            "Usage: <code>/ban</code> (reply or user ID/username)\n"
            "Example: <code>/ban @username</code>\n"
            "You may also reply to a user's message with <code>/ban</code>.\n"
            "\n"
            "<b>/tban</b> — Temporarily ban a user for a specified duration.\n"
            "Usage: <code>/tban</code> (reply or user ID/username) <code>duration</code>\n"
            "Example: <code>/tban @user 1d</code> (bans for 1 day)\n"
            "Duration format: <code>10m</code> (minutes), <code>2h</code> (hours), <code>1d</code> (days), <code>30s</code> (seconds)\n"
            "\n"
            "<b>/unban</b> — Unban a user.\n"
            "Usage: <code>/unban</code> (reply or user ID/username)\n"
            "\n"
            "<b>/banall</b> — Ban all users in all groups (Lord only, confirmation required).\n"
            "<b>/gban</b> — Globally ban a user from all groups (sudo only).\n"
            "\n"
            "<b>Notes:</b>\n"
            "• Only admins can use ban commands.\n"
            "• Sudo users, Lord, and Substitute Lords are protected from bans.\n"
            "• Use <code>/unban</code> or <code>/ungban</code> to remove bans.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
    elif arg == "help_unban":
        text = (
            "<b>/unban</b> — Unban a user.\n"
            "Usage: <code>/unban</code> (reply or user ID/username)\n"
            "Example: <code>/unban @username</code>"
        )
    elif arg == "help_warn":
        text = (
            "<b>Warn System</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>/warn</b> — Issue a warning to a user. After reaching the maximum, the user is banned.\n"
            "Usage: <code>/warn</code> (reply or user ID/username) [reason]\n"
            "Example: <code>/warn @user Spamming</code>\n"
            "\n"
            "<b>/unwarn</b> — Remove a warning from a user.\n"
            "<b>/warns</b> — Display the current warning count for a user.\n"
            "\n"
            "<b>Automatic Warnings:</b>\n"
            "• Blocklist, lock, and sticker violations can trigger automatic warnings if enabled.\n"
            "• After 3 warnings (default), the user is automatically banned.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
    # ... (rest of help texts as before, unchanged)
    # For brevity, only a few are shown here. Copy the rest from your original code.
    # Each help text should be followed by:
    # await send_new_help(text, reply_markup=back_btn)
    # and return.

    # Example for one more:
    elif arg == "help_unwarn":
        text = (
            "<b>/unwarn</b> — Remove a warning from a user.\n"
            "Usage: <code>/unwarn</code> (reply or user ID/username)"
        )
    # ... (repeat for all help_xxx cases)
    # If not matched, show main help
    if not text:
        text = (
            "<b>🆘 MonarchX Help Center</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Select a command below to view detailed usage and professional guidance.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await send_new_help(
            text,
            reply_markup=InlineKeyboardMarkup(get_help_page(1))
        )
        return

    await send_new_help(text, reply_markup=back_btn)

# Register the callback handler in your main section:

    # --- XO Game (Tic-Tac-Toe) ---

active_xo_games = {}

async def xo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        if chat_id in active_xo_games:
            await update.message.reply_text("❗️ A Tic-Tac-Toe game is already running in this chat!")
            return
        active_xo_games[chat_id] = {
            "players": [update.effective_user.id],
            "symbols": {},
            "board": [[" " for _ in range(3)] for _ in range(3)],
            "turn": 0,
            "started": False,
            "usernames": {update.effective_user.id: update.effective_user.first_name},
            "message_id": None
        }
        msg = await update.message.reply_text(
            "✅ Waiting for the second player. Another user should send /joinxo to join."
        )
        active_xo_games[chat_id]["message_id"] = msg.message_id
    except Exception as e:
        logging.error(f"Error in xo_start: {e}")
        await update.message.reply_text("❌ Oops! Something went wrong starting the game.")

async def xo_players_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

async def join_xo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        game = active_xo_games.get(chat_id)
        if not game:
            await update.message.reply_text("❌ No game found. Start a game with /xo.")
            return
        if len(game["players"]) >= 2:
            await update.message.reply_text("❌ The game already has 2 players!")
            return
        if update.effective_user.id in game["players"]:
            await update.message.reply_text("❗️ You already joined this game!")
            return
        game["players"].append(update.effective_user.id)
        game["usernames"][update.effective_user.id] = update.effective_user.first_name
        game["symbols"] = {game["players"][0]: "❌", game["players"][1]: "⭕️"}
        game["started"] = True
        start_message = (
            f"🎲 Tic-Tac-Toe started!\n"
            f"{game['usernames'][game['players'][0]]} is ❌\n"
            f"{game['usernames'][game['players'][1]]} is ⭕️\n"
            f"{game['usernames'][game['players'][0]]} goes first.\n\n"
            "Tap an empty cell below to make your move:"
        )
        msg_id = game.get("message_id")
        if msg_id:
            await context.bot.edit_message_text(
                start_message,
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=None
            )
            await show_xo_board(update, context, chat_id, edit=True)
        else:
            msg = await update.message.reply_text(start_message)
            game["message_id"] = msg.message_id
            await show_xo_board(update, context, chat_id, edit=True)
    except Exception as e:
        logging.error(f"Error in join_xo: {e}")
        await update.message.reply_text("❌ Error while joining the game.")

async def xo_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        data = query.data
        if data.startswith("xo_move:"):
            parts = data.split(":")
            if len(parts) != 3:
                return
            row = int(parts[1])
            col = int(parts[2])
            chat_id = update.effective_chat.id
            game = active_xo_games.get(chat_id)
            if not game or not game.get("started"):
                await query.edit_message_text("❌ No active game. Start one with /xo!")
                return
            user_id = query.from_user.id
            if user_id not in game["players"]:
                await query.answer("❌ You are not playing this game!", show_alert=True)
                return
            if game["players"][game["turn"]] != user_id:
                await query.answer("⏳ It's not your turn yet!", show_alert=True)
                return
            if game["board"][row][col] != " ":
                await query.answer("❌ This cell is already taken!", show_alert=True)
                return
            symbol = game["symbols"][user_id]
            game["board"][row][col] = symbol
            await show_xo_board(update, context, chat_id, edit=True)
            winner = check_xo_winner(game["board"])
            msg_id = game.get("message_id")
            if winner:
                if msg_id:
                    await context.bot.edit_message_text(
                        f"🏆 {game['usernames'][user_id]} ({symbol}) wins! Congratulations!",
                        chat_id=chat_id,
                        message_id=msg_id,
                        parse_mode="HTML"
                    )
                else:
                    await context.bot.send_message(chat_id, f"🏆 {game['usernames'][user_id]} ({symbol}) wins! Congratulations!")
                active_xo_games.pop(chat_id, None)
                return
            if all(cell != " " for row_ in game["board"] for cell in row_):
                if msg_id:
                    await context.bot.edit_message_text(
                        "🤝 It's a draw! Great game everyone.",
                        chat_id=chat_id,
                        message_id=msg_id,
                        parse_mode="HTML"
                    )
                else:
                    await context.bot.send_message(chat_id, "🤝 It's a draw! Great game everyone.")
                active_xo_games.pop(chat_id, None)
                return
            game["turn"] = 1 - game["turn"]
            await show_xo_board(update, context, chat_id, edit=True)
    except Exception as e:
        logging.error(f"Error in xo_button_handler: {e}")

def check_xo_winner(board):
    try:
        for i in range(3):
            if board[i][0] != " " and board[i][0] == board[i][1] == board[i][2]:
                return board[i][0]
            if board[0][i] != " " and board[0][i] == board[1][i] == board[2][i]:
                return board[0][i]
        if board[0][0] != " " and board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        if board[0][2] != " " and board[0][2] == board[1][1] == board[2][0]:
            return board[0][2]
    except Exception as e:
        logging.error(f"Error in check_xo_winner: {e}")
    return None

async def show_xo_board(update, context, chat_id, edit: bool = False):
    try:
        game = active_xo_games.get(chat_id)
        if not game:
            return
        board = game["board"]
        inline_buttons = []
        for i in range(3):
            row_buttons = []
            for j in range(3):
                cell = board[i][j]
                display = cell if cell != " " else "⬜️"
                callback = f"xo_move:{i}:{j}" if cell == " " else "none"
                row_buttons.append(InlineKeyboardButton(display, callback_data=callback))
            inline_buttons.append(row_buttons)
        reply_markup = InlineKeyboardMarkup(inline_buttons)
        turn_player = game["players"][game["turn"]]
        turn_text = f"<b>Tic-Tac-Toe</b>\n"
        turn_text += f"Turn: {game['usernames'][turn_player]} ({game['symbols'][turn_player]})\n"
        turn_text += "Make your move by tapping an empty cell:"
        msg_id = game.get("message_id")
        if edit and msg_id:
            try:
                await context.bot.edit_message_text(
                    turn_text,
                    chat_id=chat_id,
                    message_id=msg_id,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error editing board message: {e}")
        elif msg_id:
            try:
                await context.bot.edit_message_text(
                    turn_text,
                    chat_id=chat_id,
                    message_id=msg_id,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error editing board message: {e}")
        else:
            msg = await context.bot.send_message(chat_id, turn_text, parse_mode="HTML", reply_markup=reply_markup)
            game["message_id"] = msg.message_id
    except Exception as e:
        logging.error(f"Error in show_xo_board: {e}")
        await context.bot.send_message(chat_id, "❌ Failed to display the board.", parse_mode="HTML")

async def cancel_xo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        game = active_xo_games.get(chat_id)
        msg_id = game.get("message_id") if game else None
        if chat_id in active_xo_games:
            active_xo_games.pop(chat_id, None)
            if msg_id:
                await context.bot.edit_message_text(
                    "❌ Tic-Tac-Toe game cancelled.",
                    chat_id=chat_id,
                    message_id=msg_id
                )
            else:
                await update.message.reply_text("❌ Tic-Tac-Toe game cancelled.")
        else:
            await update.message.reply_text("No active game to cancel.")
    except Exception as e:
        logging.error(f"Error in cancel_xo: {e}")
        await update.message.reply_text("❌ Could not cancel the game due to an unexpected error.")

    # --- Rock Paper Scissors ---

    # --- Rock Paper Scissors (RPS) ---

active_rps_games = {}

RPS_CHOICES = ["🪨 Rock", "📄 Paper", "✂️ Scissors"]
RPS_EMOJI = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
def rps_result(choice1, choice2):
    if choice1 == choice2:
        return 0  # Draw
    wins = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
    return 1 if wins[choice1] == choice2 else 2

async def rps(update, context):
    try:
        chat_id = update.effective_chat.id
        if chat_id in active_rps_games:
            await update.message.reply_text(
                "❗ <b>A Rock Paper Scissors game is already running in this chat!</b>",
                parse_mode="HTML"
            )
            return
        active_rps_games[chat_id] = {
            "players": [update.effective_user.id],
            "usernames": {update.effective_user.id: update.effective_user.first_name},
            "choices": {},
            "started": False
        }
        await update.message.reply_text(
            "🎮 <b>Rock Paper Scissors Game Started!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Player 1: {update.effective_user.mention_html()}\n"
            "Waiting for a second player...\n"
            "<i>Send /joinrps to join the game!</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Error in rps: {e}")
        await update.message.reply_text(
            "❌ <b>Failed to start Rock Paper Scissors game.</b>",
            parse_mode="HTML"
        )

async def joinrps(update, context):
    try:
        chat_id = update.effective_chat.id
        game = active_rps_games.get(chat_id)
        if not game:
            await update.message.reply_text(
                "❌ <b>No active Rock Paper Scissors game. Start one with /rps.</b>",
                parse_mode="HTML"
            )
            return
        if len(game["players"]) >= 2:
            await update.message.reply_text(
                "❌ <b>The game already has 2 players!</b>",
                parse_mode="HTML"
            )
            return
        if update.effective_user.id in game["players"]:
            await update.message.reply_text(
                "❗ <b>You have already joined the game.</b>",
                parse_mode="HTML"
            )
            return
        game["players"].append(update.effective_user.id)
        game["usernames"][update.effective_user.id] = update.effective_user.first_name
        game["started"] = True
        await update.message.reply_text(
            f"✅ <b>{update.effective_user.mention_html()} joined!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Both players, please select your move:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨 Rock", callback_data="rps_choice:rock"),
                    InlineKeyboardButton("📄 Paper", callback_data="rps_choice:paper"),
                    InlineKeyboardButton("✂️ Scissors", callback_data="rps_choice:scissors"),
                ]
            ])
        )
    except Exception as e:
        logging.error(f"Error in joinrps: {e}")
        await update.message.reply_text(
            "❌ <b>Failed to join Rock Paper Scissors game.</b>",
            parse_mode="HTML"
        )

async def rps_button_handler(update, context):
    try:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        data = query.data
        if not data.startswith("rps_choice:"):
            return
        choice = data.split(":")[1]
        chat_id = update.effective_chat.id
        user_id = query.from_user.id
        game = active_rps_games.get(chat_id)
        if not game or not game.get("started"):
            await query.edit_message_text(
                "❌ <b>No active Rock Paper Scissors game. Start one with /rps.</b>",
                parse_mode="HTML"
            )
            return
        if user_id not in game["players"]:
            await query.answer("❌ You are not a player in this game!", show_alert=True)
            return
        if user_id in game["choices"]:
            await query.answer("❗ You have already made your choice.", show_alert=True)
            return
        if choice not in RPS_EMOJI:
            await query.answer("❌ Invalid choice.", show_alert=True)
            return
        game["choices"][user_id] = choice
        await query.answer(f"You chose {RPS_EMOJI[choice]}")
        # If both players have chosen, determine result
        if len(game["choices"]) == 2:
            p1, p2 = game["players"]
            c1, c2 = game["choices"][p1], game["choices"][p2]
            uname1, uname2 = game["usernames"][p1], game["usernames"][p2]
            result = rps_result(c1, c2)
            result_text = (
                "🪨📄✂️ <b>Rock Paper Scissors Result</b> 🪨📄✂️\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{uname1}: <b>{RPS_EMOJI[c1]}</b>\n"
                f"{uname2}: <b>{RPS_EMOJI[c2]}</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
            )
            if result == 0:
                result_text += "🤝 <b>It's a draw!</b>"
            elif result == 1:
                result_text += f"🏆 <b>{uname1} wins!</b>"
            else:
                result_text += f"🏆 <b>{uname2} wins!</b>"
            await context.bot.send_message(
                chat_id=chat_id,
                text=result_text,
                parse_mode="HTML"
            )
            active_rps_games.pop(chat_id, None)
        else:
            await query.answer("✅ Choice registered. Waiting for the other player.", show_alert=False)
    except Exception as e:
        logging.error(f"Error in rps_button_handler: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred.", show_alert=True)
        except Exception:
            pass

async def cancelrps(update, context):
    try:
        chat_id = update.effective_chat.id
        if chat_id in active_rps_games:
            active_rps_games.pop(chat_id, None)
            await update.message.reply_text(
                "❌ <b>Rock Paper Scissors game cancelled.</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("No active Rock Paper Scissors game to cancel.")
    except Exception as e:
        logging.error(f"Error in cancelrps: {e}")
        await update.message.reply_text(
            "❌ <b>Could not cancel the game due to an unexpected error.</b>",
            parse_mode="HTML"
        )
    # --- Connect 4 ---
    # Connect 4 game implementation with error handling


active_connect4_games = {}

def create_empty_board():
    return [[" " for _ in range(7)] for _ in range(6)]

# --- Connect 4 Game (Stylish, Ask for Number of Players First) ---

def board_to_text(board):
    symbol_map = {" ": "⚪", "🔴": "🔴", "🟡": "🟡"}
    lines = []
    for row in board:
        lines.append("".join(symbol_map.get(cell, cell) for cell in row))
    lines.append("1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣")
    return "\n".join(lines)

def drop_disc(board, col, symbol):
    for row in reversed(range(6)):
        if board[row][col] == " ":
            board[row][col] = symbol
            return row
    return None

def check_connect4_winner(board, symbol):
    rows, cols = 6, 7
    # Horizontal
    for r in range(rows):
        for c in range(cols - 3):
            if all(board[r][c + i] == symbol for i in range(4)):
                return True
    # Vertical
    for c in range(cols):
        for r in range(rows - 3):
            if all(board[r + i][c] == symbol for i in range(4)):
                return True
    # Diagonal descending
    for r in range(rows - 3):
        for c in range(cols - 3):
            if all(board[r + i][c + i] == symbol for i in range(4)):
                return True
    # Diagonal ascending
    for r in range(3, rows):
        for c in range(cols - 3):
            if all(board[r - i][c + i] == symbol for i in range(4)):
                return True
    return False

CONNECT4_START_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbG1qZ2Z1d3J6d3Z2b2J6a2Z3d2JkZ3F2b2J6a2Z3d2JkZ3F2/g9582DNuQppxC/giphy.gif"
CONNECT4_WIN_GIF = "https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif"
CONNECT4_DRAW_GIF = "https://media.giphy.com/media/1QwQb1g1wEAAAAC/tic-tac-toe-draw.gif"
CONNECT4_CANCEL_GIF = "https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif"

# --- Ask for number of players first ---

async def connect4_start(update, context):
    try:
        chat_id = update.effective_chat.id
        if chat_id in active_connect4_games:
            await update.message.reply_animation(
                animation=CONNECT4_CANCEL_GIF,
                caption="❗ <b>A Connect 4 game is already running in this chat!</b>",
                parse_mode="HTML"
            )
            return
        # Ask for number of players (2 or 3/4 for teams)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("2 Players", callback_data="c4_players:2"),
                InlineKeyboardButton("3 Players", callback_data="c4_players:3"),
                InlineKeyboardButton("4 Players", callback_data="c4_players:4"),
            ]
        ])
        await update.message.reply_text(
            "<b>🎮 Connect 4</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "How many players will play?\n"
            "Choose the number of players below:",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Error in connect4_start: {e}")
        await update.message.reply_animation(
            animation=CONNECT4_CANCEL_GIF,
            caption="❌ <b>Failed to start Connect 4 game.</b>",
            parse_mode="HTML"
        )

async def connect4_players_callback(update, context):
    try:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        chat_id = query.message.chat.id
        if chat_id in active_connect4_games:
            await query.edit_message_caption(
                caption="❗ <b>A Connect 4 game is already running in this chat!</b>",
                parse_mode="HTML"
            )
            return
        num_players = int(query.data.split(":")[1])
        # Start the game with the user who pressed the button
        active_connect4_games[chat_id] = {
            "players": [query.from_user.id],
            "symbols": {},
            "board": create_empty_board(),
            "turn": 0,
            "started": False,
            "usernames": {query.from_user.id: query.from_user.first_name},
            "message_id": None,
            "max_players": num_players
        }
        msg = await query.message.reply_animation(
            animation=CONNECT4_START_GIF,
            caption=(
                f"🎮 <b>Connect 4 Game Started!</b>\n"
                "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                f"Player 1: {query.from_user.mention_html()} (🔴)\n"
                f"Waiting for {num_players - 1} more player(s)...\n"
                "<i>Send /joinc4 to join the game!</i>"
            ),
            parse_mode="HTML"
        )
        active_connect4_games[chat_id]["message_id"] = msg.message_id
    except Exception as e:
        logging.error(f"Error in connect4_players_callback: {e}")
        await update.callback_query.message.reply_animation(
            animation=CONNECT4_CANCEL_GIF,
            caption="❌ <b>Failed to start Connect 4 game.</b>",
            parse_mode="HTML"
        )

async def join_connect4(update, context):
    try:
        chat_id = update.effective_chat.id
        game = active_connect4_games.get(chat_id)
        if not game:
            await update.message.reply_animation(
                animation=CONNECT4_CANCEL_GIF,
                caption="❌ <b>No active Connect 4 game. Start one with /connect4.</b>",
                parse_mode="HTML"
            )
            return
        max_players = game.get("max_players", 2)
        if len(game["players"]) >= max_players:
            await update.message.reply_animation(
                animation=CONNECT4_CANCEL_GIF,
                caption="❌ <b>The game already has the maximum number of players!</b>",
                parse_mode="HTML"
            )
            return
        if update.effective_user.id in game["players"]:
            await update.message.reply_animation(
                animation=CONNECT4_CANCEL_GIF,
                caption="❗ <b>You have already joined the game.</b>",
                parse_mode="HTML"
            )
            return
        game["players"].append(update.effective_user.id)
        game["usernames"][update.effective_user.id] = update.effective_user.first_name
        # Assign symbols: cycle through 🔴, 🟡, 🔵, 🟢 for up to 4 players
        symbol_cycle = ["🔴", "🟡", "🔵", "🟢"]
        game["symbols"] = {pid: symbol_cycle[i] for i, pid in enumerate(game["players"])}
        if len(game["players"]) < max_players:
            await update.message.reply_animation(
                animation=CONNECT4_START_GIF,
                caption=(
                    f"✅ <b>{update.effective_user.mention_html()} joined!</b>\n"
                    "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n" +
                    "\n".join(
                        f"{game['usernames'][pid]} is {game['symbols'][pid]}"
                        for pid in game["players"]
                    ) +
                    f"\nWaiting for {max_players - len(game['players'])} more player(s)...\n"
                    "<i>Send /joinc4 to join the game!</i>"
                ),
                parse_mode="HTML"
            )
            return
        # All players joined, start the game
        game["started"] = True
        await update.message.reply_animation(
            animation=CONNECT4_START_GIF,
            caption=(
                f"✅ <b>{update.effective_user.mention_html()} joined!</b>\n"
                "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n" +
                "\n".join(
                    f"{game['usernames'][pid]} is {game['symbols'][pid]}"
                    for pid in game["players"]
                ) +
                f"\nTurn: <b>{game['usernames'][game['players'][0]]} ({game['symbols'][game['players'][0]]})</b>\n"
                "<i>Tap a column below to drop your disc!</i>"
            ),
            parse_mode="HTML"
        )
        await show_connect4_board(update, context, chat_id, message_id=game.get("message_id"))
    except Exception as e:
        logging.error(f"Error in join_connect4: {e}")
        await update.message.reply_animation(
            animation=CONNECT4_CANCEL_GIF,
            caption="❌ <b>Failed to join Connect 4 game.</b>",
            parse_mode="HTML"
        )

async def show_connect4_board(update, context, chat_id, message_id=None):
    try:
        game = active_connect4_games.get(chat_id)
        if not game:
            return
        board_text = board_to_text(game["board"])
        buttons = [
            InlineKeyboardButton(str(col + 1), callback_data=f"c4_move:{col}")
            for col in range(7)
        ]
        keyboard = InlineKeyboardMarkup([buttons])
        turn_user = game['usernames'][game['players'][game['turn']]]
        turn_symbol = game['symbols'][game['players'][game['turn']]]
        caption = (
            f"<b>🟡🔴 Connect 4</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"{board_text}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"🎲 <b>Turn:</b> {turn_user} ({turn_symbol})\n"
            f"<i>Tap a column below to drop your disc!</i>"
        )
        if message_id:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            msg = await context.bot.send_message(
                chat_id, caption, parse_mode="HTML", reply_markup=keyboard
            )
            game["message_id"] = msg.message_id
    except Exception as e:
        logging.error(f"Error in show_connect4_board: {e}")

async def connect4_button_handler(update, context):
    try:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        data = query.data
        if not data.startswith("c4_move:"):
            return
        col = int(data.split(":")[1])
        chat_id = update.effective_chat.id
        game = active_connect4_games.get(chat_id)
        if not game or not game.get("started"):
            await query.edit_message_text(
                "❌ <b>No active Connect 4 game. Start one with /connect4.</b>",
                parse_mode="HTML"
            )
            return
        user_id = query.from_user.id
        if game["players"][game["turn"]] != user_id:
            await query.answer("⏳ It's not your turn!", show_alert=True)
            return
        row = drop_disc(game["board"], col, game["symbols"][user_id])
        if row is None:
            await query.answer("❌ Column is full!", show_alert=True)
            return

        if check_connect4_winner(game["board"], game["symbols"][user_id]):
            await show_connect4_board(update, context, chat_id, message_id=game.get("message_id"))
            await context.bot.send_animation(
                chat_id,
                animation=CONNECT4_WIN_GIF,
                caption=(
                    f"🏆 <b>{game['usernames'][user_id]} ({game['symbols'][user_id]}) wins!</b>\n"
                    "<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                    "<i>Congratulations! 🎉</i>"
                ),
                parse_mode="HTML"
            )
            active_connect4_games.pop(chat_id, None)
            return

        # Draw: if top row is filled
        if all(game["board"][0][c] != " " for c in range(7)):
            await show_connect4_board(update, context, chat_id, message_id=game.get("message_id"))
            await context.bot.send_animation(
                chat_id,
                animation=CONNECT4_DRAW_GIF,
                caption="🤝 <b>It's a draw! Great game everyone.</b>",
                parse_mode="HTML"
            )
            active_connect4_games.pop(chat_id, None)
            return

        # Switch turn (cycle through all players)
        game["turn"] = (game["turn"] + 1) % len(game["players"])
        await show_connect4_board(update, context, chat_id, message_id=game.get("message_id"))
    except Exception as e:
        logging.error(f"Error in connect4_button_handler: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred.", show_alert=True)
        except Exception:
            pass

async def cancel_connect4(update, context):
    try:
        chat_id = update.effective_chat.id
        game = active_connect4_games.get(chat_id)
        msg_id = game.get("message_id") if game else None
        if not game:
            await update.message.reply_text("No active Connect 4 game to cancel.")
            return
        # If fewer than 2 players have joined, wait 30 seconds for a chance to join
        if len(game["players"]) < 2:
            await update.message.reply_animation(
                animation=CONNECT4_CANCEL_GIF,
                caption="⏳ <b>Waiting for a second player. The game will be cancelled in 30 seconds if no one joins.</b>",
                parse_mode="HTML"
            )
            await asyncio.sleep(30)
            # Re-check the game state after waiting
            game = active_connect4_games.get(chat_id)
            if game and len(game["players"]) < 2:
                active_connect4_games.pop(chat_id, None)
                if msg_id:
                    try:
                        await context.bot.edit_message_caption(
                            chat_id=chat_id,
                            message_id=msg_id,
                            caption="❌ <b>Connect 4 game cancelled due to inactivity.</b>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                await update.message.reply_animation(
                    animation=CONNECT4_CANCEL_GIF,
                    caption="❌ <b>Connect 4 game cancelled due to inactivity.</b>",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("A second player joined. Cancellation aborted.")
        else:
            active_connect4_games.pop(chat_id, None)
            if msg_id:
                try:
                    await context.bot.edit_message_caption(
                        chat_id=chat_id,
                        message_id=msg_id,
                        caption="❌ <b>Connect 4 game cancelled.</b>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            await update.message.reply_animation(
                animation=CONNECT4_CANCEL_GIF,
                caption="❌ <b>Connect 4 game cancelled.</b>",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"Error in cancel_connect4: {e}")
        await update.message.reply_animation(
            animation=CONNECT4_CANCEL_GIF,
            caption="❌ <b>Failed to cancel the Connect 4 game.</b>",
            parse_mode="HTML"
        )



active_explain_games = {}
explain_leaderboard = defaultdict(lambda: defaultdict(int))  # {chat_id: {user_id: points}}

def pick_random_word():
    word = random.choice(WORD_LIST)
    clue = f"Word length: {len(word)}"
    return clue, word

async def explainword_start(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        if chat_id in active_explain_games:
            await update.message.reply_text(
                "❗ <b>An explain & guess game is already running in this chat!</b>",
                parse_mode="HTML"
            )
            return
        clue, word = pick_random_word()
        active_explain_games[chat_id] = {
            "word": word,
            "starter": user_id,
            "clue": clue,
            "guessed": False,
            "lead_dropped": False,
        }
        # DM the word to the starter
        try:
            await context.bot.send_message(
                user_id,
                f"🤫 <b>Your word to explain:</b> <code>{word.upper()}</code>\n"
                f"Don't say the word! Explain it in the group so others can guess.\n"
                f"Use the buttons below in group to get a new word or drop the lead.",
                parse_mode="HTML"
            )
        except Exception as dm_err:
            await update.message.reply_text("⚠️ <b>Couldn't DM you the word. Please start a private chat with me first!</b>", parse_mode="HTML")
            active_explain_games.pop(chat_id, None)
            logging.error(f"Error DMing starter in explainword_start: {dm_err}")
            return
        # Inline keyboard for actions
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Change Word", callback_data="explain_changeword"),
                InlineKeyboardButton("🪂 Drop Lead", callback_data="explain_droplead"),
            ]
        ])
        await update.message.reply_text(
            f"🎲 <b>Explain & Guess Game Started!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>{update.effective_user.mention_html()}</b> is the explainer (lead).\n"
            f"❓ <b>Clue:</b> <i>{clue}</i>\n"
            f"Everyone else: Guess the word in chat!\n"
            f"<i>(The explainer can't say the word directly!)</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Explainer: Use the buttons below to get a new word or drop the lead.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Error in explainword_start: {e}")
        try:
            await update.message.reply_text(
                "❌ <b>Failed to start the explain & guess game.</b>\n"
                f"<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception as ex:
            logging.error(f"Error sending error message in explainword_start: {ex}")

# Inline button callback handler for explain & guess game
async def explainword_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    game = active_explain_games.get(chat_id)
    if not game or game.get("guessed"):
        await query.answer("No active explain & guess game.", show_alert=True)
        return

    if query.data == "explain_changeword":
        if game["starter"] != user_id:
            await query.answer("Only the current explainer can change the word.", show_alert=True)
            return
        clue, word = pick_random_word()
        game["word"] = word
        game["clue"] = clue
        try:
            await context.bot.send_message(
                user_id,
                f"🤫 <b>Your new word to explain:</b> <code>{word.upper()}</code>\n"
                f"Don't say the word! Explain it in the group so others can guess.",
                parse_mode="HTML"
            )
            await query.edit_message_text(
                f"🔄 <b>Word changed!</b>\n❓ <b>Clue:</b> <i>{clue}</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔄 Change Word", callback_data="explain_changeword"),
                        InlineKeyboardButton("🪂 Drop Lead", callback_data="explain_droplead"),
                    ]
                ])
            )
        except Exception as e:
            await query.answer("Couldn't DM you the word. Please start a private chat with me first!", show_alert=True)
            logging.error(f"changeword DM error: {e}")

    elif query.data == "explain_droplead":
        if game["starter"] != user_id:
            await query.answer("Only the current explainer can drop the lead.", show_alert=True)
            return
        game["lead_dropped"] = True
        await query.edit_message_text(
            "🪂 <b>The explainer has dropped the lead!</b>\n"
            "Anyone can now take the lead with the button below.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎉 Take Lead", callback_data="explain_takelead")]
            ])
        )
        await query.answer("Lead dropped. Anyone can now take the lead.", show_alert=False)

    elif query.data == "explain_takelead":
        if not game.get("lead_dropped"):
            await query.answer("The lead has not been dropped yet.", show_alert=True)
            return
        clue, word = pick_random_word()
        game["word"] = word
        game["clue"] = clue
        game["starter"] = user_id
        game["lead_dropped"] = False
        try:
            await context.bot.send_message(
                user_id,
                f"🤫 <b>Your word to explain:</b> <code>{word.upper()}</code>\n"
                f"Don't say the word! Explain it in the group so others can guess.",
                parse_mode="HTML"
            )
            await query.edit_message_text(
                f"🎉 <b>{query.from_user.mention_html()} is now the explainer!</b>\n"
                f"❓ <b>Clue:</b> <i>{clue}</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔄 Change Word", callback_data="explain_changeword"),
                        InlineKeyboardButton("🪂 Drop Lead", callback_data="explain_droplead"),
                    ]
                ])
            )
            await query.answer("You are now the explainer!", show_alert=False)
        except Exception as e:
            await query.answer("Couldn't DM you the word. Please start a private chat with me first!", show_alert=True)
            logging.error(f"takelead DM error: {e}")

async def explainword_guess(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        if chat_id not in active_explain_games:
            return
        game = active_explain_games[chat_id]
        word = game["word"]
        starter = game["starter"]
        if user_id == starter:
            # Starter can't guess
            return
        guess = update.message.text.strip().lower()
        if not guess.isalpha() or len(guess) < 2:
            return
        # Cheating: explainer says the word
        if starter and guess == word.lower() and update.effective_user.id == starter:
            # Should not happen, but just in case
            await update.message.reply_text("❌ <b>You can't guess your own word!</b>", parse_mode="HTML")
            return
        # Cheating: explainer says the word in chat
        if update.effective_user.id == starter and word.lower() in guess:
            clue, new_word = pick_random_word()
            game["word"] = new_word
            game["clue"] = clue
            try:
                await context.bot.send_message(
                    starter,
                    f"🚫 <b>You said the word! New word assigned:</b> <code>{new_word.upper()}</code>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            # Edit the game message if possible
            try:
                # Find the last game message (if any)
                # This is a best effort; you may want to store message_id in game state for reliability
                pass
            except Exception:
                pass
            await update.message.reply_text(
                "🚫 <b>No cheating! You said the word directly. New word assigned.</b>",
                parse_mode="HTML"
            )
            return
        # Correct guess
        if guess == word.lower():
            game["guessed"] = True
            # Points: +1 for guesser, +1 for explainer
            explain_leaderboard[chat_id][user_id] += 1
            explain_leaderboard[chat_id][starter] += 1
            try:
                starter_member = await context.bot.get_chat_member(chat_id, starter)
                starter_mention = starter_member.user.mention_html()
            except Exception:
                starter_mention = "the explainer"
            await update.message.reply_text(
                f"🏆 <b>Correct!</b>\n"
                f"<b>{update.effective_user.mention_html()}</b> guessed the word <code>{word.upper()}</code>!\n"
                f"👏 <b>{starter_mention}</b> explained it well!\n"
                f"Both get +1 point.",
                parse_mode="HTML"
            )
            active_explain_games.pop(chat_id, None)
        elif word.lower() in guess:
            # Prevent cheating: don't allow the word in the explanation
            if update.effective_user.id == starter:
                clue, new_word = pick_random_word()
                game["word"] = new_word
                game["clue"] = clue
                try:
                    await context.bot.send_message(
                        starter,
                        f"🚫 <b>You said the word! New word assigned:</b> <code>{new_word.upper()}</code>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                await update.message.reply_text(
                    "🚫 <b>No cheating! You said the word directly. New word assigned.</b>",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    "🚫 <b>No cheating! Don't say the word directly.</b>",
                    parse_mode="HTML"
                )
    except Exception as e:
        logging.error(f"Error in explainword_guess: {e}")
        try:
            await update.message.reply_text(
                "❌ <b>Error processing your guess.</b>\n"
                f"<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception as ex:
            logging.error(f"Error sending error message in explainword_guess: {ex}")

async def explainword_cancel(update, context):
    try:
        chat_id = update.effective_chat.id
        if chat_id in active_explain_games:
            active_explain_games.pop(chat_id, None)
            await update.message.reply_text(
                "❌ <b>Explain & guess game cancelled.</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("No active explain & guess game to cancel.")
    except Exception as e:
        logging.error(f"Error in explainword_cancel: {e}")
        try:
            await update.message.reply_text("❌ Could not cancel the game due to an error.\n"
                                            f"<code>{html.escape(str(e))}</code>", parse_mode="HTML")
        except Exception as ex:
            logging.error(f"Error sending error message in explainword_cancel: {ex}")

async def explain_leaderboard_command(update, context):
    chat_id = update.effective_chat.id
    board = explain_leaderboard[chat_id]
    if not board:
        await update.message.reply_text(
            "<b>🏅 Explain & Guess Leaderboard</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "No points yet! Play the explain & guess game to earn points.",
            parse_mode="HTML"
        )
        return

        sorted_board = sorted(board.items(), key=lambda x: x[1], reverse=True)
        text = (
            "<b>🏅 Explain & Guess Leaderboard</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Top players in this group:</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        for idx, (uid, pts) in enumerate(sorted_board, 1):
            try:
                user = await context.bot.get_chat(uid)
                mention = user.mention_html()
            except Exception:
                mention = f"<code>{uid}</code>"
            text += f"<b>{idx}.</b> {mention} — <b>{pts}</b> point{'s' if pts != 1 else ''}\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "<i>Keep playing and explaining to climb the leaderboard!</i>"
        await update.message.reply_text(text, parse_mode="HTML")

        # --- Word List for Explain & Guess Game (5000 common English words) ---
        # This list is generated from a public domain word list (e.g. SCOWL, 5000 most common English words)
WORD_LIST = [
            "ability", "able", "about", "above", "accept", "according", "account", "across", "act", "action",
            "activity", "actually", "add", "address", "administration", "admit", "adult", "affect", "after", "again",
            "against", "age", "agency", "agent", "ago", "agree", "agreement", "ahead", "air", "all",
            "allow", "almost", "alone", "along", "already", "also", "although", "always", "American", "among",
            "amount", "analysis", "and", "animal", "another", "answer", "any", "anyone", "anything", "appear",
            "apply", "approach", "area", "argue", "arm", "around", "arrive", "art", "article", "artist",
            "as", "ask", "assume", "at", "attack", "attention", "attorney", "audience", "author", "authority",
            "available", "avoid", "away", "baby", "back", "bad", "bag", "ball", "bank", "bar",
            "base", "be", "beat", "beautiful", "because", "become", "bed", "before", "begin", "behavior",
            "behind", "believe", "benefit", "best", "better", "between", "beyond", "big", "bill", "billion",
            "bit", "black", "blood", "blue", "board", "body", "book", "born", "both", "box",
            "boy", "break", "bring", "brother", "budget", "build", "building", "business", "but", "buy",
            "by", "call", "camera", "campaign", "can", "cancer", "candidate", "capital", "car", "card",
            "care", "career", "carry", "case", "catch", "cause", "cell", "center", "central", "century",
            "certain", "certainly", "chair", "challenge", "chance", "change", "character", "charge", "check", "child",
            "choice", "choose", "church", "citizen", "city", "civil", "claim", "class", "clear", "clearly",
            "close", "coach", "cold", "collection", "college", "color", "come", "commercial", "common", "community",
            "company", "compare", "computer", "concern", "condition", "conference", "Congress", "consider", "consumer", "contain",
            "continue", "control", "cost", "could", "country", "couple", "course", "court", "cover", "create",
            "crime", "cultural", "culture", "cup", "current", "customer", "cut", "dark", "data", "daughter",
            "day", "dead", "deal", "death", "debate", "decade", "decide", "decision", "deep", "defense",
            "degree", "democrat", "democratic", "describe", "design", "despite", "detail", "determine", "develop", "development",
            "die", "difference", "different", "difficult", "dinner", "direction", "director", "discover", "discuss", "discussion",
            "disease", "do", "doctor", "dog", "door", "down", "draw", "dream", "drive", "drop",
            "drug", "during", "each", "early", "east", "easy", "eat", "economic", "economy", "edge",
            "education", "effect", "effort", "eight", "either", "election", "else", "employee", "end", "energy",
            "enjoy", "enough", "enter", "entire", "environment", "environmental", "especially", "establish", "even", "evening",
            "event", "ever", "every", "everybody", "everyone", "everything", "evidence", "exactly", "example", "executive",
            "exist", "expect", "experience", "expert", "explain", "eye", "face", "fact", "factor", "fail",
            "fall", "family", "far", "fast", "father", "fear", "federal", "feel", "feeling", "few",
            "field", "fight", "figure", "fill", "film", "final", "finally", "financial", "find", "fine",
            "finger", "finish", "fire", "firm", "first", "fish", "five", "floor", "fly", "focus",
            "follow", "food", "foot", "for", "force", "foreign", "forget", "form", "former", "forward",
            "four", "free", "friend", "from", "front", "full", "fund", "future", "game", "garden",
            "gas", "general", "generation", "get", "girl", "give", "glass", "go", "goal", "good",
            "government", "great", "green", "ground", "group", "grow", "growth", "guess", "gun", "guy",
            "hair", "half", "hand", "hang", "happen", "happy", "hard", "have", "he", "head",
            "health", "hear", "heart", "heat", "heavy", "help", "her", "here", "herself", "high",
            "him", "himself", "his", "history", "hit", "hold", "home", "hope", "hospital", "hot",
            "hotel", "hour", "house", "how", "however", "huge", "human", "hundred", "husband", "I",
            "idea", "identify", "if", "image", "imagine", "impact", "important", "improve", "in", "include",
            "including", "increase", "indeed", "indicate", "individual", "industry", "information", "inside", "instead", "institution",
            "interest", "interesting", "international", "interview", "into", "investment", "involve", "issue", "it", "item",
            "its", "itself", "job", "join", "just", "keep", "key", "kid", "kill", "kind",
            "kitchen", "know", "knowledge", "land", "language", "large", "last", "late", "later", "laugh",
            "law", "lawyer", "lay", "lead", "leader", "learn", "least", "leave", "left", "leg",
            "legal", "less", "let", "letter", "level", "lie", "life", "light", "like", "likely",
            "line", "list", "listen", "little", "live", "local", "long", "look", "lose", "loss",
            "lot", "love", "low", "machine", "magazine", "main", "maintain", "major", "majority", "make",
            "man", "manage", "management", "manager", "many", "market", "marriage", "material", "matter", "may",
            "maybe", "me", "mean", "measure", "media", "medical", "meet", "meeting", "member", "memory",
            "mention", "message", "method", "middle", "might", "military", "million", "mind", "minute", "miss",
            "mission", "model", "modern", "moment", "money", "month", "more", "morning", "most", "mother",
            "mouth", "move", "movement", "movie", "Mr", "Mrs", "much", "music", "must", "my",
            "myself", "name", "nation", "national", "natural", "nature", "near", "nearly", "necessary", "need",
            "network", "never", "new", "news", "newspaper", "next", "nice", "night", "no", "none",
            "nor", "north", "not", "note", "nothing", "notice", "now", "number", "occur", "of",
            "off", "offer", "office", "officer", "official", "often", "oh", "oil", "ok", "old",
            "on", "once", "one", "only", "onto", "open", "operation", "opportunity", "option", "or",
            "order", "organization", "other", "others", "our", "out", "outside", "over", "own", "owner",
            "page", "pain", "painting", "paper", "parent", "part", "participant", "particular", "particularly", "partner",
            "party", "pass", "past", "patient", "pattern", "pay", "peace", "people", "per", "perform",
            "performance", "perhaps", "period", "person", "personal", "phone", "physical", "pick", "picture", "piece",
            "place", "plan", "plant", "play", "player", "PM", "point", "police", "policy", "political",
            "politics", "poor", "popular", "population", "position", "positive", "possible", "power", "practice", "prepare",
            "present", "president", "pressure", "pretty", "prevent", "price", "private", "probably", "problem", "process",
            "produce", "product", "production", "professional", "professor", "program", "project", "property", "protect", "prove",
            "provide", "public", "pull", "purpose", "push", "put", "quality", "question", "quickly", "quite",
            "race", "radio", "raise", "range", "rate", "rather", "reach", "read", "ready", "real",
            "reality", "realize", "really", "reason", "receive", "recent", "recently", "recognize", "record", "red",
            "reduce", "reflect", "region", "relate", "relationship", "religious", "remain", "remember", "remove", "report",
            "represent", "Republican", "require", "research", "resource", "respond", "response", "responsibility", "rest", "result",
            "return", "reveal", "rich", "right", "rise", "risk", "road", "rock", "role", "room",
            "rule", "run", "safe", "same", "save", "say", "scene", "school", "science", "scientist",
            "score", "sea", "season", "seat", "second", "section", "security", "see", "seek", "seem",
            "sell", "send", "senior", "sense", "series", "serious", "serve", "service", "set", "seven",
            "several", "sex", "sexual", "shake", "share", "she", "shoot", "short", "shot", "should",
            "shoulder", "show", "side", "sign", "significant", "similar", "simple", "simply", "since", "sing",
            "single", "sister", "sit", "site", "situation", "six", "size", "skill", "skin", "small",
            "smile", "so", "social", "society", "soldier", "some", "somebody", "someone", "something", "sometimes",
            "son", "song", "soon", "sort", "sound", "source", "south", "southern", "space", "speak",
            "special", "specific", "speech", "spend", "sport", "spring", "staff", "stage", "stand", "standard",
            "star", "start", "state", "statement", "station", "stay", "step", "still", "stock", "stop",
            "store", "story", "strategy", "street", "strong", "structure", "student", "study", "stuff", "style",
            "subject", "success", "successful", "such", "suddenly", "suffer", "suggest", "summer", "support", "sure",
            "surface", "system", "table", "take", "talk", "task", "tax", "teach", "teacher", "team",
            "technology", "television", "tell", "ten", "tend", "term", "test", "than", "thank", "that",
            "the", "their", "them", "themselves", "then", "theory", "there", "these", "they", "thing",
            "think", "third", "this", "those", "though", "thought", "thousand", "threat", "three", "through",
            "throughout", "throw", "thus", "time", "to", "today", "together", "tonight", "too", "top",
            "total", "tough", "toward", "town", "trade", "traditional", "training", "travel", "treat", "treatment",
            "tree", "trial", "trip", "trouble", "true", "truth", "try", "turn", "TV", "two",
            "type", "under", "understand", "unit", "until", "up", "upon", "us", "use", "usually",
            "value", "various", "very", "victim", "view", "violence", "visit", "voice", "vote", "wait",
            "walk", "wall", "want", "war", "watch", "water", "way", "we", "weapon", "wear",
            "week", "weight", "well", "west", "western", "what", "whatever", "when", "where", "whether",
            "which", "while", "white", "who", "whole", "whom", "whose", "why", "wide", "wife",
            "will", "win", "wind", "window", "wish", "with", "within", "without", "woman", "wonder",
            "word", "work", "worker", "world", "worry", "would", "write", "writer", "wrong", "yard",
            "yeah", "year", "yes", "yet", "you", "young", "your", "yourself",
            # The above is the top 1000. To reach 5000, you can use a public domain word list.
            # For brevity, the rest are omitted, but in your actual code, you should paste the full 5000-word list here.
            # Example: Download from https://github.com/first20hours/google-10000-english/blob/master/20k.txt
            # and use the first 5000 lines, or use SCOWL's 5000 common words.
        ]

            # --- Blocklists Module (with Error Handling & Pattern Matching) ---


# --- Blocklists Module (with Error Handling & Pattern Matching) ---


MAX_WARNS = 3  # Set your max warns value here
warns = defaultdict(lambda: defaultdict(int))  # {chat_id: {user_id: warn_count}}

blocklists = defaultdict(lambda: {
    "triggers": {},  # trigger: reason
    "mode": ("warn", None),  # ("action", duration)
    "delete": True,
    "reason": "Blocked word/phrase.",
})

def blocklist_pattern_to_regex(trigger):
    # Escape regex special chars except * and ?
    trigger = re.escape(trigger)
    # Replace escaped wildcards with regex equivalents
    trigger = trigger.replace(r'\*\*', r'[\s\S]*')  # ** = any char (including spaces)
    trigger = trigger.replace(r'\*', r'\S*')        # * = any non-whitespace chars
    trigger = trigger.replace(r'\?', r'\S')         # ? = any single non-whitespace char
    # Match as word boundary or anywhere
    return re.compile(trigger, re.IGNORECASE)

def get_blocklist(chat_id):
    return blocklists[chat_id]

async def addblocklist(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        # Support multi-line triggers (one per line)
        text = update.message.text.partition(" ")[2].strip()
        if not text:
            await update.message.reply_text("❓ <b>Usage:</b> /addblocklist <trigger> [reason] or multiple triggers (one per line)", parse_mode="HTML")
            return
        triggers = [line.strip() for line in text.split("\n") if line.strip()]
        bl = get_blocklist(chat_id)
        added = []
        for line in triggers:
            # Allow: trigger [reason...]
            parts = line.split(" ", 1)
            trigger = parts[0]
            reason = parts[1] if len(parts) > 1 else ""
            bl["triggers"][trigger] = reason
            added.append(trigger)
        if len(added) == 1:
            await update.message.reply_text(
                f"✅ <b>Blocklist trigger added:</b> <code>{html.escape(added[0])}</code>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"✅ <b>{len(added)} blocklist triggers added.</b>",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"addblocklist error: {e}")
        await update.message.reply_text(f"❌ Error adding blocklist trigger.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def rmblocklist(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        text = update.message.text.partition(" ")[2].strip()
        if not text:
            await update.message.reply_text("❓ <b>Usage:</b> /rmblocklist <trigger> or multiple triggers (one per line)", parse_mode="HTML")
            return
        triggers = [line.strip() for line in text.split("\n") if line.strip()]
        bl = get_blocklist(chat_id)
        removed = []
        for trigger in triggers:
            if trigger in bl["triggers"]:
                bl["triggers"].pop(trigger)
                removed.append(trigger)
        if len(removed) == 1:
            await update.message.reply_text(
                f"✅ <b>Blocklist trigger removed:</b> <code>{html.escape(removed[0])}</code>",
                parse_mode="HTML"
            )
        elif removed:
            await update.message.reply_text(
                f"✅ <b>{len(removed)} blocklist triggers removed.</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ <b>No matching triggers found in blocklist.</b>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"rmblocklist error: {e}")
        await update.message.reply_text(f"❌ Error removing blocklist trigger.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def unblocklistall(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if getattr(member, "status", "") != "creator":
            await update.message.reply_text("👑 <b>Only the group creator can use this command!</b>", parse_mode="HTML")
            return
        bl = get_blocklist(chat_id)
        bl["triggers"].clear()
        await update.message.reply_text(
            "✅ <b>All blocklist triggers removed.</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"unblocklistall error: {e}")
        await update.message.reply_text(f"❌ Error clearing blocklist.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def blocklist(update, context):
    try:
        chat_id = update.effective_chat.id
        bl = get_blocklist(chat_id)
        if not bl["triggers"]:
            await update.message.reply_text("ℹ️ <b>No blocklist triggers set in this chat.</b>", parse_mode="HTML")
            return
        text = "<b>🚫 Blocklist triggers:</b>\n"
        for trig, reason in bl["triggers"].items():
            text += f"• <code>{html.escape(trig)}</code>"
            if reason:
                text += f" — <i>{html.escape(reason)}</i>"
            text += "\n"
        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"blocklist error: {e}")
        await update.message.reply_text(f"❌ Error listing blocklist triggers.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def blocklistmode(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            bl = get_blocklist(chat_id)
            mode, duration = bl["mode"]
            await update.message.reply_text(
                f"ℹ️ <b>Current blocklist mode:</b> <code>{mode}{' ' + duration if duration else ''}</code>",
                parse_mode="HTML"
            )
            return
        mode = context.args[0].lower()
        duration = context.args[1] if len(context.args) > 1 else None
        valid_modes = ("nothing", "ban", "mute", "kick", "warn", "tban", "tmute")
        if mode not in valid_modes:
            await update.message.reply_text(
                "❓ <b>Usage:</b> /blocklistmode <nothing/ban/mute/kick/warn/tban/tmute> [duration]",
                parse_mode="HTML"
            )
            return
        bl = get_blocklist(chat_id)
        if mode in ("tban", "tmute"):
            if not duration:
                await update.message.reply_text("⏳ <b>Please specify a duration for tban/tmute (e.g. 10m, 2h).</b>", parse_mode="HTML")
                return
            bl["mode"] = (mode, duration)
        else:
            bl["mode"] = (mode, None)
        await update.message.reply_text(
            f"✅ <b>Blocklist mode set to:</b> <code>{mode}{' ' + duration if duration else ''}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"blocklistmode error: {e}")
        await update.message.reply_text(f"❌ Error setting blocklist mode.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def blocklistdelete(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            bl = get_blocklist(chat_id)
            await update.message.reply_text(
                f"ℹ️ <b>Blocklist delete is currently {'<u>ON</u>' if bl['delete'] else '<u>OFF</u>'}.</b>",
                parse_mode="HTML"
            )
            return
        arg = context.args[0].lower()
        bl = get_blocklist(chat_id)
        if arg in ("yes", "on", "true", "enable"):
            bl["delete"] = True
            await update.message.reply_text(
                "✅ <b>Blocklisted messages will be deleted.</b>",
                parse_mode="HTML"
            )
        elif arg in ("no", "off", "false", "disable"):
            bl["delete"] = False
            await update.message.reply_text(
                "❌ <b>Blocklisted messages will NOT be deleted.</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❓ <b>Usage:</b> /blocklistdelete <yes/no/on/off>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"blocklistdelete error: {e}")
        await update.message.reply_text(f"❌ Error setting blocklist delete.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def setblocklistreason(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            await update.message.reply_text("❓ <b>Usage:</b> /setblocklistreason <reason>", parse_mode="HTML")
            return
        reason = " ".join(context.args)
        bl = get_blocklist(chat_id)
        bl["reason"] = reason
        await update.message.reply_text(
            f"✅ <b>Blocklist reason set to:</b> <i>{html.escape(reason)}</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"setblocklistreason error: {e}")
        await update.message.reply_text(f"❌ Error setting blocklist reason.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def resetblocklistreason(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        bl = get_blocklist(chat_id)
        bl["reason"] = "Blocked word/phrase."
        await update.message.reply_text(
            "✅ <b>Blocklist reason reset to default.</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"resetblocklistreason error: {e}")
        await update.message.reply_text(f"❌ Error resetting blocklist reason.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def blocklist_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or update.message.chat.type == "private":
            return
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        text = update.message.text or ""
        bl = get_blocklist(chat_id)
        if not bl["triggers"]:
            return
        # Compile all triggers to regex
        for trigger, reason in bl["triggers"].items():
            try:
                regex = blocklist_pattern_to_regex(trigger)
                if regex.search(text):
                    # Blocklist matched!
                    action, duration = bl["mode"]
                    # Delete message if enabled
                    if bl["delete"]:
                        try:
                            await update.message.delete()
                        except Exception as e:
                            logging.error(f"Failed to delete blocklisted message: {e}")
                    # Take action
                    msg_reason = reason or bl["reason"]
                    if action == "nothing":
                        # Only delete (if enabled)
                        return
                    elif action == "ban":
                        await context.bot.ban_chat_member(chat_id, user_id)
                        await context.bot.send_message(
                            chat_id,
                            f"🔨 <b>User banned for blocklisted word:</b> <code>{html.escape(trigger)}</code>\n"
                            f"📝 <b>Reason:</b> <i>{html.escape(msg_reason)}</i>",
                            parse_mode="HTML"
                        )
                    elif action == "kick":
                        await context.bot.ban_chat_member(chat_id, user_id)
                        await context.bot.unban_chat_member(chat_id, user_id)
                        await context.bot.send_message(
                            chat_id,
                            f"🥾 <b>User kicked for blocklisted word:</b> <code>{html.escape(trigger)}</code>\n"
                            f"📝 <b>Reason:</b> <i>{html.escape(msg_reason)}</i>",
                            parse_mode="HTML"
                        )
                    elif action == "mute":
                        until_date = datetime.now() + timedelta(days=365*10)
                        await context.bot.restrict_chat_member(
                            chat_id, user_id, permissions=ChatPermissions(can_send_messages=False), until_date=until_date
                        )
                        await context.bot.send_message(
                            chat_id,
                            f"🔇 <b>User muted for blocklisted word:</b> <code>{html.escape(trigger)}</code>\n"
                            f"📝 <b>Reason:</b> <i>{html.escape(msg_reason)}</i>",
                            parse_mode="HTML"
                        )
                    elif action == "warn":
                        warns[chat_id][user_id] += 1
                        count = warns[chat_id][user_id]
                        warn_bar = "🟩" * count + "⬜" * (MAX_WARNS - count)
                        await context.bot.send_message(
                            chat_id,
                            f"⚠️ <b>User warned for blocklisted word:</b> <code>{html.escape(trigger)}</code>\n"
                            f"{warn_bar}\n"
                            f"📝 <b>Reason:</b> <i>{html.escape(msg_reason)}</i>",
                            parse_mode="HTML"
                        )
                        if count >= MAX_WARNS:
                            await context.bot.ban_chat_member(chat_id, user_id)
                            warns[chat_id][user_id] = 0
                            await context.bot.send_message(
                                chat_id,
                                f"🔨 <b>User banned after max warns (blocklist).</b>",
                                parse_mode="HTML"
                            )
                    elif action == "tban" and duration:
                        seconds = parse_duration(duration)
                        if seconds:
                            until_date = datetime.now() + timedelta(seconds=seconds)
                            await context.bot.ban_chat_member(chat_id, user_id, until_date=until_date)
                            await context.bot.send_message(
                                chat_id,
                                f"⏳🔨 <b>User tempbanned for blocklisted word:</b> <code>{html.escape(trigger)}</code>\n"
                                f"📝 <b>Reason:</b> <i>{html.escape(msg_reason)}</i>",
                                parse_mode="HTML"
                            )
                    elif action == "tmute" and duration:
                        seconds = parse_duration(duration)
                        if seconds:
                            until_date = datetime.now() + timedelta(seconds=seconds)
                            await context.bot.restrict_chat_member(
                                chat_id, user_id, permissions=ChatPermissions(can_send_messages=False), until_date=until_date
                            )
                            await context.bot.send_message(
                                chat_id,
                                f"⏳🔇 <b>User tempmuted for blocklisted word:</b> <code>{html.escape(trigger)}</code>\n"
                                f"📝 <b>Reason:</b> <i>{html.escape(msg_reason)}</i>",
                                parse_mode="HTML"
                            )
                    break  # Only trigger once per message
            except Exception as e:
                logging.error(f"blocklist regex error for trigger '{trigger}': {e}")
    except Exception as e:
        logging.error(f"blocklist_message_handler error: {e}")




        # --- Locks Module (with Error Handling & Allowlist) ---

# --- Locks Module (with Error Handling & Allowlist) ---


LOCK_TYPES = {
    "audio": filters.AUDIO,
    "voice": filters.VOICE,
    "document": filters.Document.ALL,
    "video": filters.VIDEO,
    "contact": filters.CONTACT,
    "photo": filters.PHOTO,
    "url": filters.Entity(MessageEntity.URL) | filters.CaptionEntity(MessageEntity.URL),
    "bots": filters.StatusUpdate.NEW_CHAT_MEMBERS,
    "forward": filters.FORWARDED,
    "game": filters.GAME,
    "location": filters.LOCATION,
    "egame": filters.Dice.ALL,
    "rtl": "rtl",
    "button": "button",
    "inline": "inline",
    "phone": filters.Entity(MessageEntity.PHONE_NUMBER) | filters.CaptionEntity(MessageEntity.PHONE_NUMBER),
    "command": filters.COMMAND,
    "email": filters.Entity(MessageEntity.EMAIL) | filters.CaptionEntity(MessageEntity.EMAIL),
    "anonchannel": "anonchannel",
    "forwardchannel": "forwardchannel",
    "forwardbot": "forwardbot",
    # "invitelink": ,
    "videonote": filters.VIDEO_NOTE,
    "emojicustom": filters.Entity(MessageEntity.CUSTOM_EMOJI) | filters.CaptionEntity(MessageEntity.CUSTOM_EMOJI),
    "stickerpremium": filters.Sticker.PREMIUM,
    "stickeranimated": filters.Sticker.ANIMATED,
}

lockable_types = list(LOCK_TYPES.keys())

locks = defaultdict(lambda: set())
lockwarns_enabled = defaultdict(lambda: True)
allowlists = defaultdict(lambda: set())

def normalize_lock_type(item):
    item = item.lower()
    aliases = {
        "stickers": "sticker",
        "sticker": "sticker",
        "photos": "photo",
        "photo": "photo",
        "pic": "photo",
        "pics": "photo",
        "picture": "photo",
        "pictures": "photo",
        "videos": "video",
        "video": "video",
        "audios": "audio",
        "audio": "audio",
        "music": "audio",
        "voices": "voice",
        "voice": "voice",
        "voicemessage": "voice",
        "documents": "document",
        "document": "document",
        "doc": "document",
        "docs": "document",
        "contacts": "contact",
        "contact": "contact",
        "locations": "location",
        "location": "location",
        "urls": "url",
        "url": "url",
        "links": "url",
        "link": "url",
        "forwards": "forward",
        "forward": "forward",
        "invitelink": "invitelink",
        "invitelinks": "invitelink",
        "invite": "invitelink",
        "invite_link": "invitelink",
        "inline": "inline",
        "inlinebot": "inline",
        "inlinebots": "inline",
        "command": "command",
        "commands": "command",
        "externalreply": "externalreply",
        "externalreplies": "externalreply",
        "anonchannel": "anonchannel",
        "anonymouschannel": "anonchannel",
        "anonchannels": "anonchannel",
        "forwardchannel": "forwardchannel",
        "forwardbot": "forwardbot",
        "videonote": "videonote",
        "emojicustom": "emojicustom",
        "stickerpremium": "stickerpremium",
        "stickeranimated": "stickeranimated",
        "game": "game",
        "egame": "egame",
        "button": "button",
        "phone": "phone",
        "email": "email",
        "bots": "bots",
        "rtl": "rtl",
    }
    return aliases.get(item, item)

async def lock_command(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            await update.message.reply_text("❓ <b>Usage:</b> /lock <item(s)>", parse_mode="HTML")
            return
        locked = []
        for item in context.args:
            typ = normalize_lock_type(item)
            if typ in lockable_types:
                locks[chat_id].add(typ)
                locked.append(typ)
        if locked:
            await update.message.reply_animation(
                animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                caption=f"🔒 <b>Locked:</b> <code>{', '.join(locked)}</code>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ <b>No valid lockable items specified.</b>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"lock_command error: {e}")
        await update.message.reply_text(f"❌ Error locking items.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def unlock_command(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            await update.message.reply_text("❓ <b>Usage:</b> /unlock <item(s)>", parse_mode="HTML")
            return
        unlocked = []
        for item in context.args:
            typ = normalize_lock_type(item)
            if typ in locks[chat_id]:
                locks[chat_id].discard(typ)
                unlocked.append(typ)
        if unlocked:
            await update.message.reply_animation(
                animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                caption=f"🔓 <b>Unlocked:</b> <code>{', '.join(unlocked)}</code>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ <b>No locked items specified or already unlocked.</b>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"unlock_command error: {e}")
        await update.message.reply_text(f"❌ Error unlocking items.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def locks_command(update, context):
    try:
        chat_id = update.effective_chat.id
        current = sorted(list(locks[chat_id]))
        if not current:
            await update.message.reply_text("🔓 <b>No items are currently locked in this chat.</b>", parse_mode="HTML")
            return
        await update.message.reply_text(
            f"🔒 <b>Locked items:</b> <code>{', '.join(current)}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"locks_command error: {e}")
        await update.message.reply_text(f"❌ Error listing locks.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def lockwarns_command(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            status = "ON" if lockwarns_enabled[chat_id] else "OFF"
            await update.message.reply_text(
                f"⚠️ <b>Lockwarns are currently <u>{status}</u>.</b>\nUse <code>/lockwarns yes</code> or <code>/lockwarns no</code>.",
                parse_mode="HTML"
            )
            return
        arg = context.args[0].lower()
        if arg in ("yes", "on", "true", "enable"):
            lockwarns_enabled[chat_id] = True
            await update.message.reply_animation(
                animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                caption="✅ <b>Lockwarns enabled.</b>",
                parse_mode="HTML"
            )
        elif arg in ("no", "off", "false", "disable"):
            lockwarns_enabled[chat_id] = False
            await update.message.reply_animation(
                animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                caption="❌ <b>Lockwarns disabled.</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❓ <b>Usage:</b> /lockwarns <yes/no/on/off>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"lockwarns_command error: {e}")
        await update.message.reply_text(f"❌ Error setting lockwarns.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def locktypes_command(update, context):
    try:
        await update.message.reply_text(
            "<b>Lockable items:</b>\n" +
            ", ".join(lockable_types),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"locktypes_command error: {e}")
        await update.message.reply_text(f"❌ Error listing lock types.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def allowlist_command(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            items = sorted(list(allowlists[chat_id]))
            if not items:
                await update.message.reply_text("ℹ️ <b>No allowlisted items in this chat.</b>", parse_mode="HTML")
                return
            await update.message.reply_text(
                "<b>Allowlisted items:</b>\n" + "\n".join(f"<code>{html.escape(x)}</code>" for x in items),
                parse_mode="HTML"
            )
            return
        added = []
        for item in context.args:
            allowlists[chat_id].add(item)
            added.append(item)
        await update.message.reply_animation(
            animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
            caption=f"✅ <b>Allowlisted:</b> <code>{', '.join(added)}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"allowlist_command error: {e}")
        await update.message.reply_text(f"❌ Error updating allowlist.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def rmallowlist_command(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(member):
            await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
            return
        if not context.args:
            await update.message.reply_text("❓ <b>Usage:</b> /rmallowlist <item(s)>", parse_mode="HTML")
            return
        removed = []
        for item in context.args:
            if item in allowlists[chat_id]:
                allowlists[chat_id].remove(item)
                removed.append(item)
        if removed:
            await update.message.reply_animation(
                animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                caption=f"✅ <b>Removed from allowlist:</b> <code>{', '.join(removed)}</code>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ <b>No matching allowlist items found.</b>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"rmallowlist_command error: {e}")
        await update.message.reply_text(f"❌ Error removing allowlist items.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def rmallowlistall_command(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if getattr(member, "status", "") != "creator":
            await update.message.reply_text("👑 <b>Only the group creator can use this command!</b>", parse_mode="HTML")
            return
        allowlists[chat_id].clear()
        await update.message.reply_animation(
            animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
            caption="✅ <b>All allowlist items removed.</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"rmallowlistall_command error: {e}")
        await update.message.reply_text(f"❌ Error clearing allowlist.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

def is_allowlisted(chat_id, update):
    items = allowlists[chat_id]
    if not items:
        return False
    text = (update.message.text or "") if update.message else ""
    for item in items:
        if item.startswith("@"):
            if item.lower() in text.lower():
                return True
            if update.message and update.message.forward_from_chat:
                if update.message.forward_from_chat.username and ("@" + update.message.forward_from_chat.username.lower() == item.lower()):
                    return True
        elif item.startswith("/"):
            if text.startswith(item):
                return True
        elif item in text:
            return True
        if update.message and update.message.sticker and update.message.sticker.set_name:
            if item.lower() in update.message.sticker.set_name.lower():
                return True
    return False

async def locks_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or update.message.chat.type == "private":
            return
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        if is_admin(member):
            return
        if is_allowlisted(chat_id, update):
            return
        locked = locks[chat_id]
        if "sticker" in locked and update.message.sticker:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Stickers are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "photo" in locked and update.message.photo:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Photos are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "video" in locked and update.message.video:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Videos are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "audio" in locked and update.message.audio:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Audios are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "voice" in locked and update.message.voice:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Voice messages are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "document" in locked and update.message.document:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Documents are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "contact" in locked and update.message.contact:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Contacts are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "location" in locked and update.message.location:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Locations are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "url" in locked:
            entities = update.message.entities or []
            for ent in entities:
                if ent.type in ("url", "text_link"):
                    await update.message.delete()
                    if lockwarns_enabled[chat_id]:
                        warns[chat_id][user_id] += 1
                        await context.bot.send_message(
                            chat_id,
                            f"⚠️ <b>Links are locked!</b> {update.effective_user.mention_html()} warned.",
                            parse_mode="HTML"
                        )
                    return
        if "forward" in locked and (update.message.forward_from or update.message.forward_from_chat):
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Forwards are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "invitelink" in locked:
            text = update.message.text or ""
            if "t.me/joinchat/" in text or "t.me/+" in text or "telegram.me/joinchat/" in text:
                await update.message.delete()
                if lockwarns_enabled[chat_id]:
                    warns[chat_id][user_id] += 1
                    await context.bot.send_message(
                        chat_id,
                        f"⚠️ <b>Invite links are locked!</b> {update.effective_user.mention_html()} warned.",
                        parse_mode="HTML"
                    )
                return
        if "inline" in locked and update.message.via_bot:
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Inline bots are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "command" in locked and update.message.text and update.message.text.startswith("/"):
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Commands are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
        if "externalreply" in locked and update.message.reply_to_message:
            rep = update.message.reply_to_message
            if rep.from_user and rep.from_user.is_bot and rep.from_user.id != context.bot.id:
                await update.message.delete()
                if lockwarns_enabled[chat_id]:
                    warns[chat_id][user_id] += 1
                    await context.bot.send_message(
                        chat_id,
                        f"⚠️ <b>External replies are locked!</b> {update.effective_user.mention_html()} warned.",
                        parse_mode="HTML"
                    )
                return
        if "anonchannel" in locked and getattr(update.message, "sender_chat", None):
            await update.message.delete()
            if lockwarns_enabled[chat_id]:
                warns[chat_id][user_id] += 1
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ <b>Anonymous channel messages are locked!</b> {update.effective_user.mention_html()} warned.",
                    parse_mode="HTML"
                )
            return
    except Exception as e:
        logging.error(f"locks_message_handler error: {e}")

        # --- Blacklist Stickers Module (Simple Version, No SQL) ---

blacklist_stickers = defaultdict(lambda: set())
blacklist_sticker_mode = defaultdict(lambda: ("warn", None))  # ("action", duration)

async def blackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            stickers = blacklist_stickers[chat_id]
            if not stickers:
                await update.message.reply_text(
                    f"There are no blacklisted stickers in <b>{html.escape(update.effective_chat.title or str(chat_id))}</b>!",
                    parse_mode="HTML"
                )
                return
            sticker_list = "<b>List of blacklisted stickers in {}:</b>\n".format(html.escape(update.effective_chat.title or str(chat_id)))
            for s in stickers:
                sticker_list += f" - <code>{html.escape(s)}</code>\n"
            await update.message.reply_text(sticker_list, parse_mode="HTML")

async def add_blackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            member = await context.bot.get_chat_member(chat_id, user_id)
            if not is_admin(member):
                await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                return
            msg = update.message
            if msg.reply_to_message and msg.reply_to_message.sticker and msg.reply_to_message.sticker.set_name:
                trigger = msg.reply_to_message.sticker.set_name
                blacklist_stickers[chat_id].add(trigger.lower())
                await update.message.reply_text(
                    f"Sticker <code>{html.escape(trigger)}</code> added to blacklist stickers in <b>{html.escape(update.effective_chat.title or str(chat_id))}</b>!",
                    parse_mode="HTML"
                )
            elif context.args:
                added = 0
                for trigger in context.args:
                    blacklist_stickers[chat_id].add(trigger.lower())
                    added += 1
                await update.message.reply_text(
                    f"{added} sticker(s) added to blacklist stickers in <b>{html.escape(update.effective_chat.title or str(chat_id))}</b>!",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("Reply to a sticker or provide sticker set names to blacklist.")
async def unblackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            member = await context.bot.get_chat_member(chat_id, user_id)
            if not is_admin(member):
                await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                return
            msg = update.message
            if msg.reply_to_message and msg.reply_to_message.sticker and msg.reply_to_message.sticker.set_name:
                trigger = msg.reply_to_message.sticker.set_name
                if trigger.lower() in blacklist_stickers[chat_id]:
                    blacklist_stickers[chat_id].remove(trigger.lower())
                    await update.message.reply_text(
                        f"Sticker <code>{html.escape(trigger)}</code> removed from blacklist in <b>{html.escape(update.effective_chat.title or str(chat_id))}</b>!",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text("This sticker is not on the blacklist.")
            elif context.args:
                removed = 0
                for trigger in context.args:
                    if trigger.lower() in blacklist_stickers[chat_id]:
                        blacklist_stickers[chat_id].remove(trigger.lower())
                        removed += 1
                await update.message.reply_text(
                    f"{removed} sticker(s) removed from blacklist in <b>{html.escape(update.effective_chat.title or str(chat_id))}</b>!",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("Reply to a sticker or provide sticker set names to unblacklist.")
async def blackliststickermode(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            member = await context.bot.get_chat_member(chat_id, user_id)
            if not is_admin(member):
                await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                return
            if not context.args:
                mode, duration = blacklist_sticker_mode[chat_id]
                await update.message.reply_text(
                    f"Blacklist sticker mode is currently set to <b>{mode}{' ' + duration if duration else ''}</b>.",
                    parse_mode="HTML"
                )
                return
            mode = context.args[0].lower()
            duration = context.args[1] if len(context.args) > 1 else None
            valid_modes = ("off", "nothing", "delete", "warn", "mute", "kick", "ban", "tban", "tmute")
            if mode not in valid_modes:
                await update.message.reply_text("I only understand off/delete/warn/ban/kick/mute/tban/tmute!", parse_mode="HTML")
                return
            if mode in ("tban", "tmute") and not duration:
                await update.message.reply_text("Please specify a duration for tban/tmute (e.g. 10m, 2h).", parse_mode="HTML")
                return
            blacklist_sticker_mode[chat_id] = (mode, duration)
            await update.message.reply_text(
                f"Blacklist sticker mode changed, users will be <b>{mode}{' ' + duration if duration else ''}</b>!",
                parse_mode="HTML"
            )

async def blackliststicker_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not update.message or not update.message.sticker or not update.message.sticker.set_name:
                return
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            set_name = update.message.sticker.set_name.lower()
            if set_name not in blacklist_stickers[chat_id]:
                return
            mode, duration = blacklist_sticker_mode[chat_id]
            try:
                if mode in ("off", "nothing"):
                    return
                await update.message.delete()
                if mode == "delete":
                    return
                elif mode == "warn":
                    warns[chat_id][user_id] += 1
                    count = warns[chat_id][user_id]
                    warn_bar = "🟩" * count + "⬜" * (MAX_WARNS - count)
                    await context.bot.send_message(
                        chat_id,
                        f"⚠️ <b>User warned for blacklisted sticker:</b> <code>{html.escape(set_name)}</code>\n"
                        f"{warn_bar}",
                        parse_mode="HTML"
                    )
                    if count >= MAX_WARNS:
                        await context.bot.ban_chat_member(chat_id, user_id)
                        warns[chat_id][user_id] = 0
                        await context.bot.send_message(
                            chat_id,
                            f"🔨 <b>User banned after max warns (blacklist sticker).</b>",
                            parse_mode="HTML"
                        )
                elif mode == "mute":
                    until_date = datetime.now() + timedelta(days=365*10)
                    await context.bot.restrict_chat_member(
                        chat_id, user_id, permissions=ChatPermissions(can_send_messages=False), until_date=until_date
                    )
                    await context.bot.send_message(
                        chat_id,
                        f"🔇 <b>User muted for blacklisted sticker:</b> <code>{html.escape(set_name)}</code>",
                        parse_mode="HTML"
                    )
                elif mode == "kick":
                    await context.bot.ban_chat_member(chat_id, user_id)
                    await context.bot.unban_chat_member(chat_id, user_id)
                    await context.bot.send_message(
                        chat_id,
                        f"🥾 <b>User kicked for blacklisted sticker:</b> <code>{html.escape(set_name)}</code>",
                        parse_mode="HTML"
                    )
                elif mode == "ban":
                    await context.bot.ban_chat_member(chat_id, user_id)
                    await context.bot.send_message(
                        chat_id,
                        f"🔨 <b>User banned for blacklisted sticker:</b> <code>{html.escape(set_name)}</code>",
                        parse_mode="HTML"
                    )
                elif mode == "tban" and duration:
                    seconds = parse_duration(duration)
                    if seconds:
                        until_date = datetime.now() + timedelta(seconds=seconds)
                        await context.bot.ban_chat_member(chat_id, user_id, until_date=until_date)
                        await context.bot.send_message(
                            chat_id,
                            f"⏳🔨 <b>User tempbanned for blacklisted sticker:</b> <code>{html.escape(set_name)}</code>",
                            parse_mode="HTML"
                        )
                elif mode == "tmute" and duration:
                    seconds = parse_duration(duration)
                    if seconds:
                        until_date = datetime.now() + timedelta(seconds=seconds)
                        await context.bot.restrict_chat_member(
                            chat_id, user_id, permissions=ChatPermissions(can_send_messages=False), until_date=until_date
                        )
                        await context.bot.send_message(
                            chat_id,
                            f"⏳🔇 <b>User tempmuted for blacklisted sticker:</b> <code>{html.escape(set_name)}</code>",
                            parse_mode="HTML"
                        )
            except Exception as e:
                logging.error(f"blackliststicker_message_handler error: {e}")

        # Register blacklist sticker commands and handler in main section

greetings_settings = defaultdict(lambda: {
            "welcome_enabled": True,
            "goodbye_enabled": False,
            "welcome_text": "👋 Welcome, {mention}!",
            "goodbye_text": "😢 Goodbye, {mention}!",
            "clean_welcome": False,
            "last_welcome_msg": None,
        })

def format_greeting(text, user, chat):
            try:
                return text.format(
                    mention=user.mention_html(),
                    first=user.first_name or "",
                    last=user.last_name or "",
                    username="@" + user.username if user.username else user.first_name,
                    chat_title=chat.title or "",
                    id=user.id,
                )
            except Exception as e:
                logging.error(f"format_greeting error: {e}")
                return text

async def welcome_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                if not context.args:
                    status = "ON" if greetings_settings[chat_id]["welcome_enabled"] else "OFF"
                    await update.message.reply_text(
                        f"👋 <b>Welcome messages are currently <u>{status}</u>.</b>\nUse <code>/welcome yes</code> or <code>/welcome no</code>.",
                        parse_mode="HTML"
                    )
                    return
                arg = context.args[0].lower()
                if arg in ("yes", "on", "true", "enable"):
                    greetings_settings[chat_id]["welcome_enabled"] = True
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                        caption="✅ <b>Welcome messages enabled.</b>",
                        parse_mode="HTML"
                    )
                elif arg in ("no", "off", "false", "disable"):
                    greetings_settings[chat_id]["welcome_enabled"] = False
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                        caption="❌ <b>Welcome messages disabled.</b>",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text("❓ <b>Usage:</b> /welcome <yes/no/on/off>", parse_mode="HTML")
            except Exception as e:
                logging.error(f"welcome_command error: {e}")
                await update.message.reply_text(f"❌ Error setting welcome.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def goodbye_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                if not context.args:
                    status = "ON" if greetings_settings[chat_id]["goodbye_enabled"] else "OFF"
                    await update.message.reply_text(
                        f"😢 <b>Goodbye messages are currently <u>{status}</u>.</b>\nUse <code>/goodbye yes</code> or <code>/goodbye no</code>.",
                        parse_mode="HTML"
                    )
                    return
                arg = context.args[0].lower()
                if arg in ("yes", "on", "true", "enable"):
                    greetings_settings[chat_id]["goodbye_enabled"] = True
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                        caption="✅ <b>Goodbye messages enabled.</b>",
                        parse_mode="HTML"
                    )
                elif arg in ("no", "off", "false", "disable"):
                    greetings_settings[chat_id]["goodbye_enabled"] = False
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                        caption="❌ <b>Goodbye messages disabled.</b>",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text("❓ <b>Usage:</b> /goodbye <yes/no/on/off>", parse_mode="HTML")
            except Exception as e:
                logging.error(f"goodbye_command error: {e}")
                await update.message.reply_text(f"❌ Error setting goodbye.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def setwelcome_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                text = update.message.text.partition(" ")[2].strip()
                if not text:
                    await update.message.reply_text("❓ <b>Usage:</b> /setwelcome <text>", parse_mode="HTML")
                    return
                greetings_settings[chat_id]["welcome_text"] = text
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                    caption="✅ <b>Welcome message updated!</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"setwelcome_command error: {e}")
                await update.message.reply_text(f"❌ Error setting welcome message.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def resetwelcome_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                greetings_settings[chat_id]["welcome_text"] = "👋 Welcome, {mention}!"
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                    caption="✅ <b>Welcome message reset to default.</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"resetwelcome_command error: {e}")
                await update.message.reply_text(f"❌ Error resetting welcome message.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def setgoodbye_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                text = update.message.text.partition(" ")[2].strip()
                if not text:
                    await update.message.reply_text("❓ <b>Usage:</b> /setgoodbye <text>", parse_mode="HTML")
                    return
                greetings_settings[chat_id]["goodbye_text"] = text
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                    caption="✅ <b>Goodbye message updated!</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"setgoodbye_command error: {e}")
                await update.message.reply_text(f"❌ Error setting goodbye message.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def resetgoodbye_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                greetings_settings[chat_id]["goodbye_text"] = "😢 Goodbye, {mention}!"
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                    caption="✅ <b>Goodbye message reset to default.</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"resetgoodbye_command error: {e}")
                await update.message.reply_text(f"❌ Error resetting goodbye message.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def cleanwelcome_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                if not context.args:
                    status = "ON" if greetings_settings[chat_id]["clean_welcome"] else "OFF"
                    await update.message.reply_text(
                        f"🧹 <b>Clean welcome is currently <u>{status}</u>.</b>\nUse <code>/cleanwelcome yes</code> or <code>/cleanwelcome no</code>.",
                        parse_mode="HTML"
                    )
                    return
                arg = context.args[0].lower()
                if arg in ("yes", "on", "true", "enable"):
                    greetings_settings[chat_id]["clean_welcome"] = True
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                        caption="✅ <b>Clean welcome enabled.</b>",
                        parse_mode="HTML"
                    )
                elif arg in ("no", "off", "false", "disable"):
                    greetings_settings[chat_id]["clean_welcome"] = False
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                        caption="❌ <b>Clean welcome disabled.</b>",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text("❓ <b>Usage:</b> /cleanwelcome <yes/no/on/off>", parse_mode="HTML")
            except Exception as e:
                logging.error(f"cleanwelcome_command error: {e}")
                await update.message.reply_text(f"❌ Error setting clean welcome.\n<code>{html.escape(str(e))}</code>", parse_mode="HTML")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                if not update.message or not update.message.new_chat_members:
                    return
                chat_id = update.effective_chat.id
                settings = greetings_settings[chat_id]
                if not settings["welcome_enabled"]:
                    return
                # Clean previous welcome if enabled
                if settings["clean_welcome"] and settings["last_welcome_msg"]:
                    try:
                        await context.bot.delete_message(chat_id, settings["last_welcome_msg"])
                    except Exception as e:
                        logging.debug(f"Failed to delete old welcome: {e}")
                for user in update.message.new_chat_members:
                    text = format_greeting(settings["welcome_text"], user, update.effective_chat)
                    try:
                        msg = await update.message.reply_text(
                            text, parse_mode="HTML", disable_web_page_preview=True
                        )
                        if settings["clean_welcome"]:
                            settings["last_welcome_msg"] = msg.message_id
                            # Schedule deletion after 5 minutes
                            async def delete_later(chat_id, msg_id):
                                await asyncio.sleep(300)
                                try:
                                    await context.bot.delete_message(chat_id, msg_id)
                                except Exception:
                                    pass
                            asyncio.create_task(delete_later(chat_id, msg.message_id))
                    except Exception as e:
                        logging.error(f"Error sending welcome: {e}")
            except Exception as e:
                logging.error(f"welcome_new_member error: {e}")

async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                if not update.message or not update.message.left_chat_member:
                    return
                chat_id = update.effective_chat.id
                settings = greetings_settings[chat_id]
                if not settings["goodbye_enabled"]:
                    return
                user = update.message.left_chat_member
                text = format_greeting(settings["goodbye_text"], user, update.effective_chat)
                try:
                    await update.message.reply_text(
                        text, parse_mode="HTML", disable_web_page_preview=True
                    )
                except Exception as e:
                    logging.error(f"Error sending goodbye: {e}")
            except Exception as e:
                logging.error(f"goodbye_member error: {e}")

        # Register greetings handlers in main section


        # --- Rules Module (with Error Handling & Button Support) ---

rules_settings = defaultdict(lambda: {
            "rules": "No rules set yet. Be nice and follow the group guidelines!",
            "privaterules": False,
            "rulesbutton": "Show Rules",
        })

def get_rules(chat_id):
            return rules_settings[chat_id]["rules"]

def get_rules_button(chat_id):
            return rules_settings[chat_id]["rulesbutton"]

async def rules_command(update, context):
            try:
                chat_id = update.effective_chat.id
                args = context.args
                settings = rules_settings[chat_id]
                rules_text = settings["rules"]
                button_name = settings["rulesbutton"]
                priv = settings["privaterules"]

                # /rules noformat
                if args and args[0].lower() == "noformat":
                    await update.message.reply_text(rules_text)
                    return

                # If privaterules is enabled, send rules in private
                if priv and update.effective_user:
                    try:
                        await context.bot.send_message(
                            update.effective_user.id,
                            f"📜 <b>Chat Rules for {update.effective_chat.title or 'this chat'}:</b>\n\n{rules_text}",
                            parse_mode="HTML"
                        )
                        await update.message.reply_text(
                            "📬 <b>Rules sent in private!</b>",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logging.error(f"Failed to send rules in private: {e}")
                        await update.message.reply_text(
                            "❌ <b>Could not send rules in private. Please start a chat with me first.</b>",
                            parse_mode="HTML"
                        )
                    return

                # If rules contain {rules}, show a button
                if "{rules}" in rules_text:
                    button = InlineKeyboardMarkup([
                        [InlineKeyboardButton(button_name, callback_data="show_rules")]
                    ])
                    await update.message.reply_text(
                        rules_text.replace("{rules}", ""),
                        parse_mode="HTML",
                        reply_markup=button
                    )
                else:
                    await update.message.reply_text(
                        f"📜 <b>Chat Rules:</b>\n\n{rules_text}",
                        parse_mode="HTML"
                    )
            except Exception as e:
                logging.error(f"rules_command error: {e}")
                await update.message.reply_text(
                    f"❌ Error showing rules.\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )

async def show_rules_callback(update, context):
            try:
                query = update.callback_query
                chat_id = query.message.chat.id
                rules_text = rules_settings[chat_id]["rules"]
                await query.answer()
                await query.message.reply_text(
                    f"📜 <b>Chat Rules:</b>\n\n{rules_text}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"show_rules_callback error: {e}")
                try:
                    await update.callback_query.answer("❌ Error showing rules.", show_alert=True)
                except Exception:
                    pass

async def setrules_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to set rules!</b>", parse_mode="HTML")
                    return
                text = update.message.text.partition(" ")[2].strip()
                if not text:
                    await update.message.reply_text("❓ <b>Usage:</b> /setrules <text>", parse_mode="HTML")
                    return
                rules_settings[chat_id]["rules"] = text
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                    caption="✅ <b>Rules updated!</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"setrules_command error: {e}")
                await update.message.reply_text(
                    f"❌ Error setting rules.\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )

async def privaterules_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
                    return
                if not context.args:
                    status = "ON" if rules_settings[chat_id]["privaterules"] else "OFF"
                    await update.message.reply_text(
                        f"📬 <b>Private rules is currently <u>{status}</u>.</b>\nUse <code>/privaterules yes</code> or <code>/privaterules no</code>.",
                        parse_mode="HTML"
                    )
                    return
                arg = context.args[0].lower()
                if arg in ("yes", "on", "true", "enable"):
                    rules_settings[chat_id]["privaterules"] = True
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                        caption="✅ <b>Private rules enabled.</b>",
                        parse_mode="HTML"
                    )
                elif arg in ("no", "off", "false", "disable"):
                    rules_settings[chat_id]["privaterules"] = False
                    await update.message.reply_animation(
                        animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                        caption="❌ <b>Private rules disabled.</b>",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text("❓ <b>Usage:</b> /privaterules <yes/no/on/off>", parse_mode="HTML")
            except Exception as e:
                logging.error(f"privaterules_command error: {e}")
                await update.message.reply_text(
                    f"❌ Error setting private rules.\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )

async def resetrules_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to reset rules!</b>", parse_mode="HTML")
                    return
                rules_settings[chat_id]["rules"] = "No rules set yet. Be nice and follow the group guidelines!"
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                    caption="✅ <b>Rules reset to default.</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"resetrules_command error: {e}")
                await update.message.reply_text(
                    f"❌ Error resetting rules.\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )

async def setrulesbutton_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to set the rules button!</b>", parse_mode="HTML")
                    return
                text = update.message.text.partition(" ")[2].strip()
                if not text:
                    await update.message.reply_text("❓ <b>Usage:</b> /setrulesbutton <button name>", parse_mode="HTML")
                    return
                rules_settings[chat_id]["rulesbutton"] = text
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
                    caption=f"✅ <b>Rules button name set to:</b> <code>{html.escape(text)}</code>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"setrulesbutton_command error: {e}")
                await update.message.reply_text(
                    f"❌ Error setting rules button.\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )

async def resetrulesbutton_command(update, context):
            try:
                chat_id = update.effective_chat.id
                user_id = update.effective_user.id
                member = await context.bot.get_chat_member(chat_id, user_id)
                if not is_admin(member):
                    await update.message.reply_text("👮 <b>You must be an admin to reset the rules button!</b>", parse_mode="HTML")
                    return
                rules_settings[chat_id]["rulesbutton"] = "Show Rules"
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
                    caption="✅ <b>Rules button name reset to default.</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"resetrulesbutton_command error: {e}")
                await update.message.reply_text(
                    f"❌ Error resetting rules button.\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )

        # Register rules commands and callback
        # --- AFK Module (Stylish, with Reason & Mention Handling) ---
        # --- Stats Module ---

stats_data = {
    "groups": set(),
    "users": set(),
}

# List of all command handler functions (for stats)
ALL_COMMANDS = [
    "start", "ban", "warn", "unwarn", "warns_command", "speedtest_command", "unban", "mute", "tmute", "unmute", "id_command", "afk_command",
    "xo_start", "join_xo", "cancel_xo", "rps", "joinrps", "cancelrps", "connect4_start", "join_connect4", "cancel_connect4",
    "lowpromote", "midpromote", "fullpromote", "check_rights", "demote", "adminlist", "admincache", "anonadmin", "adminerror",
    "pin", "unpin", "tpin", "flood_command", "setflood", "setfloodtimer", "floodmode", "clearflood",
    "antiraid_command", "raidtime_command", "raidactiontime_command", "autoantiraid_command",
    "help_command", "wordgame_start", "wordgame_cancel", "welcome_command", "goodbye_command", "setwelcome_command", "resetwelcome_command",
    "setgoodbye_command", "resetgoodbye_command", "cleanwelcome_command", "addblocklist", "rmblocklist", "unblocklistall", "blocklist",
    "blocklistmode", "blocklistdelete", "setblocklistreason", "resetblocklistreason", "rules_command", "setrules_command", "privaterules_command",
    "resetrules_command", "setrulesbutton_command", "resetrulesbutton_command", "allowlist_command", "rmallowlist_command", "rmallowlistall_command",
    "lock_command", "unlock_command", "locks_command", "lockwarns_command", "locktypes_command", "explainword_start", "explainword_cancel"
]
ALL_COMMANDS = list(sorted(set(ALL_COMMANDS)))
MODULES_COUNT = len(ALL_COMMANDS)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num_groups = len(stats_data["groups"])
        num_users = len(stats_data["users"])
        assistants = 1
        blocked = ""
        modules = MODULES_COUNT
        sudoers = ""
        bot_me = await context.bot.get_me()
        bot_mention = bot_me.mention_html()
        await update.message.reply_text(
            f"˹{bot_mention}˼ 𝖲𝗍𝖺𝗍𝗌 𝖠𝗇𝖽 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 :\n\n"
            f"𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍𝗌 : <code>{assistants}</code>\n"
            f"𝖡𝗅𝗈𝖼𝗄𝖾𝖽 : <code>{blocked}</code>\n"
            f"𝖦𝗋𝗈𝗎𝗉𝗌 (joined): <code>{num_groups}</code>\n"
            f"𝖴𝗌𝖾𝗋𝗌 (started bot): <code>{num_users}</code>\n"
            f"𝖬𝗈𝖽𝗎𝗅𝖾𝗌 : <code>{modules}</code>\n"
            f"𝖲𝗎𝖽𝗈𝖾𝗋𝗌 : <code>{sudoers}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"stats_command error: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Error fetching stats.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception as ex:
            logging.error(f"stats_command outer fallback error: {ex}")

async def stats_track_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            chat = update.effective_chat
            user = update.effective_user
            if chat:
                if chat.type in ("group", "supergroup"):
                    stats_data["groups"].add(chat.id)
            if user:
                stats_data["users"].add(user.id)
    except Exception as e:
        logging.error(f"stats_track_handler error: {e}")
        # --- Global Ban & Global Mute (Stylish, Robust Error Handling) ---
        # --- Sudo Users Management ---
sudo_users = {
    "lord": 7819315360,  # Replace with your Telegram user ID
    "substitute_lords": {8162803790, 6138142369},  # Both bot users as substitute lords
    "descendants": set(),
}

def is_sudo(user_id):
    try:
        return (
            user_id == sudo_users["lord"] or
            user_id in sudo_users.get("substitute_lords", set()) or
            user_id in sudo_users["descendants"]
        )
    except Exception as e:
        logging.error(f"is_sudo error: {e}")
        return False

async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        # Only lord or substitute lords can add sudo users
        if user_id != sudo_users["lord"] and user_id not in sudo_users.get("substitute_lords", set()):
            await update.message.reply_text("🚫 <b>Only the Lord or Substitute Lord can add sudo users!</b>", parse_mode="HTML")
            return

        # Determine target user id: from reply, argument, or fail
        target_id = None
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        elif context.args and len(context.args) >= 1:
            try:
                target_id = int(context.args[0])
            except Exception as e:
                logging.error(f"addsudo invalid user_id: {e}")
                await update.message.reply_text("❌ <b>Invalid user ID.</b>", parse_mode="HTML")
                return
        else:
            await update.message.reply_text(
                "❓ <b>Usage:</b> Reply to a user or use <code>/addsudo &lt;user_id&gt; [type]</code>\nTypes: <code>lord</code>, <code>substitute</code>, <code>descendant</code>",
                parse_mode="HTML"
            )
            return

        # Determine type: from args or default to descendant
        if update.message.reply_to_message and context.args:
            typ = context.args[0].lower()
        elif context.args and len(context.args) > 1:
            typ = context.args[1].lower()
        else:
            typ = "descendant"

        if typ == "lord":
            sudo_users["lord"] = target_id
            await update.message.reply_text(
                f"👑 <b>Lord set to:</b> <code>{target_id}</code>\n<b>The supreme power has shifted!</b>",
                parse_mode="HTML"
            )
        elif typ in ("substitute", "substitute_lord"):
            sudo_users.setdefault("substitute_lords", set()).add(target_id)
            await update.message.reply_text(
                f"🦸 <b>Substitute Lord added:</b> <code>{target_id}</code>\n<b>A new hero rises as backup!</b>",
                parse_mode="HTML"
            )
        elif typ == "descendant":
            sudo_users["descendants"].add(target_id)
            await update.message.reply_text(
                f"🧬 <b>Descendant added:</b> <code>{target_id}</code>\n<b>The sudo bloodline grows stronger!</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                "❓ <b>Type must be one of: lord, substitute, descendant</b>",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"addsudo error: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Error adding sudo user.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception as ex:
            logging.error(f"addsudo fallback error: {ex}")

async def rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        # Only lord or substitute lords can remove sudo users, but lord can remove anyone
        if user_id != sudo_users["lord"] and user_id not in sudo_users.get("substitute_lords", set()):
            await update.message.reply_text("🚫 <b>Only the Lord or Substitute Lord can remove sudo users!</b>", parse_mode="HTML")
            return

        # Determine target user and type
        target_id = None
        typ = None

        # If replied, get user from reply
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
            # Try to get type from args if present, else auto-detect
            if context.args and context.args[0].lower() in ("lord", "substitute", "substitute_lord", "descendant"):
                typ = context.args[0].lower()
            else:
                # Auto-detect type
                if target_id == sudo_users["lord"]:
                    typ = "lord"
                elif target_id in sudo_users.get("substitute_lords", set()):
                    typ = "substitute"
                elif target_id in sudo_users["descendants"]:
                    typ = "descendant"
        # If not reply, get from args
        elif context.args:
            # If only user_id is given, try to auto-detect type
            if len(context.args) == 1:
                try:
                    target_id = int(context.args[0])
                except Exception as e:
                    logging.error(f"rmsudo invalid user_id: {e}")
                    await update.message.reply_text("❌ <b>Invalid user ID.</b>", parse_mode="HTML")
                    return
                if target_id == sudo_users["lord"]:
                    typ = "lord"
                elif target_id in sudo_users.get("substitute_lords", set()):
                    typ = "substitute"
                elif target_id in sudo_users["descendants"]:
                    typ = "descendant"
                else:
                    await update.message.reply_text("❌ <b>This user is not a sudo user.</b>", parse_mode="HTML")
                    return
            # If type and user_id are given
            elif len(context.args) >= 2:
                typ = context.args[0].lower()
                try:
                    target_id = int(context.args[1])
                except Exception as e:
                    logging.error(f"rmsudo invalid user_id: {e}")
                    await update.message.reply_text("❌ <b>Invalid user ID.</b>", parse_mode="HTML")
                    return
        else:
            await update.message.reply_text(
                "❓ <b>Usage:</b> /rmsudo <code>type</code> <code>user_id</code> or reply to a sudo user\nTypes: <code>lord</code>, <code>substitute</code>, <code>descendant</code>",
                parse_mode="HTML"
            )
            return

        if not target_id or not typ:
            await update.message.reply_text("❌ <b>Could not determine sudo type or user.</b>", parse_mode="HTML")
            return

        # Only lord can remove lord
        if typ == "lord":
            if user_id == sudo_users["lord"]:
                await update.message.reply_text("🚫 <b>You cannot remove yourself as Lord!</b>", parse_mode="HTML")
            else:
                await update.message.reply_text("🚫 <b>Only the Lord can remove the Lord!</b>", parse_mode="HTML")
        elif typ in ("substitute", "substitute_lord"):
            # Lord or substitute lords can remove substitute, but only lord can remove all
            if target_id in sudo_users.get("substitute_lords", set()):
                if user_id == sudo_users["lord"] or user_id in sudo_users.get("substitute_lords", set()):
                    sudo_users["substitute_lords"].discard(target_id)
                    await update.message.reply_text(
                        f"🦸 <b>Substitute Lord removed:</b> <code>{target_id}</code>\n<b>The backup hero has stepped down.</b>",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text(
                        "🚫 <b>Only the Lord or Substitute Lord can remove the Substitute Lord.</b>",
                        parse_mode="HTML"
                    )
            else:
                await update.message.reply_text(
                    "❌ <b>This user is not a Substitute Lord.</b>",
                    parse_mode="HTML"
                )
        elif typ == "descendant":
            # Lord or substitute lords can remove descendants
            if target_id in sudo_users["descendants"]:
                sudo_users["descendants"].discard(target_id)
                await update.message.reply_text(
                    f"🧬 <b>Descendant removed:</b> <code>{target_id}</code>\n<b>The sudo legacy just got lighter.</b>",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    "❌ <b>This user is not a descendant.</b>",
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                "❓ <b>Type must be one of: lord, substitute, descendant</b>",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"rmsudo error: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Error removing sudo user.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception as ex:
            logging.error(f"rmsudo fallback error: {ex}")

async def sudousers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lord = sudo_users["lord"]
    substitute_lords = sudo_users.get("substitute_lords", set())
    descendants = sudo_users["descendants"]
    # Fetch user info for mentions
    lord_mention = "<i>None</i>"
    substitute_mentions = []
    processing_msg = None
    try:
        # Step 1: Gathering sudo hierarchy...
        processing_msg = await update.message.reply_text(
            "<b>👑 <u>Sudo Users Control Panel</u> 👑</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            "<i>Processing sudo users list...</i>\n"
            "🔄 <b>Step 1:</b> Gathering sudo hierarchy...",
            parse_mode="HTML"
        )
        await asyncio.sleep(1.0)
        # Step 2: Formatting user mentions...
        if lord:
            try:
                lord_user = await context.bot.get_chat(lord)
                lord_mention = f"<a href='tg://user?id={lord}'>{html.escape(lord_user.full_name)}</a>"
            except Exception:
                lord_mention = f"<a href='tg://user?id={lord}'>Lord</a>"
        for sub in substitute_lords:
            try:
                sub_user = await context.bot.get_chat(sub)
                substitute_mentions.append(f"<a href='tg://user?id={sub}'>{html.escape(sub_user.full_name)}</a>")
            except Exception:
                substitute_mentions.append(f"<a href='tg://user?id={sub}'>Substitute Lord</a>")
        await processing_msg.edit_text(
            "<b>👑 <u>Sudo Users Control Panel</u> 👑</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            "<i>Processing sudo users list...</i>\n"
            "🔄 <b>Step 2:</b> Formatting user mentions...",
            parse_mode="HTML"
        )
        await asyncio.sleep(1.0)
        # Step 3: Finalizing display...
        text = (
            "<b>👑 <u>Sudo Users Control Panel</u> 👑</b>\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"👑 <b>Lord:</b> {lord_mention}\n"
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        )
        if substitute_mentions:
            text += "🦸 <b>Substitute Lords:</b>\n"
            for sub_mention in substitute_mentions:
                text += f"   └ {sub_mention}\n"
            text += "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        else:
            text += "🦸 <b>Substitute Lords:</b> <i>None</i>\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        if descendants:
            text += "🧬 <b>Descendants:</b>\n"
            for d in descendants:
                try:
                    d_user = await context.bot.get_chat(d)
                    d_mention = f"<a href='tg://user?id={d}'>{html.escape(d_user.full_name)}</a>"
                except Exception:
                    d_mention = f"<a href='tg://user?id={d}'>Descendant</a>"
                text += f"   └ {d_mention}\n"
        else:
            text += "🧬 <b>Descendants:</b> <i>None</i>\n"
        text += (
            "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            "<i>Only the <b>Lord</b> and <b>Substitute Lords</b> can manage sudo users.</i>\n"
            "<b>⚡️ Sudo powers are reserved for the elite. Use them wisely! ⚡️</b>"
        )
        await asyncio.sleep(1.0)
        await processing_msg.edit_text(
            text,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"sudousers error: {e}")
        try:
            if processing_msg:
                await processing_msg.edit_text(
                    f"❌ <b>Error showing sudo users.</b>\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    f"❌ <b>Error showing sudo users.</b>\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
        except Exception as ex:
            logging.error(f"sudousers fallback error: {ex}")

global_bans = set()
global_mutes = set()

async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not is_sudo(user_id):
            await update.message.reply_text("🚫 <b>Only sudo users can use /gban!</b>", parse_mode="HTML")
            return
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user or target_user.id == user_id:
            await update.message.reply_text("🙅‍♂️ <b>You can't gban yourself!</b>", parse_mode="HTML")
            return
        # Prevent gban on any sudo user, lord, or substitute_lord
        if is_sudo(target_user.id):
            await update.message.reply_text("🚫 <b>You cannot gban a sudo user, the Lord, or the Substitute Lord!</b>", parse_mode="HTML")
            return
        if target_user.id == sudo_users["lord"] or target_user.id in sudo_users.get("substitute_lords", set()):
            await update.message.reply_text("🚫 <b>You cannot gban the Lord or the Substitute Lord!</b>", parse_mode="HTML")
            return
        if target_user.id in global_bans:
            await update.message.reply_text("⚠️ <b>User is already globally banned!</b>", parse_mode="HTML")
            return
        global_bans.add(target_user.id)
        # Try to ban in current chat
        try:
            await context.bot.ban_chat_member(chat_id, target_user.id)
        except Exception as e:
            logging.warning(f"gban: Could not ban in current chat: {e}")
        # Processing animation/message for GBAN
        try:
            processing_msg = await update.message.reply_text(
                "<b>🌐 Initiating Global Ban Process...</b>\n"
                "<i>Please wait while we process the global ban request.</i>",
                parse_mode="HTML"
            )
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 1: Gathering all groups...</b>\n"
                    "<i>Locating every group where the bot is present.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gban error (edit step 1): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 2: Executing ban in all groups...</b>\n"
                    "<i>Applying ban to the user across all managed groups.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gban error (edit step 2): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 3: Finalizing global ban...</b>\n"
                    "<i>Ensuring the user is removed and cannot rejoin any group.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gban error (edit step 3): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    f"<b>🌐 GLOBAL BAN EXECUTED</b>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                    f"👤 <b>User:</b> {target_user.mention_html()}\n"
                    f"👮 <b>Actioned By:</b> {update.effective_user.mention_html()}\n"
                    f"🚫 <b>Status:</b> <i>This user has been globally banned from <u>all groups</u> where I am present and have sufficient permissions.</i>\n"
                    f"\n"
                    f"<i>Note: The ban will be enforced automatically in every group the bot is a member of. If the user attempts to join any managed group, they will be instantly removed.</i>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gban error (edit final): {e}")
        except Exception as e:
            logging.error(f"gban error: {e}")
            try:
                await update.message.reply_text(
                    f"❌ <b>Failed to globally ban the user.</b>\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
            except Exception as ex:
                logging.error(f"gban fallback error: {ex}")
    except Exception as e:
        logging.error(f"gban error (outer): {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Unexpected error in gban.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not is_sudo(user_id):
            await update.message.reply_text("🚫 <b>Only sudo users can use /ungban!</b>", parse_mode="HTML")
            return
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user:
            await update.message.reply_text("❓ <b>Could not find the user to unban.</b>", parse_mode="HTML")
            return
        if target_user.id not in global_bans:
            await update.message.reply_text("ℹ️ <b>User is not globally banned.</b>", parse_mode="HTML")
            return
        try:
            processing_msg = await update.message.reply_text(
                "<b>🌐 Initiating Global Unban Process...</b>\n"
                "<i>Please wait while we process the global unban request.</i>",
                parse_mode="HTML"
            )
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 1: Locating all groups...</b>\n"
                    "<i>Identifying every group where the bot is present.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungban error (edit step 1): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 2: Removing ban in all groups...</b>\n"
                    "<i>Allowing the user to rejoin all managed groups.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungban error (edit step 2): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 3: Finalizing global unban...</b>\n"
                    "<i>Ensuring the user can participate again.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungban error (edit step 3): {e}")
            await asyncio.sleep(1.2)
            # Actually unban the user in all groups where the bot is present
            for group_id in list(stats_data["groups"]):
                try:
                    await context.bot.unban_chat_member(group_id, target_user.id)
                except Exception as e:
                    logging.debug(f"ungban: failed to unban user {target_user.id} in group {group_id}: {e}")
            global_bans.discard(target_user.id)
            try:
                await processing_msg.edit_text(
                    f"<b>🌐 GLOBAL UNBAN COMPLETED</b>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                    f"👤 <b>User:</b> {target_user.mention_html()}\n"
                    f"👮 <b>Actioned By:</b> {update.effective_user.mention_html()}\n"
                    f"🎉 <b>Status:</b> <i>This user is now unbanned globally and can join all groups managed by the bot.</i>\n"
                    f"\n"
                    f"<i>Note: The user will be able to participate in all groups unless restricted by other means.</i>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungban error (edit final): {e}")
        except Exception as e:
            logging.error(f"ungban error (processing): {e}")
            try:
                await update.message.reply_text(
                    f"❌ <b>Failed to globally unban the user.</b>\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
            except Exception as ex:
                logging.error(f"ungban fallback error: {ex}")
    except Exception as e:
        logging.error(f"ungban error (outer): {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Unexpected error in ungban.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not is_sudo(user_id):
            await update.message.reply_text("🚫 <b>Only sudo users can use /gmute!</b>", parse_mode="HTML")
            return
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user or target_user.id == user_id:
            await update.message.reply_text("🙅‍♂️ <b>You can't gmute yourself!</b>", parse_mode="HTML")
            return
        # Prevent gmute on any sudo user, lord, or substitute_lord
        if is_sudo(target_user.id):
            await update.message.reply_text("🚫 <b>You cannot gmute a sudo user, the Lord, or the Substitute Lord!</b>", parse_mode="HTML")
            return
        if target_user.id == sudo_users["lord"] or target_user.id in sudo_users.get("substitute_lords", set()):
            await update.message.reply_text("🚫 <b>You cannot gmute the Lord or the Substitute Lord!</b>", parse_mode="HTML")
            return
        if target_user.id in global_mutes:
            await update.message.reply_text("⚠️ <b>User is already globally muted!</b>", parse_mode="HTML")
            return
        try:
            processing_msg = await update.message.reply_text(
                "<b>🌐 Initiating Global Mute Process...</b>\n"
                "<i>Please wait while we process the global mute request.</i>",
                parse_mode="HTML"
            )
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 1: Gathering all groups...</b>\n"
                    "<i>Locating every group where the bot is present.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gmute error (edit step 1): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 2: Muting user in all groups...</b>\n"
                    "<i>Applying mute to the user across all managed groups.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gmute error (edit step 2): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 3: Finalizing global mute...</b>\n"
                    "<i>Ensuring the user cannot send messages in any group.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gmute error (edit step 3): {e}")
            await asyncio.sleep(1.2)
            global_mutes.add(target_user.id)
            try:
                await processing_msg.edit_text(
                    f"<b>🌐 GLOBAL MUTE EXECUTED</b>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                    f"👤 <b>User:</b> {target_user.mention_html()}\n"
                    f"👮 <b>Actioned By:</b> {update.effective_user.mention_html()}\n"
                    f"🔇 <b>Status:</b> <i>This user has been globally muted in <u>all groups</u> where I am present and have sufficient permissions.</i>\n"
                    f"\n"
                    f"<i>Note: Any message sent by this user in any managed group will be automatically deleted until unmuted globally.</i>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"gmute error (edit final): {e}")
        except Exception as e:
            logging.error(f"gmute error (processing): {e}")
            try:
                await update.message.reply_text(
                    f"❌ <b>Failed to globally mute the user.</b>\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
            except Exception as ex:
                logging.error(f"gmute fallback error: {ex}")
    except Exception as e:
        logging.error(f"gmute error (outer): {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Unexpected error in gmute.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def ungmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not is_sudo(user_id):
            await update.message.reply_text("🚫 <b>Only sudo users can use /ungmute!</b>", parse_mode="HTML")
            return
        if update.message.chat.type == "private":
            await update.message.reply_text("🚫 <b>This command can only be used in groups!</b>", parse_mode="HTML")
            return
        target_user = await get_target_user(update, context)
        if not target_user:
            await update.message.reply_text("❓ <b>Could not find the user to unmute.</b>", parse_mode="HTML")
            return
        if target_user.id not in global_mutes:
            await update.message.reply_text("ℹ️ <b>User is not globally muted.</b>", parse_mode="HTML")
            return
        try:
            processing_msg = await update.message.reply_text(
                "<b>🌐 Initiating Global Unmute Process...</b>\n"
                "<i>Please wait while we process the global unmute request.</i>",
                parse_mode="HTML"
            )
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 1: Locating all groups...</b>\n"
                    "<i>Identifying every group where the bot is present.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungmute error (edit step 1): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 2: Removing mute in all groups...</b>\n"
                    "<i>Allowing the user to speak in all managed groups.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungmute error (edit step 2): {e}")
            await asyncio.sleep(1.2)
            try:
                await processing_msg.edit_text(
                    "<b>🌐 Step 3: Finalizing global unmute...</b>\n"
                    "<i>Ensuring the user can participate again.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungmute error (edit step 3): {e}")
            await asyncio.sleep(1.2)
            global_mutes.discard(target_user.id)
            try:
                await processing_msg.edit_text(
                    f"<b>🌐 GLOBAL UNMUTE COMPLETED</b>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                    f"👤 <b>User:</b> {target_user.mention_html()}\n"
                    f"👮 <b>Actioned By:</b> {update.effective_user.mention_html()}\n"
                    f"🔊 <b>Status:</b> <i>This user is now unmuted globally and can send messages in all groups managed by the bot.</i>\n"
                    f"\n"
                    f"<i>Note: The user will be able to participate in all groups unless restricted by other means.</i>\n"
                    f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"ungmute error (edit final): {e}")
        except Exception as e:
            logging.error(f"ungmute error (processing): {e}")
            try:
                await update.message.reply_text(
                    f"❌ <b>Failed to globally unmute the user.</b>\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML"
                )
            except Exception as ex:
                logging.error(f"ungmute fallback error: {ex}")
    except Exception as e:
        logging.error(f"ungmute error (outer): {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Unexpected error in ungmute.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def global_enforcement_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or update.message.chat.type == "private":
            return
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        # Do not enforce on sudo users, lord, or substitute_lord
        if is_sudo(user_id) or user_id == sudo_users["lord"] or user_id in sudo_users.get("substitute_lords", set()):
            return
        # GBAN: Ban user if in global_bans
        if user_id in global_bans:
            try:
                await update.message.delete()
            except Exception as e:
                logging.debug(f"global_enforcement_handler: failed to delete message (gban): {e}")
            try:
                await context.bot.ban_chat_member(chat_id, user_id)
            except Exception as e:
                logging.debug(f"global_enforcement_handler: failed to ban user (gban): {e}")
            try:
                await context.bot.send_message(
                    chat_id,
                    f"🌐 <b>This user is globally banned and has been removed from the group.</b>\n"
                    f"<i>Global bans are enforced across all groups managed by the bot.</i>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.debug(f"global_enforcement_handler: failed to send gban notice: {e}")
            return
        # GMUTE: Delete every message from user if in global_mutes
        if user_id in global_mutes:
            try:
                await update.message.delete()
            except Exception as e:
                logging.debug(f"global_enforcement_handler: failed to delete message (gmute): {e}")
            # Optionally, you can send a notification to the group (commented out to avoid spam)
            # try:
            #     await context.bot.send_message(
            #         chat_id,
            #         f"🌐 <b>This user is globally muted and their message was deleted.</b>",
            #         parse_mode="HTML"
            #     )
            # except Exception as e:
            #     logging.debug(f"global_enforcement_handler: failed to send gmute notice: {e}")
            return
    except Exception as e:
        logging.error(f"global_enforcement_handler error: {e}")

        # Register commands and enforcement handler in main section
afk_status = defaultdict(lambda: {"is_afk": False, "reason": "", "since": None})

async def afk_command(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    reason = " ".join(context.args) if context.args else ""
    afk_status[user_id]["is_afk"] = True
    afk_status[user_id]["reason"] = reason
    afk_status[user_id]["since"] = datetime.now()
    text = f"😴 <b>{update.effective_user.mention_html()} is now AFK!</b>"
    if reason:
        text += f"\n📝 <b>Reason:</b> <i>{html.escape(reason)}</i>"
    try:
        await update.message.reply_text(
            text,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"afk_command error: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Failed to set AFK status.</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def afk_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or update.message.chat.type == "private":
            return
        user_id = update.effective_user.id
        # Remove AFK if user sends a message and was AFK
        if afk_status[user_id]["is_afk"]:
            afk_status[user_id]["is_afk"] = False
            afk_status[user_id]["reason"] = ""
            afk_status[user_id]["since"] = None
            try:
                await update.message.reply_text(
                    f"👋 <b>Welcome back, {update.effective_user.mention_html()}! You are no longer AFK.</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"afk_message_handler error (welcome back): {e}")
        mentioned_ids = set()
        entities = update.message.entities or []
        # Check for mentions by username or text_mention
        for ent in entities:
            try:
                if ent.type == "mention":
                    username = (update.message.text or "")[ent.offset+1:ent.offset+ent.length]
                    for uid, status in afk_status.items():
                        if status["is_afk"]:
                            try:
                                user = await context.bot.get_chat_member(update.effective_chat.id, uid)
                                if user.user.username and user.user.username.lower() == username.lower():
                                    mentioned_ids.add(uid)
                            except Exception as e:
                                logging.debug(f"afk_message_handler error (get_chat_member): {e}")
                                continue
                elif ent.type == "text_mention" and ent.user:
                    mentioned_ids.add(ent.user.id)
            except Exception as e:
                logging.error(f"afk_message_handler error (entity parse): {e}")
        # Check for reply to an AFK user
        if update.message.reply_to_message:
            replied_user = update.message.reply_to_message.from_user
            if replied_user and afk_status[replied_user.id]["is_afk"]:
                mentioned_ids.add(replied_user.id)
        for uid in mentioned_ids:
            try:
                status = afk_status[uid]
                if status["is_afk"]:
                    since = status["since"]
                    since_str = f" (since {since.strftime('%Y-%m-%d %H:%M')})" if since else ""
                    text = f"😴 <b>This user is AFK{since_str}.</b>"
                    if status["reason"]:
                        text += f"\n📝 <b>Reason:</b> <i>{html.escape(status['reason'])}</i>"
                    try:
                        await update.message.reply_text(text, parse_mode="HTML")
                    except Exception as e:
                        logging.error(f"afk_message_handler error (notify mention): {e}")
            except Exception as e:
                logging.error(f"afk_message_handler error (mentioned_ids loop): {e}")
    except Exception as e:
        logging.error(f"afk_message_handler outer error: {e}")

        # Register AFK command and handler

        # --- Banall Command (Lord Only, Confirmation Button) ---


import logging
import html
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# You must import or pass these from your main bot
# from your_main_file import sudo_users, stats_data

async def banall_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, sudo_users, stats_data):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id != sudo_users["lord"]:
        await query.answer("🚫 Only the Lord can confirm this action.", show_alert=True)
        return
    await query.answer("Processing banall...", show_alert=False)
    try:
        banned_count = 0
        failed_count = 0
        already_banned = 0
        total_targets = 0
        for chat_id in list(stats_data["groups"]):
            try:
                admins = await context.bot.get_chat_administrators(chat_id)
                admin_ids = {admin.user.id for admin in admins}
                for uid in list(stats_data["users"]):
                    if uid == sudo_users["lord"] or uid in admin_ids:
                        continue
                    total_targets += 1
                    try:
                        member = await context.bot.get_chat_member(chat_id, uid)
                        if member.status == "kicked":
                            already_banned += 1
                            continue
                        await context.bot.ban_chat_member(chat_id, uid)
                        banned_count += 1
                    except Exception as e:
                        if "USER_ALREADY_BANNED" in str(e) or "kicked" in str(e):
                            already_banned += 1
                        else:
                            failed_count += 1
            except Exception as e:
                logging.error(f"banall: error in chat {chat_id}: {e}")
                failed_count += 1
        await query.edit_message_text(
            f"🔨 <b>Banall completed!</b>\n"
            f"Total targets: <code>{total_targets}</code>\n"
            f"Banned users: <code>{banned_count}</code>\n"
            f"Already banned: <code>{already_banned}</code>\n"
            f"Failed: <code>{failed_count}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"banall_confirm_callback error: {e}")
        try:
            await query.edit_message_text(
                f"❌ <b>Error during banall:</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def banall(update: Update, context: ContextTypes.DEFAULT_TYPE, sudo_users):
    user_id = update.effective_user.id
    if user_id != sudo_users["lord"]:
        await update.message.reply_text("🚫 <b>Only the Lord can use /banall!</b>", parse_mode="HTML")
        return
    confirm_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="banall_cancel"),
         InlineKeyboardButton("✅ Confirm Banall", callback_data="banall_confirm")]
    ])
    await update.message.reply_text(
        "<b>⚠️ Are you sure you want to ban ALL users (except admins and the Lord) from ALL groups?</b>\n"
        "<i>This action is irreversible and will ban all non-admin users from every group the bot is in.</i>\n\n"
        "Press <b>Confirm Banall</b> to proceed or <b>Cancel</b> to abort.",
        parse_mode="HTML",
        reply_markup=confirm_markup
    )

async def banall_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, sudo_users):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id != sudo_users["lord"]:
        await query.answer("🚫 Only the Lord can cancel this action.", show_alert=True)
        return
    await query.answer("Banall cancelled.", show_alert=False)
    try:
        await query.edit_message_text(
            "❌ <b>Banall cancelled.</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

async def unbanall(update: Update, context: ContextTypes.DEFAULT_TYPE, sudo_users, stats_data):
    user_id = update.effective_user.id
    if user_id != sudo_users["lord"]:
        await update.message.reply_text("🚫 <b>Only the Lord can use /unbanall!</b>", parse_mode="HTML")
        return
    try:
        processing_msg = await update.message.reply_text(
            "<b>🌐 Initiating Unbanall Process...</b>\n"
            "<i>Please wait while we process the unban request for all groups.</i>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1.0)
        unbanned_count = 0
        failed_count = 0
        for chat_id in list(stats_data["groups"]):
            try:
                for uid in list(stats_data["users"]):
                    if uid == sudo_users["lord"]:
                        continue
                    try:
                        await context.bot.unban_chat_member(chat_id, uid)
                        unbanned_count += 1
                    except Exception:
                        failed_count += 1
            except Exception as e:
                logging.error(f"unbanall: error in chat {chat_id}: {e}")
                failed_count += 1
        await processing_msg.edit_text(
            f"✅ <b>Unbanall completed!</b>\n"
            f"Unbanned users: <code>{unbanned_count}</code>\n"
            f"Failed: <code>{failed_count}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"unbanall error: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Error during unbanall:</b>\n<code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass
                            # --- Good Morning/Night Auto-Reply Handler ---
                            # Expanded patterns for more languages, styles, and common typo
GOOD_MORNING_PATTERNS = [
                                r"\bgood\s*morning\b",
                                r"\bgm\b",
                                r"\bmorning\b",
                                r"\bsubh\s*prabhat\b",
                                r"\bशुभ\s*प्रभात\b",
                                r"\bbonjour\b",
                                r"\bおはよう\b",
                                r"\b早上好\b",
                                r"\bbuongiorno\b",
                                r"\bbuenos\s*d[ií]as\b",
                                r"\bдоброе\s*утро\b",
                                r"\bguten\s*morgen\b",
                                r"\bصباح\s*الخير\b",
                                r"\bصباح\s*النور\b",
                                r"\b좋은\s*아침\b",
                                r"\b좋은아침\b",
                                r"\bselamat\s*pagi\b",
                                r"\bmagandang\s*umaga\b",
                                r"\bสวัสดี\s*ตอนเช้า\b",
                                r"\bสวัสดีตอนเช้า\b",
                                r"\bkalimera\b",
                                r"\bκαλημέρα\b",
                                r"\bbuongiorno\b",
                                r"\bgoeie\s*more\b",
                                r"\bgoedemorgen\b",
                                r"\bhyvää\s*huomenta\b",
                                r"\bdzień\s*dobry\b",
                                r"\bjó\s*reggelt\b",
                                r"\bдобро\s*утро\b",
                                r"\bdobro\s*juto\b",
                                r"\bbon\s*matin\b",
                                r"\bbonmatin\b",
                                r"\bgoood\s*morning\b",
                                r"\bgood\s*mrng\b",
                                r"\bgood\s*mornin\b",
                                r"\bgood\s*morin\b",
                                r"\bgood\s*mrng\b",
                                r"\bgoood\s*mrng\b",
                                r"\bgmorn\b",
                                r"\bgud\s*morning\b",
                                r"\bgud\s*mrng\b",
                                r"\bgud\s*mornin\b",
                                r"\bgud\s*mrn\b",
                                r"\bgr8\s*morning\b",
                                r"\bgr8\s*mrng\b",
                            ]
GOOD_NIGHT_PATTERNS = [
                                r"\bgood\s*night\b",
                                r"\bgn\b",
                                r"\bnight\b",
                                r"\bshubh\s*ratri\b",
                                r"\bशुभ\s*रात्रि\b",
                                r"\bbonne\s*nuit\b",
                                r"\bおやすみ\b",
                                r"\b晚安\b",
                                r"\bbuenas\s*noches\b",
                                r"\bbuona\s*notte\b",
                                r"\bдоброй\s*ночи\b",
                                r"\bgute\s*nacht\b",
                                r"\bليلة\s*سعيدة\b",
                                r"\bتصبح\s*على\s*خير\b",
                                r"\b잘\s*자요\b",
                                r"\b잘자요\b",
                                r"\bselamat\s*malam\b",
                                r"\bmagandang\s*gabi\b",
                                r"\bราตรี\s*สวัสดิ์\b",
                                r"\bราตรีสวัสดิ์\b",
                                r"\bkalinichta\b",
                                r"\bκαληνύχτα\b",
                                r"\bgoeie\s*naand\b",
                                r"\bgoedenacht\b",
                                r"\bhyvää\s*yötä\b",
                                r"\bdobranoc\b",
                                r"\bjó\s*éjszakát\b",
                                r"\bдобра\s*ноћ\b",
                                r"\bdobra\s*noć\b",
                                r"\bbon\s*soir\b",
                                r"\bbonsoir\b",
                                r"\bgoood\s*night\b",
                                r"\bgood\s*nite\b",
                                r"\bgood\s*nyt\b",
                                r"\bgood\s*nght\b",
                                r"\bgood\s*nt\b",
                                r"\bgoood\s*nite\b",
                                r"\bgnite\b",
                                r"\bgud\s*night\b",
                                r"\bgud\s*nite\b",
                                r"\bgud\s*nyt\b",
                                r"\bgud\s*ngt\b",
                                r"\bgr8\s*night\b",
                                r"\bgr8\s*nite\b",
                            ]

good_morning_regex = re.compile("|".join(GOOD_MORNING_PATTERNS), re.IGNORECASE)
good_night_regex = re.compile("|".join(GOOD_NIGHT_PATTERNS), re.IGNORECASE)

async def wish_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                if not update.message or not update.message.text:
                                    return
                                text = update.message.text.lower()
                                user_mention = update.effective_user.mention_html()
                                if good_morning_regex.search(text):
                                    await update.message.reply_text(
                                        f"🌞 Good morning, {user_mention}! Have a wonderful day ahead!",
                                        parse_mode="HTML"
                                    )
                                elif good_night_regex.search(text):
                                    await update.message.reply_text(
                                        f"🌙 Good night, {user_mention}! Sleep well and sweet dreams!",
                                        parse_mode="HTML"
                                    )

                            # Register the wishes handler (should be after blocklist/locks/afk/wordgame handlers)


GOOD_MORNING_PATTERNS = [
                                r"\bgood\s*morning\b",
                                r"\bgm\b",
                                r"\bmorning\b",
                                r"\bsubh\s*prabhat\b",
                                r"\bशुभ\s*प्रभात\b",
                                r"\bbonjour\b",
                                r"\bおはよう\b",
                                r"\b早上好\b",
                            ]
GOOD_NIGHT_PATTERNS = [
                                r"\bgood\s*night\b",
                                r"\bgn\b",
                                r"\bnight\b",
                                r"\bshubh\s*ratri\b",
                                r"\bशुभ\s*रात्रि\b",
                                r"\bbonne\s*nuit\b",
                                r"\bおやすみ\b",
                                r"\b晚安\b",
                            ]

good_morning_regex = re.compile("|".join(GOOD_MORNING_PATTERNS), re.IGNORECASE)
good_night_regex = re.compile("|".join(GOOD_NIGHT_PATTERNS), re.IGNORECASE)

async def wish_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                                if not update.message or not update.message.text:
                                    return
                                text = update.message.text.lower()
                                user_mention = update.effective_user.mention_html()
                                if good_morning_regex.search(text):
                                    await update.message.reply_text(
                                        f"🌞 Good morning, {user_mention}! Have a wonderful day ahead!",
                                        parse_mode="HTML"
                                    )
                                elif good_night_regex.search(text):
                                    await update.message.reply_text(
                                        f"🌙 Good night, {user_mention}! Sleep well and sweet dreams!",
                                        parse_mode="HTML"
                                    )

                            # Register the wishes handler (should be after blocklist/locks/afk/wordgame handlers)

                            # --- Chess Game (Stylish, Robust Error Handling) ---



active_chess_games = {}

def render_chess_board(board):
    # Use Unicode for board rendering (no SVG in Telegram)
    unicode_pieces = {
        "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
        "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚", ".": "·"
    }
    files = "abcdefgh"
    top = "   " + " ".join(f"<b>{f.upper()}</b>" for f in files)
    sep = "  " + "—" * 23
    rows = [top, sep]
    for rank in range(8, 0, -1):
        row = f"<b>{rank}</b> "
        for file in range(8):
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            symbol = unicode_pieces.get(piece.symbol(), "·") if piece else "·"
            # Alternate background for squares
            bg = "⬛" if (file + rank) % 2 == 0 else "⬜"
            cell = f"{symbol}"
            row += f"{cell} "
        rows.append(row)
    board_str = "\n".join(rows)
    return board_str

def chess_inline_keyboard(board):
    # Generate inline keyboard for chess moves (show all legal moves for the current player)
    keyboard = []
    moves = list(board.legal_moves)
    move_dict = defaultdict(list)
    for move in moves:
        move_dict[chess.square_name(move.from_square)].append(move)
    row = []
    for idx, from_sq in enumerate(sorted(move_dict.keys())):
        row.append(InlineKeyboardButton(f"♟ {from_sq}", callback_data=f"chess_from:{from_sq}"))
        if (idx + 1) % 4 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def chess_to_inline_keyboard(board, from_sq):
    moves = [m for m in board.legal_moves if chess.square_name(m.from_square) == from_sq]
    row = []
    keyboard = []
    for idx, move in enumerate(moves):
        to_sq = chess.square_name(move.to_square)
        row.append(InlineKeyboardButton(f"➡️ {to_sq}", callback_data=f"chess_move:{from_sq}:{to_sq}"))
        if (idx + 1) % 4 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="chess_back")])
    return InlineKeyboardMarkup(keyboard)

async def chess_start(update, context):
    try:
        chat_id = update.effective_chat.id
        if chat_id in active_chess_games:
            await update.message.reply_text("❗ <b>A chess game is already running in this chat!</b>", parse_mode="HTML")
            return
        active_chess_games[chat_id] = {
            "players": [update.effective_user.id],
            "usernames": {update.effective_user.id: update.effective_user.first_name},
            "board": chess.Board(),
            "turn": 0,
            "started": False,
            "message_id": None,
            "awaiting_from": None
        }
        msg = await update.message.reply_animation(
            animation="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif",
            caption="♟️ <b>Waiting for a second player...</b>\n<i>Another user should send /joinchess to join.</i>",
            parse_mode="HTML"
        )
        active_chess_games[chat_id]["message_id"] = msg.message_id
    except Exception as e:
        logging.error(f"chess_start error: {e}")
        await update.message.reply_text("❌ Error starting chess game.")

async def join_chess(update, context):
    try:
        chat_id = update.effective_chat.id
        game = active_chess_games.get(chat_id)
        if not game:
            await update.message.reply_text("❌ No chess game found. Start one with /chess.", parse_mode="HTML")
            return
        if len(game["players"]) >= 2:
            await update.message.reply_text("❌ The game already has 2 players!", parse_mode="HTML")
            return
        if update.effective_user.id in game["players"]:
            await update.message.reply_text("❗ You already joined this game!", parse_mode="HTML")
            return
        game["players"].append(update.effective_user.id)
        game["usernames"][update.effective_user.id] = update.effective_user.first_name
        game["started"] = True
        msg_id = game.get("message_id")
        board = game["board"]
        white = game["players"][0]
        black = game["players"][1]
        game["colors"] = {white: "White", black: "Black"}
        start_message = (
            "♟️ <b>Chess Game Started!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"♔ <b>{game['usernames'][white]}</b> is <b>White</b>\n"
            f"♚ <b>{game['usernames'][black]}</b> is <b>Black</b>\n"
            f"🎲 <b>{game['usernames'][white]}</b> goes first.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Tap a piece to move using the inline buttons below.</i>"
        )
        if msg_id:
            await context.bot.edit_message_caption(
                caption=start_message,
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="HTML"
            )
        else:
            msg = await update.message.reply_text(start_message, parse_mode="HTML")
            game["message_id"] = msg.message_id
        await show_chess_board(update, context, chat_id, inline=True)
    except Exception as e:
        logging.error(f"join_chess error: {e}")
        await update.message.reply_text("❌ Error joining chess game.")

async def show_chess_board(update, context, chat_id, inline=False):
    try:
        game = active_chess_games.get(chat_id)
        if not game:
            return
        board = game["board"]
        board_str = render_chess_board(board)
        turn_player = game["players"][game["turn"]]
        turn_color = game["colors"][turn_player]
        msg_id = game.get("message_id")
        caption = (
            "<b>♟️ Chess Game</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<pre>{board_str}</pre>\n"
            f"🎲 <b>Turn:</b> {game['usernames'][turn_player]} (<b>{turn_color}</b>)"
        )
        reply_markup = None
        if inline:
            reply_markup = chess_inline_keyboard(board)
        if msg_id:
            try:
                await context.bot.edit_message_caption(
                    caption=caption,
                    chat_id=chat_id,
                    message_id=msg_id,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.debug(f"show_chess_board edit error: {e}")
        else:
            msg = await context.bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=reply_markup)
            game["message_id"] = msg.message_id
    except Exception as e:
        logging.error(f"show_chess_board error: {e}")

async def chess_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        if not query:
            return
        chat_id = query.message.chat.id
        game = active_chess_games.get(chat_id)
        if not game or not game.get("started"):
            await query.answer("No active chess game.", show_alert=True)
            return
        user_id = query.from_user.id
        if user_id not in game["players"]:
            await query.answer("You are not a player in this game.", show_alert=True)
            return
        if game["players"][game["turn"]] != user_id:
            await query.answer("⏳ It's not your turn!", show_alert=True)
            return
        data = query.data
        if data.startswith("chess_from:"):
            from_sq = data.split(":")[1]
            await query.edit_message_reply_markup(reply_markup=chess_to_inline_keyboard(game["board"], from_sq))
            game["awaiting_from"] = from_sq
            await query.answer()
            return
        elif data.startswith("chess_move:"):
            _, from_sq, to_sq = data.split(":")
            board = game["board"]
            move = None
            for m in board.legal_moves:
                if chess.square_name(m.from_square) == from_sq and chess.square_name(m.to_square) == to_sq:
                    move = m
                    break
            if not move:
                await query.answer("Invalid move.", show_alert=True)
                return
            board.push(move)
            # Check for checkmate, stalemate, draw
            if board.is_checkmate():
                winner = game["usernames"][user_id]
                await query.edit_message_caption(
                    caption=f"🏆 <b>Checkmate!</b> <b>{winner}</b> wins!\n<pre>{render_chess_board(board)}</pre>",
                    parse_mode="HTML"
                )
                active_chess_games.pop(chat_id, None)
                await query.answer()
                return
            elif board.is_stalemate():
                await query.edit_message_caption(
                    caption=f"🤝 <b>Stalemate! It's a draw.</b>\n<pre>{render_chess_board(board)}</pre>",
                    parse_mode="HTML"
                )
                active_chess_games.pop(chat_id, None)
                await query.answer()
                return
            elif board.is_insufficient_material():
                await query.edit_message_caption(
                    caption=f"🤝 <b>Draw! Insufficient material.</b>\n<pre>{render_chess_board(board)}</pre>",
                    parse_mode="HTML"
                )
                active_chess_games.pop(chat_id, None)
                await query.answer()
                return
            elif board.can_claim_threefold_repetition():
                await query.edit_message_caption(
                    caption=f"🤝 <b>Draw! Threefold repetition.</b>\n<pre>{render_chess_board(board)}</pre>",
                    parse_mode="HTML"
                )
                active_chess_games.pop(chat_id, None)
                await query.answer()
                return
            # Switch turn
            game["turn"] = 1 - game["turn"]
            game["awaiting_from"] = None
            await show_chess_board(update, context, chat_id, inline=True)
            await query.answer("Move played.")
            return
        elif data == "chess_back":
            await query.edit_message_reply_markup(reply_markup=chess_inline_keyboard(game["board"]))
            game["awaiting_from"] = None
            await query.answer()
            return
    except Exception as e:
        logging.error(f"chess_inline_handler error: {e}")
        try:
            await update.callback_query.answer("❌ Error in chess move.", show_alert=True)
        except Exception:
            pass

async def chess_move_handler(update, context):
    try:
        chat_id = update.effective_chat.id
        if chat_id not in active_chess_games:
            return
        game = active_chess_games[chat_id]
        if not game.get("started"):
            return
        user_id = update.effective_user.id
        if user_id not in game["players"]:
            return
        if game["players"][game["turn"]] != user_id:
            await update.message.reply_text("⏳ <b>It's not your turn!</b>", parse_mode="HTML")
            return
        move_text = update.message.text.strip()
        board = game["board"]
        try:
            move = None
            try:
                move = board.parse_uci(move_text)
            except Exception:
                try:
                    move = board.parse_san(move_text)
                except Exception:
                    pass
            if not move or move not in board.legal_moves:
                await update.message.reply_text(
                    "❌ <b>Invalid move!</b> Use algebraic notation (e.g. <code>e2e4</code> or <code>Nf3</code>)",
                    parse_mode="HTML"
                )
                return
            board.push(move)
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>Error parsing move:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
            return
        # Check for checkmate, stalemate, draw
        if board.is_checkmate():
            winner = game["usernames"][user_id]
            await update.message.reply_text(
                f"🏆 <b>Checkmate!</b> <b>{winner}</b> wins!\n<pre>{render_chess_board(board)}</pre>",
                parse_mode="HTML"
            )
            active_chess_games.pop(chat_id, None)
            return
        elif board.is_stalemate():
            await update.message.reply_text(
                f"🤝 <b>Stalemate! It's a draw.</b>\n<pre>{render_chess_board(board)}</pre>",
                parse_mode="HTML"
            )
            active_chess_games.pop(chat_id, None)
            return
        elif board.is_insufficient_material():
            await update.message.reply_text(
                f"🤝 <b>Draw! Insufficient material.</b>\n<pre>{render_chess_board(board)}</pre>",
                parse_mode="HTML"
            )
            active_chess_games.pop(chat_id, None)
            return
        elif board.can_claim_threefold_repetition():
            await update.message.reply_text(
                f"🤝 <b>Draw! Threefold repetition.</b>\n<pre>{render_chess_board(board)}</pre>",
                parse_mode="HTML"
            )
            active_chess_games.pop(chat_id, None)
            return
        # Switch turn
        game["turn"] = 1 - game["turn"]
        await show_chess_board(update, context, chat_id, inline=True)
    except Exception as e:
        logging.error(f"chess_move_handler error: {e}")
        try:
            await update.message.reply_text("❌ Error processing chess move.", parse_mode="HTML")
        except Exception:
            pass

async def cancel_chess(update, context):
    try:
        chat_id = update.effective_chat.id
        game = active_chess_games.get(chat_id)
        msg_id = game.get("message_id") if game else None
        if chat_id in active_chess_games:
            active_chess_games.pop(chat_id, None)
            if msg_id:
                try:
                    await context.bot.edit_message_caption(
                        caption="❌ <b>Chess game cancelled.</b>",
                        chat_id=chat_id,
                        message_id=msg_id,
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            await update.message.reply_text("❌ <b>Chess game cancelled.</b>", parse_mode="HTML")
        else:
            await update.message.reply_text("No active chess game to cancel.", parse_mode="HTML")
    except Exception as e:
        logging.error(f"cancel_chess error: {e}")
        await update.message.reply_text("❌ Could not cancel the chess game due to an error.", parse_mode="HTML")
        # --- Truth and Dare Game ---

active_truthdare_games = {}

TRUTH_QUESTIONS = [
            "If you could have any superpower, what would it be and why?",
            "What is a talent you wish you had?",
            "If you could travel anywhere in the world, where would you go?",
            "What is your favorite childhood memory?",
            "If you could meet any historical figure, who would it be?",
            "What is the most adventurous thing you have ever done?",
            "If you could change one thing about the world, what would it be?",
            "What is your favorite book or movie and why?",
            "If you could instantly master any skill, what would it be?",
            "What is something you are proud of but rarely talk about?",
            "If you could live in any era, which would you choose?",
            "What is your favorite way to relax after a long day?",
            "If you could swap lives with anyone for a day, who would it be?",
            "What is a goal you hope to achieve in the next five years?",
            "What is the best advice you have ever received?",
            "If you could have dinner with any celebrity, who would it be?",
            "What is a hobby you would like to pick up?",
            "What is your favorite thing about yourself?",
            "If you could speak any language fluently, which would you choose?",
            "What is a tradition your family has that you love?",
            "What is the most beautiful place you have ever visited?",
            "If you could time travel, would you go to the past or the future?",
            "What is a food you could eat every day?",
            "What is something you wish more people knew about you?",
            "If you could invent something, what would it be?",
            "What is your favorite holiday and why?",
            "If you could be famous for something, what would it be?",
            "What is a song that always makes you happy?",
            "If you could change one thing about your personality, what would it be?",
            "What is a skill you admire in others?",
            "If you could have any animal as a pet, what would you choose?",
            "What is your favorite way to spend a weekend?",
            "If you could learn any instrument, which would it be?",
            "What is a subject you wish you were better at?",
            "If you could witness any event in history, what would it be?",
            "What is your favorite season and why?",
            "If you could have any job for a day, what would it be?",
            "What is a language you would like to learn?",
            "If you could change your name, would you? What would it be?",
            "What is a cause you are passionate about?",
            "If you could live anywhere, where would it be?",
            "What is your favorite thing to cook or bake?",
            "If you could be an expert in any field, what would it be?",
            "What is a dream you have yet to accomplish?",
            "If you could see the future, what would you want to know?",
            "What is your favorite way to exercise?",
            "If you could be any character from a book or movie, who would you be?",
            "What is a place you want to visit again?",
            "If you could change one thing about your daily routine, what would it be?",
            "What is a lesson you learned the hard way?",
            "If you could have any car, what would you drive?",
            "What is your favorite board or card game?",
            "If you could have a conversation with your future self, what would you ask?",
            "What is your favorite thing about your culture?",
            "If you could be on any reality TV show, which would you choose?",
            "What is a small act of kindness you experienced recently?",
            "If you could design your dream home, what would it look like?",
            "What is a skill you learned as a child that you still use?",
            "If you could change one law, what would it be?",
            "What is your favorite way to spend time outdoors?",
            "If you could have any job in the world, what would it be?",
            "What is a tradition you would like to start?",
            "If you could be any age forever, what age would you choose?",
            "What is your favorite thing to do with friends?",
            "If you could have a conversation with any animal, which would you choose?",
            "What is a goal you are currently working towards?",
            "If you could be a master chef in any cuisine, which would it be?",
            "What is your favorite quote or saying?",
            "If you could change one thing about your school or workplace, what would it be?",
            "What is a technology you are excited about?",
            "If you could be a professional athlete, which sport would you play?",
            "What is your favorite way to give back to your community?",
            "If you could write a book, what would it be about?",
            "What is a language you find beautiful?",
            "If you could have any piece of art in your home, what would it be?",
            "What is your favorite way to celebrate special occasions?",
            "If you could be a character in any video game, who would you be?",
            "What is a subject you could talk about for hours?",
            "If you could have any job in the world for a week, what would it be?",
            "What is your favorite thing to do on a rainy day?",
            "If you could be a part of any fictional universe, which would you choose?",
            "What is a habit you are proud of?",
            "If you could have any magical ability, what would it be?",
            "What is your favorite way to unwind?",
            "If you could be a famous musician, what genre would you play?",
            "What is a place you feel most at peace?",
            "If you could change one thing about the internet, what would it be?",
            "What is your favorite way to learn new things?",
            "If you could have a conversation with your childhood self, what would you say?",
            "What is a tradition you hope to pass on?",
            "If you could be a master at any game, which would it be?",
            "What is your favorite thing about technology?",
            "If you could have any job in the arts, what would you choose?",
            "What is a cause you would volunteer for?",
            "If you could be a character in any TV show, who would you be?",
            "What is your favorite way to stay healthy?",
            "If you could invent a holiday, what would it celebrate?",
            "What is a place you want to explore?",
            "If you could be a scientist, what would you research?",
            "What is your favorite way to spend time with family?",
            "If you could be a leader of a country, what would you change?",
            "What is a lesson you want to teach others?",
            "If you could have any job in the world, what would it be?",
            "What is your favorite way to express creativity?",
            "If you could be a professional in any sport, which would you choose?",
            "What is a tradition you wish was more common?",
            "If you could have any animal as a companion, what would it be?",
            "What is your favorite way to connect with others?",
            "If you could be a character in a fairy tale, who would you be?",
            "What is a goal you have for this year?",
            "If you could have any job in the world, what would it be?",
            "What is your favorite way to spend a holiday?",
            "If you could be a master at any craft, what would it be?",
            "What is a place you want to visit in your lifetime?",
            "If you could have any superpower, what would it be?",
            "What is your favorite way to relax?",
            "If you could be a famous artist, what would you create?",
            "What is a tradition you want to start with your friends?",
            "If you could be a character in a book, who would you be?",
            "What is your favorite way to celebrate achievements?",
            "If you could have any job in the world, what would it be?",
            "What is a skill you want to learn this year?",
            "If you could be a professional in any field, what would it be?",
            "What is your favorite way to spend time alone?",
            "If you could have any animal as a pet, what would it be?",
            "What is your favorite way to help others?",
            "If you could be a character in a movie, who would you be?",
            "What is a goal you have for the next five years?",
            "If you could have any job in the world, what would it be?",
            "What is your favorite way to spend a weekend?",
            "If you could be a master at any skill, what would it be?",
            "What is a place you want to visit again?",
            "If you could have any superpower, what would it be?",
            "What is your favorite way to unwind after a long day?",
            "If you could be a famous musician, what genre would you play?",
            "What is a tradition you want to start with your family?",
            "If you could be a character in a TV show, who would you be?",
            "What is your favorite way to stay active?",
            "If you could invent something, what would it be?",
            "What is a cause you are passionate about?",
            "If you could be a professional athlete, which sport would you play?",
            "What is your favorite way to spend time with friends?",
            "If you could have any job in the world, what would it be?",
            "What is a skill you admire in others?",
            "If you could be a character in a video game, who would you be?",
            "What is your favorite way to learn new things?",
            "If you could have any animal as a companion, what would it be?",
            "What is your favorite way to express yourself?",
            "If you could be a leader of a country, what would you change?",
            "What is a tradition you hope to pass on?",
            "If you could be a master at any game, which would it be?",
            "What is your favorite way to celebrate special occasions?",
            "If you could have any job in the world, what would it be?",
            "What is a goal you are currently working towards?",
            "If you could be a professional in any field, what would it be?",
            "What is your favorite way to spend time outdoors?",
            "If you could have any superpower, what would it be?",
            "What is your favorite way to relax?",
            "If you could be a famous artist, what would you create?",
            "What is a tradition you want to start with your friends?",
            "If you could be a character in a book, who would you be?",
            "What is your favorite way to celebrate achievements?",
            "If you could have any job in the world, what would it be?",
            "What is a skill you want to learn this year?",
            "If you could be a professional in any field, what would it be?",
            "What is your favorite way to spend time alone?",
            "If you could have any animal as a pet, what would it be?",
            "What is your favorite way to help others?",
            "If you could be a character in a movie, who would you be?",
            "What is a goal you have for the next five years?",
            "If you could have any job in the world, what would it be?",
            "What is your favorite way to spend a weekend?",
            "If you could be a master at any skill, what would it be?",
            "What is a place you want to visit again?",
            "If you could have any superpower, what would it be?",
            "What is your favorite way to unwind after a long day?",
            "If you could be a famous musician, what genre would you play?",
            "What is a tradition you want to start with your family?",
            "If you could be a character in a TV show, who would you be?",
            "What is your favorite way to stay active?",
            "If you could invent something, what would it be?",
            "What is a cause you are passionate about?",
            "If you could be a professional athlete, which sport would you play?",
            "What is your favorite way to spend time with friends?",
            "If you could have any job in the world, what would it be?",
            "What is a skill you admire in others?",
            "If you could be a character in a video game, who would you be?",
            "What is your favorite way to learn new things?",
            "If you could have any animal as a companion, what would it be?",
            "What is your favorite way to express yourself?",
            "If you could be a leader of a country, what would you change?",
            "What is a tradition you hope to pass on?",
            "If you could be a master at any game, which would it be?",
            "What is your favorite way to celebrate special occasions?",
            # ... (add more for 500 total, but these are all different types)
        ]

DARE_QUESTIONS = [
            "Do your best dance move for 30 seconds.",
            "Speak in an accent for the next 3 turns.",
            "Share a funny childhood story.",
            "Draw a picture of the person to your right.",
            "Sing the chorus of your favorite song.",
            "Do 10 jumping jacks.",
            "Pretend to be a celebrity for 1 minute.",
            "Tell a joke.",
            "Act like your favorite animal until your next turn.",
            "Send a selfie making a silly face.",
            "Talk in rhymes for the next 2 minutes.",
            "Do your best impression of a famous person.",
            "Balance a book on your head for 1 minute.",
            "Make up a poem about someone in the group.",
            "Say the alphabet backwards.",
            "Do your best robot dance.",
            "Speak only in questions for the next 3 turns.",
            "Draw a picture with your eyes closed.",
            "Share a random fun fact.",
            "Do your best superhero pose.",
            "Act like you just won the lottery.",
            "Pretend to be a news anchor and report a funny story.",
            "Make up a new handshake with someone.",
            "Do your best animal sound.",
            "Tell everyone your favorite joke.",
            "Do a tongue twister 3 times fast.",
            "Pretend to be a chef and describe your signature dish.",
            "Act like a famous movie character.",
            "Do your best runway walk.",
            "Make up a song about pizza.",
            "Pretend to be a weather reporter.",
            "Do your best evil laugh.",
            "Act like you are on a roller coaster.",
            "Pretend to be a robot for 1 minute.",
            "Do your best impression of a teacher.",
            "Make up a story about a talking animal.",
            "Pretend to be a sports commentator.",
            "Do your best superhero impression.",
            "Act like you are in a silent movie.",
            "Pretend to be a famous singer.",
            "Do your best impression of a cartoon character.",
            "Make up a commercial for a silly product.",
            "Act like you are stuck in slow motion.",
            "Pretend to be a tour guide in your city.",
            "Do your best impression of a villain.",
            "Make up a dance for a new song.",
            "Pretend to be a famous athlete.",
            "Do your best impression of a parent.",
            "Act like you are on a cooking show.",
            "Pretend to be a stand-up comedian.",
            "Do your best impression of a superhero's sidekick.",
            "Make up a story about a magical place.",
            "Pretend to be a famous artist.",
            "Do your best impression of a scientist.",
            "Act like you are in a musical.",
            "Pretend to be a famous explorer.",
            "Do your best impression of a game show host.",
            "Make up a new holiday and explain it.",
            "Pretend to be a famous inventor.",
            "Do your best impression of a sports coach.",
            "Act like you are in a movie trailer.",
            "Pretend to be a famous author.",
            "Do your best impression of a detective.",
            "Make up a story about a lost treasure.",
            "Pretend to be a famous dancer.",
            "Do your best impression of a magician.",
            "Act like you are in a talent show.",
            "Pretend to be a famous chef.",
            "Do your best impression of a pilot.",
            "Make up a story about a secret agent.",
            "Pretend to be a famous painter.",
            "Do your best impression of a race car driver.",
            "Act like you are in a fashion show.",
            "Pretend to be a famous actor.",
            "Do your best impression of a news reporter.",
            "Make up a story about a superhero team.",
            "Pretend to be a famous musician.",
            "Do your best impression of a weather forecaster.",
            "Act like you are in a game show.",
            "Pretend to be a famous scientist.",
            "Do your best impression of a talk show host.",
            "Make up a story about a magical creature.",
            "Pretend to be a famous athlete.",
            "Do your best impression of a movie director.",
            "Act like you are in a commercial.",
            "Pretend to be a famous comedian.",
            "Do your best impression of a sports announcer.",
            "Make up a story about a time traveler.",
            "Pretend to be a famous singer.",
            "Do your best impression of a cartoon character.",
            "Act like you are in a music video.",
            "Pretend to be a famous explorer.",
            "Do your best impression of a chef.",
            "Make up a story about a talking animal.",
            "Pretend to be a famous inventor.",
            "Do your best impression of a superhero.",
            "Act like you are in a talent competition.",
            "Pretend to be a famous artist.",
            "Do your best impression of a scientist.",
            "Make up a story about a magical land.",
            "Pretend to be a famous dancer.",
            "Do your best impression of a magician.",
            "Act like you are in a movie scene.",
            "Pretend to be a famous author.",
            "Do your best impression of a detective.",
            "Make up a story about a lost city.",
            "Pretend to be a famous painter.",
            "Do your best impression of a race car driver.",
            "Act like you are in a fashion show.",
            "Pretend to be a famous actor.",
            "Do your best impression of a news reporter.",
            "Make up a story about a superhero team.",
            "Pretend to be a famous musician.",
            "Do your best impression of a weather forecaster.",
            "Act like you are in a game show.",
            "Pretend to be a famous scientist.",
            "Do your best impression of a talk show host.",
            "Make up a story about a magical creature.",
            "Pretend to be a famous athlete.",
            "Do your best impression of a movie director.",
            "Act like you are in a commercial.",
            "Pretend to be a famous comedian.",
            "Do your best impression of a sports announcer.",
            "Make up a story about a time traveler.",
            "Pretend to be a famous singer.",
            "Do your best impression of a cartoon character.",
            "Act like you are in a music video.",
            "Pretend to be a famous explorer.",
            "Do your best impression of a chef.",
            "Make up a story about a talking animal.",
            "Pretend to be a famous inventor.",
            "Do your best impression of a superhero.",
            "Act like you are in a talent competition.",
            "Pretend to be a famous artist.",
            "Do your best impression of a scientist.",
            "Make up a story about a magical land.",
            "Pretend to be a famous dancer.",
            "Do your best impression of a magician.",
            "Act like you are in a movie scene.",
            "Pretend to be a famous author.",
            "Do your best impression of a detective.",
            "Make up a story about a lost city.",
            "Pretend to be a famous painter.",
            "Do your best impression of a race car driver.",
            "Act like you are in a fashion show.",
            "Pretend to be a famous actor.",
            "Do your best impression of a news reporter.",
            "Make up a story about a superhero team.",
            "Pretend to be a famous musician.",
            "Do your best impression of a weather forecaster.",
            "Act like you are in a game show.",
            "Pretend to be a famous scientist.",
            "Do your best impression of a talk show host.",
            "Make up a story about a magical creature.",
            "Pretend to be a famous athlete.",
            "Do your best impression of a movie director.",
            "Act like you are in a commercial.",
            "Pretend to be a famous comedian.",
            "Do your best impression of a sports announcer.",
            "Make up a story about a time traveler.",
            # ... (add more for 500 total, but these are all different types)
        ]

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
from telegram import InputMediaPhoto
import yt_dlp

async def truthdare_command(update, _context):
    keyboard = [
        [InlineKeyboardButton("Truth", callback_data="truthdare:truth"),
         InlineKeyboardButton("Dare", callback_data="truthdare:dare")]
    ]
    await update.message.reply_text(
        "🎲 <b>Truth or Dare!</b>\nChoose one:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def truthdare_button_handler(update, _context):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data
    if data == "truthdare:truth":
        question = random.choice(TRUTH_QUESTIONS)
        await query.edit_message_text(
            f"🟢 <b>Truth:</b> {question}",
            parse_mode="HTML"
        )
    elif data == "truthdare:dare":
        question = random.choice(DARE_QUESTIONS)
        await query.edit_message_text(
            f"🔴 <b>Dare:</b> {question}",
            parse_mode="HTML"
        )

# Add /truth and /dare commands for direct access
async def truth_command(update, _context):
    question = random.choice(TRUTH_QUESTIONS)
    await update.message.reply_text(
        f"🟢 <b>Truth:</b> {question}",
        parse_mode="HTML"
    )

async def dare_command(update, _context):
    question = random.choice(DARE_QUESTIONS)
    await update.message.reply_text(
        f"🔴 <b>Dare:</b> {question}",
        parse_mode="HTML"
    )
       # Register the command and callback in your main section:

                            # Register chess commands and handlers in main section
async def upscale_command(update, context):
    try:
        # Check if the command is a reply to a photo
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text(
                "❓ <b>Reply to an image with /upscale to upscale it.</b>",
                parse_mode="HTML"
            )
            return

        # Send a processing message
        processing_msg = await update.message.reply_text(
            "🖼️ <b>Upscaling image... Please wait.</b>",
            parse_mode="HTML"
        )

        # Get the highest resolution photo
        photo = update.message.reply_to_message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        image_stream = io.BytesIO(file_bytes)

        try:
            img = Image.open(image_stream).convert("RGB")
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ <b>Could not open the image:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
            return

        # Upscale: 2x using high-quality resampling, then enhance
        try:
            new_size = (img.width * 2, img.height * 2)
            upscaled = img.resize(new_size, Image.LANCZOS)
            # Apply more smoothing for extra smoothness
            for _ in range(3):
                upscaled = upscaled.filter(ImageFilter.SMOOTH_MORE)
            # Sharpen after smoothing
            upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))
            # Enhance contrast and sharpness for "very good quality"
            upscaled = ImageEnhance.Contrast(upscaled).enhance(1.25)
            upscaled = ImageEnhance.Sharpness(upscaled).enhance(2.0)
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ <b>Error during upscaling:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
            return

        # Save to bytes as high-quality JPEG
        output = io.BytesIO()
        try:
            upscaled.save(output, format="JPEG", quality=98, subsampling=0, optimize=True)
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ <b>Failed to save upscaled image:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
            return
        output.seek(0)

        # Send as a file (document) for best quality
        await processing_msg.edit_text(
            "✅ <b>Upscaled image ready! Sending as a file for best quality.</b>",
            parse_mode="HTML"
        )
        await update.message.reply_document(
            document=output,
            filename="upscaled_image.jpg",
            caption="🖼️ <b>Upscaled image (2x, extra smooth, sharp, high quality)</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"upscale_command error: {e}")
        try:
            await update.message.reply_text(
                f"❌ <b>Unexpected error during upscaling:</b> <code>{html.escape(str(e))}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

                        # Register the command handler


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != sudo_users["lord"]:
        await update.message.reply_text("🚫 <b>Only the Lord can use /restart!</b>", parse_mode="HTML")
        return
    try:
        msg = await update.message.reply_text("♻️ <b>Restarting bot...</b>", parse_mode="HTML")
        await asyncio.sleep(2)
        await msg.edit_text("♻️ <b>Restarted bot. Shinzou wo Sasageyo!</b>", parse_mode="HTML")
        await asyncio.sleep(1)
        # Flush stdout/stderr to avoid message loss
        sys.stdout.flush()
        sys.stderr.flush()
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>Failed to restart:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

    # --- Couple Selecting Command (Telegram Bot API version, async/pyrogram-like logic) ---
ADDITIONAL_IMAGES = [
    "https://telegra.ph/file/7ef6006ed6e452a6fd871.jpg",
    "https://telegra.ph/file/16ede7c046f35e699ed3c.jpg",
    "https://telegra.ph/file/f16b555b2a66853cc594e.jpg",
    "https://telegra.ph/file/7ef6006ed6e452a6fd871.jpg",
]

couple_storage = defaultdict(dict)  # {chat_id: {date: {"c1_id": ..., "c2_id": ...}}}

def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list

def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a

tomorrow = str(dt_tom())
today = str(dt()[0])

C = """
        •➵💞࿐ 𝐇𝐚𝐩𝐩𝐲 𝐜𝐨𝐮𝐩𝐥𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐝𝐚𝐲
        ╭──────────────
        ┊•➢ {} + ( PGM🎀😶 (https://t.me/Chalnayaaaaaarr) + 花火 (https://t.me/zd_sr07) + ゼロツー (https://t.me/wewewe_x) ) = 💞
        ╰───•➢♡
        ╭──────────────
        ┊•➢ 𝗡𝗲𝘄 𝗰𝗼𝘂𝗽𝗹𝗲 𝗼𝗳 𝘁𝗵𝗲 𝗱𝗮𝘆 𝗺𝗮𝘆𝗯𝗲
        ┊ 𝗰𝗵𝗼𝘀𝗲𝗻 𝗮𝘁 12AM {}
        ╰───•➢♡
        """
CAP = """
        •➵💞࿐ 𝐇𝐚𝐩𝐩𝐲 𝐜𝐨𝐮𝐩𝐥𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐝𝐚𝐲
        ╭──────────────
        ┊•➢ {} + {} = 💞
        ╰───•➢♡
        ╭──────────────
        ┊•➢ 𝗡𝗲𝘄 𝗰𝗼𝘂𝗽𝗹𝗲 𝗼𝗳 𝘁𝗵𝗲 𝗱𝗮𝘆 𝗺𝗮𝘆𝗯𝗲
        ┊ 𝗰𝗵𝗼𝘀𝗲𝗻 𝗮𝘁 12AM {}
        ╰───•➢♡
        """

CAP2 = """
        •➵💞࿐ 𝐇𝐚𝐩𝐩𝐲 𝐜𝐨𝐮𝐩𝐥𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐝𝐚𝐲
        ╭──────────────
        ┊{} (tg://openmessage?user_id={}) + {} (tg://openmessage?user_id={}) = 💞
        ╰───•➢♡
        ╭──────────────
        ┊•➢ 𝗡𝗲𝘄 𝗰𝗼𝘂𝗽𝗹𝗲 𝗼𝗳 𝘁𝗵𝗲 𝗱𝗮𝘆 𝗺𝗮𝘆𝗯𝗲
        ┊ 𝗰𝗵𝗼𝘀𝗲𝗻 𝗮𝘁 12AM {}
        ╰───•➢♡
        """

async def get_couple(chat_id, date):
    return couple_storage[chat_id].get(date)

async def save_couple(chat_id, date, couple):
    couple_storage[chat_id][date] = couple

async def couple_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("This command only works in groups!")
        return
    COUPLES_PIC = random.choice(ADDITIONAL_IMAGES)
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    # Special user shortcut (optional, can be removed)
    if user_id == 5540249238:
        await update.message.reply_photo(
            photo=COUPLES_PIC, caption=C.format(update.effective_user.mention_html(), tomorrow), parse_mode="HTML"
        )
        return
    try:
        is_selected = await get_couple(chat_id, today)
        if not is_selected:
            # Get all group members (excluding admins and bots)
            members = set()
            try:
                # Get admin user IDs
                admin_ids = set()
                admins = await context.bot.get_chat_administrators(chat_id)
                for admin in admins:
                    admin_ids.add(admin.user.id)
                # Telegram API does not provide a direct way to list all members.
                # So, we use recent message senders as a proxy (best effort).
                async for message in context.bot.get_chat_history(chat_id, limit=500):
                    user = message.from_user
                    if (
                        user
                        and user.id not in admin_ids
                        and not user.is_bot
                    ):
                        members.add(user.id)
                members = list(members)
            except Exception as e:
                logging.error(f"couple_command: failed to get group members: {e}")
            if len(members) < 2:
                await update.message.reply_text("Not enough users in the group. Please ensure there are at least 2 non-admin, non-bot members who have recently sent messages.")
                return
            c1_id = random.choice(members)
            c2_id = random.choice(members)
            while c1_id == c2_id:
                c2_id = random.choice(members)
            c1_user = await context.bot.get_chat(c1_id)
            c2_user = await context.bot.get_chat(c2_id)
            c1_mention = c1_user.mention_html()
            c2_mention = c2_user.mention_html()
            await context.bot.send_photo(
                chat_id,
                photo=COUPLES_PIC,
                caption=CAP.format(c1_mention, c2_mention, tomorrow),
                parse_mode="HTML"
            )
            couple = {"c1_id": c1_id, "c2_id": c2_id}
            await save_couple(chat_id, today, couple)
        else:
            c1_id = int(is_selected["c1_id"])
            c2_id = int(is_selected["c2_id"])
            c1_user = await context.bot.get_chat(c1_id)
            c2_user = await context.bot.get_chat(c2_id)
            c1_name = c1_user.first_name
            c2_name = c2_user.first_name
            couple_selection_message = (
                f"•➵💞࿐ 𝐇𝐚𝐩𝐩𝐲 𝐜𝐨𝐮𝐩𝐥𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐝𝐚𝐲\n"
                f"╭──────────────\n"
                f"┊•➢ [{c1_name}](tg://openmessage?user_id={c1_id}) + [{c2_name}](tg://openmessage?user_id={c2_id}) = 💞\n"
                f"╰───•➢♡\n"
                f"╭──────────────\n"
                f"┊•➢ 𝗡𝗲𝘄 𝗰𝗼𝘂𝗽𝗹𝗲 𝗼𝗳 𝘁𝗵𝗲 𝗱𝗮𝘆 𝗺𝗮𝘆𝗯𝗲\n"
                f"┊ 𝗰𝗵𝗼𝘀𝗲𝗻 𝗮𝘁 12AM {tomorrow}\n"
                f"╰───•➢♡"
            )
            await context.bot.send_photo(
                chat_id, photo=COUPLES_PIC, caption=couple_selection_message, parse_mode="Markdown"
            )
    except Exception as e:
        logging.error(f"couple_command error: {e}")
        await update.message.reply_text(str(e))

    # Register the couple command

import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DEFAULT_REGION = "ind"

def parse_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M')
    except:
        return 'N/A'

async def ff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /ff <player_id> [region]")
            return

        player_id = context.args[0]
        region = context.args[1].lower() if len(context.args) > 1 else DEFAULT_REGION

        api_url = f"https://ariiflexlabs-playerinfo-icxc.onrender.com/ff_info?uid={player_id}&region={region}"
        response = requests.get(api_url)

        if response.status_code != 200:
            await update.message.reply_text("❌ Failed to fetch player info. Please check the ID and try again.")
            return

        data = response.json()
        account = data.get("AccountInfo", {})
        profile = data.get("AccountProfileInfo", {})
        guild = data.get("GuildInfo", {})
        captain = data.get("captainBasicInfo", {})
        social = data.get("socialinfo", {})

        name = account.get("AccountName", captain.get("nickname", "N/A"))
        level = account.get("AccountLevel", captain.get("level", "N/A"))
        exp = account.get("AccountEXP", captain.get("exp", "N/A"))
        region_display = account.get("AccountRegion", captain.get("region", "N/A")).upper()

        create_time = parse_timestamp(account.get("AccountCreateTime", captain.get("createAt", 0)))
        last_login = parse_timestamp(account.get("AccountLastLogin", captain.get("lastLoginAt", 0)))

        br_rank = account.get('BrRankPoint', captain.get('rankingPoints', 'N/A'))
        br_max = account.get('BrMaxRank', captain.get('maxRank', 'N/A'))
        cs_rank = account.get('CsRankPoint', captain.get('csRankingPoints', 'N/A'))
        cs_max = account.get('CsMaxRank', captain.get('csMaxRank', 'N/A'))

        weapons = ', '.join(map(str, account.get('EquippedWeapon', []))) or 'N/A'
        outfits = ', '.join(map(str, profile.get('EquippedOutfit', []))) or 'N/A'

        guild_name = guild.get('GuildName', 'N/A')
        guild_level = guild.get('GuildLevel', 'N/A')
        guild_members = f"{guild.get('GuildMember', 'N/A')}/{guild.get('GuildCapacity', 'N/A')}"

        signature = social.get('AccountSignature', 'N/A')
        prefer_mode = social.get('AccountPreferMode', 'N/A').split('_')[-1] if social.get('AccountPreferMode') else 'N/A'

        info_text = f"""
🎮 *Free Fire Player Info* 🎮

👤 *Basic Info:*
├─ Name: `{name}`
├─ Level: `{level}`
├─ EXP: `{exp}`
├─ Region: `{region_display}`
├─ Created: `{create_time}`
└─ Last Login: `{last_login}`

🏆 *Rank Info:*
├─ BR Rank: `{br_rank} pts (Max: {br_max})`
└─ CS Rank: `{cs_rank} pts (Max: {cs_max})`

👕 *Equipment:*
├─ Weapons: `{weapons}`
└─ Outfit: `{outfits}`

🏛️ *Guild Info:*
├─ Name: `{guild_name}`
├─ Level: `{guild_level}`
└─ Members: `{guild_members}`

📝 *Social:*
├─ Signature: `{signature}`
└─ Preferred Mode: `{prefer_mode}`

🔗 *Profile Link:* [View in FF](https://freefiremobile.com/profile/{player_id})
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_ff_{player_id}_{region}")]
        ])

        await update.message.reply_text(
            info_text.strip(),
            reply_markup=buttons,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: `{str(e)}`", parse_mode="Markdown")

async def refresh_ff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        data_parts = query.data.split("_", 2)
        player_id = data_parts[2]
        region = data_parts[3]

        api_url = f"https://ariiflexlabs-playerinfo-icxc.onrender.com/ff_info?uid={player_id}&region={region}"
        response = requests.get(api_url)

        if response.status_code != 200:
            await query.answer("Failed to refresh data", show_alert=True)
            return

        data = response.json()
        account = data.get("AccountInfo", {})
        last_login = parse_timestamp(account.get('AccountLastLogin', 0))

        # Update only the Last Login line in the message
        old_lines = query.message.text.splitlines()
        new_lines = []
        for line in old_lines:
            if "Last Login:" in line:
                new_lines.append(f"└─ Last Login: `{last_login}`")
            else:
                new_lines.append(line)

        await query.edit_message_text(
            text="\n".join(new_lines),
            reply_markup=query.message.reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.callback_query.answer(f"Error: {str(e)}", show_alert=True)


async def mmf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("❗ Reply to an image with: `/mmf top;text;bottom`", parse_mode="Markdown")
        return

    if len(context.args) == 0:
        await message.reply_text("❗ Give some text after the command like `/mmf Hello;World`", parse_mode="Markdown")
        return

    text = " ".join(context.args)

    msg = await message.reply_text("🧠 Memifying this image...")

    photo = message.reply_to_message.photo[-1]
    image_path = await photo.get_file()
    downloaded = await image_path.download_to_drive()

    meme = await draw_text_on_image(downloaded, text)
    await message.reply_document(document=open(meme, "rb"))

    os.remove(meme)
    os.remove(downloaded)
    await msg.delete()


# === Text Drawing Helper ===
async def draw_text_on_image(image_path, text):
    img = Image.open(image_path)
    i_width, i_height = img.size

    try:
        font_path = FONT_PATH if os.name != 'nt' else "arial.ttf"
        font = ImageFont.truetype(font_path, int((70 / 640) * i_width))
    except:
        font = ImageFont.load_default()

    upper_text, lower_text = (text.split(";", 1) + [""])[:2]
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    def get_text_size(txt):
        bbox = draw.textbbox((0, 0), txt, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Upper text
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = get_text_size(u_text)
            x = (i_width - u_width) / 2
            y = int((current_h / 640) * i_width)

            for offset in [(-2,0), (2,0), (0,-2), (0,2)]:
                draw.text((x + offset[0], y + offset[1]), u_text, font=font, fill="black")
            draw.text((x, y), u_text, font=font, fill="white")

            current_h += u_height + pad

    # Lower text
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = get_text_size(l_text)
            x = (i_width - u_width) / 2
            y = i_height - u_height - int((20 / 640) * i_width)

            for offset in [(-2,0), (2,0), (0,-2), (0,2)]:
                draw.text((x + offset[0], y + offset[1]), l_text, font=font, fill="black")
            draw.text((x, y), l_text, font=font, fill="white")

    out_path = "meme.webp"
    img.save(out_path, "webp")
    return out_path
FONT_PATH = "fonts/Roboto-Regular.ttf" if os.path.exists("fonts/Roboto-Regular.ttf") else "arial.ttf"
from io import BytesIO
from httpx import AsyncClient, Timeout
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

fetch = AsyncClient(
    http2=True,
    verify=False,
    headers={
        "Accept-Language": "id-ID",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edge/107.0.1418.42",
    },
    timeout=Timeout(20),
)

class QuotlyException(Exception):
    pass


# ================== HELPERS ===================

async def get_text_or_caption(message):
    return message.text or message.caption or ""

async def pyrogram_to_quotly(message, context: ContextTypes.DEFAULT_TYPE, is_reply):
    messages = [message]
    if context.args:
        try:
            count = int(context.args[0])
            if count < 2 or count > 10:
                return None, "❌ Range must be between 2 and 10"
            start_id = message.reply_to_message.message_id
            end_id = start_id + count
            messages = []
            for msg_id in range(start_id, end_id):
                try:
                    msg = await context.bot.get_chat(message.chat.id)
                    fetched = await context.bot.get_message(message.chat.id, msg_id)
                    if fetched and not fetched.photo and not fetched.video:
                        messages.append(fetched)
                except:
                    pass
        except ValueError:
            return None, "❌ Invalid number format"

    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": []
    }

    for msg in messages:
        sender = msg.from_user
        name = sender.full_name
        username = sender.username or ""
        chat_type = "private" if msg.chat.type.name == "private" else "group"
        photo = ""

        text = await get_text_or_caption(msg)
        entities = [
            {
                "type": entity.type.name.lower(),
                "offset": entity.offset,
                "length": entity.length
            }
            for entity in msg.entities or msg.caption_entities or []
        ]

        reply = {}
        if is_reply and msg.reply_to_message:
            reply = {
                "name": msg.reply_to_message.from_user.full_name,
                "text": await get_text_or_caption(msg.reply_to_message),
                "chatId": msg.reply_to_message.from_user.id
            }

        payload["messages"].append({
            "chatId": sender.id,
            "text": text,
            "entities": entities,
            "avatar": True,
            "from": {
                "id": sender.id,
                "name": name,
                "username": username,
                "type": chat_type,
                "photo": photo
            },
            "replyMessage": reply
        })

    response = await fetch.post("https://bot.lyo.su/quote/generate.png", json=payload)
    if not response.is_error:
        return response.read(), None
    raise QuotlyException(response.json())

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.reply_to_message:
        await message.reply_text("⚠️ Reply to a message to quote it.")
        return

    is_reply = message.text and message.text.startswith("/r")

    try:
        data, error = await pyrogram_to_quotly(message, context, is_reply)
        if error:
            await message.reply_text(error)
            return
        sticker = BytesIO(data)
        sticker.name = "quote.webp"
        await message.reply_sticker(sticker)
    except Exception as e:
        await message.reply_text(f"❌ Failed to generate quote: {e}")
            # --- Simple Sangmata-like "sg" Command for Username/Name History Tracking ---

            # In-memory storage for user data: {user_id: {"username": ..., "first_name": ..., "last_name": ...}}
# --- Sangmata-like "sg" Command for Username/Name History Tracking ---

# Store full history: {user_id: {"username": [..], "first_name": [..], "last_name": [..]}}
sg_userdata = defaultdict(lambda: {"username": [], "first_name": [], "last_name": []})
sg_enabled = defaultdict(lambda: False)

async def sg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    # Only admins can enable/disable
    member = await context.bot.get_chat_member(chat_id, user_id)
    if not is_admin(member):
        await update.message.reply_text("👮 <b>You must be an admin to use this command!</b>", parse_mode="HTML")
        return
    # If reply to a user: show their history
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target = update.message.reply_to_message.from_user
        # Try to fetch from sangmata-api
        sangmata_data = await fetch_sangmata_history(target.id)
        if sangmata_data:
            def uniq(seq):
                seen = set()
                return [x for x in seq if x and not (x in seen or seen.add(x))]
            usernames = uniq(sangmata_data.get("username", []))
            first_names = uniq(sangmata_data.get("first_name", []))
            last_names = uniq(sangmata_data.get("last_name", []))
            text = f"<b>👁️‍🗨️ Sangmata History for {target.mention_html()} <code>{target.id}</code></b>\n"
            if usernames:
                text += "🆔 <b>Usernames:</b>\n" + "\n".join(f"• <code>@{u}</code>" for u in usernames if u) + "\n"
            if first_names:
                text += "👤 <b>First Names:</b>\n" + "\n".join(f"• <code>{html.escape(n)}</code>" for n in first_names if n) + "\n"
            if last_names:
                text += "👥 <b>Last Names:</b>\n" + "\n".join(f"• <code>{html.escape(n)}</code>" for n in last_names if n) + "\n"
            if not (usernames or first_names or last_names):
                text += "<i>No history found for this user.</i>"
            await update.message.reply_text(text, parse_mode="HTML")
            return
        # fallback to local
        history = sg_userdata[target.id]
        def uniq(seq):
            seen = set()
            return [x for x in seq if x and not (x in seen or seen.add(x))]
        usernames = uniq(history["username"])
        first_names = uniq(history["first_name"])
        last_names = uniq(history["last_name"])
        text = f"<b>👁️‍🗨️ Sangmata History for {target.mention_html()} <code>{target.id}</code></b>\n"
        if usernames:
            text += "🆔 <b>Usernames:</b>\n" + "\n".join(f"• <code>@{u}</code>" for u in usernames if u) + "\n"
        if first_names:
            text += "👤 <b>First Names:</b>\n" + "\n".join(f"• <code>{html.escape(n)}</code>" for n in first_names if n) + "\n"
        if last_names:
            text += "👥 <b>Last Names:</b>\n" + "\n".join(f"• <code>{html.escape(n)}</code>" for n in last_names if n) + "\n"
        if not (usernames or first_names or last_names):
            text += "<i>No history found for this user.</i>"
        await update.message.reply_text(text, parse_mode="HTML")
        return
    # Otherwise: enable/disable
    if not context.args:
        status = "ON" if sg_enabled[chat_id] else "OFF"
        await update.message.reply_text(
            f"👁️‍🗨️ <b>Sangmata (username/name history) is currently <u>{status}</u>.</b>\n"
            f"Use <code>/sg on</code> or <code>/sg off</code>.\n"
            f"Or reply to a user with <code>/sg</code> to see their history.",
            parse_mode="HTML"
        )
        return
    arg = context.args[0].lower()
    if arg in ("on", "yes", "enable", "true"):
        sg_enabled[chat_id] = True
        await update.message.reply_text("✅ <b>Sangmata enabled. Name/username changes will be tracked.</b>", parse_mode="HTML")
    elif arg in ("off", "no", "disable", "false"):
        sg_enabled[chat_id] = False
        await update.message.reply_text("❌ <b>Sangmata disabled. Name/username changes will not be tracked.</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("❓ <b>Usage:</b> /sg <on/off> or reply to a user.", parse_mode="HTML")

async def sg_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only in groups, only if enabled
    if not update.message or update.message.chat.type == "private":
        return
    chat_id = update.effective_chat.id
    if not sg_enabled[chat_id]:
        return
    user = update.effective_user
    if not user or user.is_bot:
        return
    user_id = user.id
    prev = sg_userdata[user_id]
    msg = ""
    changed = False
    # Username history
    if user.username and (not prev["username"] or user.username != prev["username"][-1]):
        prev["username"].append(user.username)
        if len(prev["username"]) > 1 and prev["username"][-2] != user.username:
            before = f"@{prev['username'][-2]}" if prev["username"][-2] else "<i>None</i>"
            after = f"@{user.username}" if user.username else "<i>None</i>"
            msg += f"📝 <b>Username changed:</b> {before} → {after}\n"
            changed = True
    elif user.username is None and (not prev["username"] or prev["username"][-1] is not None):
        prev["username"].append(None)
        msg += f"📝 <b>Username removed.</b>\n"
        changed = True
    # First name history
    if user.first_name and (not prev["first_name"] or user.first_name != prev["first_name"][-1]):
        prev["first_name"].append(user.first_name)
        if len(prev["first_name"]) > 1 and prev["first_name"][-2] != user.first_name:
            before = prev["first_name"][-2] or "<i>None</i>"
            after = user.first_name or "<i>None</i>"
            msg += f"📝 <b>First name changed:</b> <code>{before}</code> → <code>{after}</code>\n"
            changed = True
    # Last name history
    if user.last_name != (prev["last_name"][-1] if prev["last_name"] else None):
        prev["last_name"].append(user.last_name)
        if len(prev["last_name"]) > 1 and prev["last_name"][-2] != user.last_name:
            before = prev["last_name"][-2] or "<i>None</i>"
            after = user.last_name or "<i>None</i>"
            msg += f"📝 <b>Last name changed:</b> <code>{before}</code> → <code>{after}</code>\n"
            changed = True
    if changed:
        text = (
            f"<b>👁️‍🗨️ Sangmata Alert</b>\n"
            f"User: {user.mention_html()} <code>{user.id}</code>\n"
            f"{msg}"
        )
        try:
            await update.message.reply_text(text, parse_mode="HTML")
        except Exception:
            pass

async def fetch_sangmata_history(user_id):
    """
    Fetch user history from @sangmata_bot via sangmata-api.up.railway.app.
    Returns a dict with keys: username, first_name, last_name (each a list).
    """
    url = f"https://sangmata-api.up.railway.app/api/history/{user_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
    except Exception as e:
        logging.error(f"fetch_sangmata_history error: {e}")
    return None

BINGSEARCH_URL = "https://sugoi-api.vercel.app/search"
NEWS_URL = "https://sugoi-api.vercel.app/news?keyword={}"


async def news_command(update, context):
        keyword = " ".join(context.args) if context.args else ""
        url = NEWS_URL.format(keyword)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    news_data = await resp.json()
            if "error" in news_data:
                await update.message.reply_text(f"Error: {news_data['error']}")
            elif news_data:
                news_item = random.choice(news_data)
                title = news_item.get("title", "")
                excerpt = news_item.get("excerpt", "")
                source = news_item.get("source", "")
                relative_time = news_item.get("relative_time", "")
                news_url = news_item.get("url", "")
                message_text = (
                    f"𝗧𝗜𝗧𝗟𝗘: {title}\n"
                    f"𝗦𝗢𝗨𝗥𝗖𝗘: {source}\n"
                    f"𝗧𝗜𝗠𝗘: {relative_time}\n"
                    f"𝗘𝗫𝗖𝗘𝗥𝗣𝗧: {excerpt}\n"
                    f"𝗨𝗥𝗟: {news_url}"
                )
                await update.message.reply_text(message_text)
            else:
                await update.message.reply_text("No news found.")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

async def bingsearch_command(update, context):
    if not context.args:
        await update.message.reply_text("Please provide a keyword to search.")
        return
    keyword = " ".join(context.args)
    params = {"keyword": keyword}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BINGSEARCH_URL, params=params) as resp:
                if resp.status == 200:
                    try:
                        results = await resp.json()
                    except Exception:
                        await update.message.reply_text("Sorry, something went wrong with the search (invalid response).")
                        return
                    if not results or not isinstance(results, list):
                        await update.message.reply_text("No results found.")
                    else:
                        message_text = ""
                        for result in results[:7]:
                            title = result.get("title", "")
                            link = result.get("link", "")
                            message_text += f"{title}\n{link}\n\n"
                        await update.message.reply_text(message_text.strip())
                else:
                    if resp.status == 500:
                        await update.message.reply_text("Sorry, the search service is temporarily unavailable (HTTP 500). Please try again later.")
                    else:
                        await update.message.reply_text(f"Sorry, something went wrong with the search. (HTTP {resp.status})")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def bingimg_command(update, context):
    if not context.args:
        await update.message.reply_text("Provide me a query to search!")
        return
    text = " ".join(context.args)
    search_message = await update.message.reply_text("🔎")
    bingimg_url = f"https://sugoi-api.vercel.app/bingimg?keyword={text}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(bingimg_url) as resp:
                images = await resp.json()
        media = []
        for img in images[:7]:
            media.append(InputMediaPhoto(media=img))
        if media:
            await update.message.reply_media_group(media=media)
        await search_message.delete()
        await update.message.delete()
    except Exception as e:
        await search_message.edit_text(f"Error: {str(e)}")

async def googleimg_command(update, context):
        if not context.args:
            await update.message.reply_text("Provide me a query to search!")
            return
        text = " ".join(context.args)
        search_message = await update.message.reply_text("💭")
        googleimg_url = f"https://sugoi-api.vercel.app/googleimg?keyword={text}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(googleimg_url) as resp:
                    images = await resp.json()
            media = []
            for img in images[:7]:
                media.append(InputMediaPhoto(media=img))
            if media:
                await update.message.reply_media_group(media=media)
            await search_message.delete()
            await update.message.delete()
        except Exception as e:
            await search_message.edit_text(f"Error: {str(e)}")
            # --- Instagram, YouTube, Pinterest Video Downloader Handler ---
async def download_video(update: Update, _: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return
        text = update.message.text.strip()
        # Check if the message contains a YouTube link
        yt_regex = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+"
        match = re.search(yt_regex, text)
        if not match:
            return  # Ignore non-YouTube links/messages

        url = match.group(0)
        processing_msg = await update.message.reply_text("⬇️ Downloading video, please wait...")

        # Download video using yt_dlp
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "ytvideo.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "merge_output_format": None,
        }
        loop = asyncio.get_running_loop()
        info = {}

        def run_yt(opts):
            with yt_dlp.YoutubeDL(opts) as ydl:
                info.update(ydl.extract_info(url, download=True))
                return ydl.prepare_filename(info)

        try:
            filename = await loop.run_in_executor(None, run_yt, ydl_opts)
        except Exception as e:
            err_str = str(e)
            if "ffmpeg" in err_str.lower():
                await processing_msg.edit_text(
                    "❌ Failed to download video: <b>ffmpeg is not installed on the server. Please install ffmpeg to enable video downloads.</b>",
                    parse_mode="HTML"
                )
            else:
                await processing_msg.edit_text(f"❌ Failed to download video: <code>{html.escape(err_str)}</code>", parse_mode="HTML")
            return

        # Check file size before sending (Telegram limit is 2GB for bots)
        file_size = os.path.getsize(filename)
        tg_limit = 2 * 1024 * 1024 * 1024  # 2GB

        # If file is too large, try to redownload at lower quality
        if file_size > tg_limit:
            try:
                os.remove(filename)
            except Exception:
                pass
            # Try to get a lower quality format under 2GB
            # Use yt_dlp to get available formats
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                meta = ydl.extract_info(url, download=False)
                formats = meta.get("formats", [])
                # Sort by filesize (ascending), filter mp4 and video only
                candidates = [
                    f for f in formats
                    if f.get("ext") == "mp4" and f.get("filesize") and f.get("vcodec") != "none"
                ]
                candidates = sorted(candidates, key=lambda x: x["filesize"])
                found = False
                for fmt in candidates:
                    if fmt["filesize"] <= tg_limit:
                        ydl_opts_low = ydl_opts.copy()
                        ydl_opts_low["format"] = fmt["format_id"]
                        try:
                            filename = await loop.run_in_executor(None, run_yt, ydl_opts_low)
                            file_size = os.path.getsize(filename)
                            if file_size <= tg_limit:
                                found = True
                                break
                            else:
                                os.remove(filename)
                        except Exception:
                            continue
                if not found:
                    # Provide a download link if file is too large for Telegram
                    video_url = info.get("webpage_url", url)
                    await processing_msg.edit_text(
                        "❌ Could not find a video quality under 2GB to send via Telegram.\n"
                        f"🔗 <b>You can download it directly here:</b> <a href=\"{html.escape(video_url)}\">{html.escape(video_url)}</a>",
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                    return

        # Send the video
        caption = info.get("title", "YouTube Video")
        try:
            with open(filename, "rb") as f:
                try:
                    await update.message.reply_video(
                        video=f,
                        caption=f"🎬 <b>{html.escape(caption)}</b>",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    if "413" in str(e) or "Request Entity Too Large" in str(e):
                        video_url = info.get("webpage_url", url)
                        await processing_msg.edit_text(
                            "❌ Failed to upload video: The file is too large for Telegram (limit is 2GB for bots).\n"
                            f"🔗 <b>You can download it directly here:</b> <a href=\"{html.escape(video_url)}\">{html.escape(video_url)}</a>",
                            parse_mode="HTML",
                            disable_web_page_preview=True
                        )
                    else:
                        await processing_msg.edit_text(f"❌ Failed to upload video: <code>{html.escape(str(e))}</code>", parse_mode="HTML")
                    return
        finally:
            try:
                os.remove(filename)
            except Exception:
                pass

        await processing_msg.delete()
        try:
            await update.message.delete()
        except Exception:
            pass
    except Exception as e:
        logging.error(f"download_video error: {e}")


async def download_instagram(update: Update, _: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return
        text = update.message.text.strip()
        # Check if the message contains an Instagram link
        insta_regex = r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/[^\s]+"
        match = re.search(insta_regex, text)
        if not match:
            return  # Ignore non-Instagram links/messages

        url = match.group(0)
        # Remove query parameters for yt_dlp compatibility
        url = url.split("?")[0]

        processing_msg = await update.message.reply_text("⬇️ Downloading Instagram media, please wait...")

        # Use yt_dlp to download Instagram media
        # Load cookies from a file if available (export cookies from your browser as 'instagram_cookies.txt')
        cookies_file = "instacookies.txt"
        ydl_opts = {
            "format": "best",
            "outtmpl": "insta_media.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "merge_output_format": None,
        }
        if not os.path.exists(cookies_file):
            await update.message.reply_text(
                "❌ Instagram requires authentication to download media. Please export your Instagram cookies from your browser and save them as <b>instagram_cookies.txt</b> in the bot's directory.\n\n"
                "See: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp",
                parse_mode="HTML"
            )
            return
        ydl_opts["cookiefile"] = cookies_file
        loop = asyncio.get_running_loop()
        info = {}

        def run_yt(opts):
            with yt_dlp.YoutubeDL(opts) as ydl:
                info.update(ydl.extract_info(url, download=True))
                return ydl.prepare_filename(info)

        try:
            filename = await loop.run_in_executor(None, run_yt, ydl_opts)
        except Exception as e:
            err_str = str(e)
            await processing_msg.edit_text(f"❌ Failed to download Instagram media: <code>{html.escape(err_str)}</code>", parse_mode="HTML")
            return

        # Check file size before sending (Telegram limit is 2GB for bots)
        file_size = os.path.getsize(filename)
        tg_limit = 2 * 1024 * 1024 * 1024  # 2GB

        if file_size > tg_limit:
            try:
                os.remove(filename)
            except Exception:
                pass
            media_url = info.get("webpage_url", url)
            await processing_msg.edit_text(
                "❌ The file is too large for Telegram (limit is 2GB for bots).\n"
                f"🔗 <b>You can download it directly here:</b> <a href=\"{html.escape(media_url)}\">{html.escape(media_url)}</a>",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return

        caption = info.get("title", "Instagram Media")
        try:
            with open(filename, "rb") as f:
                if info.get("ext") in ["mp4", "webm"]:
                    await update.message.reply_video(
                        video=f,
                        caption=f"📸 <b>{html.escape(caption)}</b>",
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_photo(
                        photo=f,
                        caption=f"📸 <b>{html.escape(caption)}</b>",
                        parse_mode="HTML"
                    )
        finally:
            try:
                os.remove(filename)
            except Exception:
                pass

        await processing_msg.delete()
        try:
            await update.message.delete()
        except Exception:
            pass
    except Exception as e:
        logging.error(f"download_instagram error: {e}")

import math
import time

SAFE_NAMES = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
SAFE_NAMES.update({"abs": abs, "round": round})

def safe_eval(expr):
    try:
        return eval(expr, {"__builtins__": {}}, SAFE_NAMES)
    except Exception as e:
        return f"Error: {e}"

async def calculator_handler(update, context):
    text = update.message.text.strip()
    # Only allow digits, math ops, parentheses, decimal, and spaces
    if not re.match(r"^[\d\s\.\+\-\*\/\%\(\)\^,]+$", text):
        return  # Ignore non-math messages
    # Replace ^ with ** for exponentiation
    expr = text.replace("^", "**")
    result = safe_eval(expr)
    await update.message.reply_text(f"🧮 <b>Result:</b> <code>{result}</code>", parse_mode="HTML")
import sqlite3
from telegram import Update, Message, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
import logging
import asyncio
from datetime import datetime

# Database setup with datetime handling for Python 3.12+
def init_db():
    conn = sqlite3.connect('bot_database.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Register datetime adapter
    sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
    sqlite3.register_converter("TIMESTAMP", lambda dt: datetime.fromisoformat(dt.decode()))

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        chat_id INTEGER PRIMARY KEY,
        title TEXT,
        last_active TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        last_active TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

init_db()
AUTHORIZED_USERS = [7775049190]  # Replace with your admin user IDs
BROADCAST_DELAY = 0.5  # Delay between messages in seconds to avoid rate limiting
MAX_FAILED_DISPLAY = 5  # Max failed chats to display in report

class DatabaseManager:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect('bot_database.db', detect_types=sqlite3.PARSE_DECLTYPES)
        return conn

    @staticmethod
    def add_group(chat_id, title=None):
        conn = DatabaseManager.get_connection()
        try:
            conn.execute('''
            INSERT OR REPLACE INTO groups (chat_id, title, last_active)
            VALUES (?, ?, ?)
            ''', (chat_id, title, datetime.now()))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def add_user(user_id, username=None, first_name=None, last_name=None):
        conn = DatabaseManager.get_connection()
        try:
            conn.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, datetime.now()))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_all_groups():
        conn = DatabaseManager.get_connection()
        try:
            return [row[0] for row in conn.execute('SELECT chat_id FROM groups')]
        finally:
            conn.close()

    @staticmethod
    def get_all_users():
        conn = DatabaseManager.get_connection()
        try:
            return [row[0] for row in conn.execute('SELECT user_id FROM users')]
        finally:
            conn.close()

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track chats and users in the database"""
    if not update.message:
        return

    if update.message.chat.type in ['group', 'supergroup']:
        DatabaseManager.add_group(
            update.message.chat.id,
            update.message.chat.title
        )

    if update.message.from_user:
        DatabaseManager.add_user(
            update.message.from_user.id,
            update.message.from_user.username,
            update.message.from_user.first_name,
            update.message.from_user.last_name
        )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the broadcast command with interactive buttons"""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    # Get the message to broadcast
    if update.message.reply_to_message:
        message_to_broadcast = update.message.reply_to_message
        original_sender = message_to_broadcast.forward_from or message_to_broadcast.from_user
    elif context.args:
        message_to_broadcast = ' '.join(context.args)
        original_sender = update.effective_user
    else:
        await update.message.reply_text(
            "ℹ️ Usage:\n/bcast <message>\nor reply to a message with /bcast",
            reply_to_message_id=update.message.message_id
        )
        return

    # Get destinations and verify
    destinations = list(set(DatabaseManager.get_all_groups() + DatabaseManager.get_all_users()))
    if not destinations:
        await update.message.reply_text("❌ No destinations found in database.")
        return

    # Create confirmation buttons
    keyboard = [
        [InlineKeyboardButton("✅ Confirm Broadcast", callback_data='confirm_bcast')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_bcast')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store broadcast data
    context.user_data['pending_broadcast'] = {
        'message': message_to_broadcast,
        'sender': original_sender,
        'destinations': destinations,
        'original_message_id': update.message.message_id
    }

    # Generate preview text
    preview_text = ""
    if isinstance(message_to_broadcast, Message):
        preview_text = message_to_broadcast.text or message_to_broadcast.caption or "[Media message]"
    else:
        preview_text = message_to_broadcast

    preview_text = (preview_text[:200] + '...') if len(preview_text) > 200 else preview_text

    # Send confirmation with buttons
    await update.message.reply_text(
        f"⚠️ Confirm broadcast to {len(destinations)} chats?\n\n"
        f"Message preview:\n\n{preview_text}",
        reply_markup=reply_markup,
        reply_to_message_id=update.message.message_id
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks for broadcast confirmation"""
    query = update.callback_query
    await query.answer()

    if query.data == 'confirm_bcast':
        await confirm_broadcast(update, context)
    elif query.data == 'cancel_bcast':
        await cancel_broadcast(update, context)

async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute the broadcast to all destinations"""
    query = update.callback_query
    broadcast_data = context.user_data.get('pending_broadcast')

    if not broadcast_data:
        await query.edit_message_text("❌ No pending broadcast found.")
        return

    message_to_broadcast = broadcast_data['message']
    destinations = broadcast_data['destinations']

    # Update status message
    status_msg = await query.edit_message_text(
        f"📢 Broadcasting to {len(destinations)} chats...\n\n"
        "0% complete (0 sent)"
    )

    total_sent = 0
    failed_chats = []

    # Broadcast to all destinations
    for i, chat_id in enumerate(destinations):
        try:
            if isinstance(message_to_broadcast, Message):
                # Forward the original message with sender info
                await message_to_broadcast.forward(chat_id=chat_id)

                # Handle media with captions
                if message_to_broadcast.caption and message_to_broadcast.effective_attachment:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message_to_broadcast.caption,
                        reply_to_message_id=message_to_broadcast.message_id
                    )
            else:
                # Send text message
                await context.bot.send_message(chat_id=chat_id, text=message_to_broadcast)

            total_sent += 1

            # Update progress periodically
            if (i + 1) % 10 == 0 or (i + 1) == len(destinations):
                percent = int((i + 1) / len(destinations) * 100)
                await status_msg.edit_text(
                    f"📢 Broadcasting to {len(destinations)} chats...\n\n"
                    f"{percent}% complete ({i + 1} sent)\n"
                    f"✅ Success: {total_sent}\n"
                    f"❌ Failed: {len(failed_chats)}"
                )

            await asyncio.sleep(BROADCAST_DELAY)

        except Exception as e:
            failed_chats.append(str(chat_id))
            logger.error(f"Failed to send to {chat_id}: {e}")

    # Generate final report
    report = (
        f"✅ Broadcast completed!\n\n"
        f"📊 Stats:\n"
        f"• Total destinations: {len(destinations)}\n"
        f"• Successfully sent: {total_sent}\n"
        f"• Failed to send: {len(failed_chats)}"
    )

    if failed_chats:
        report += f"\n\nFailed chats (first {MAX_FAILED_DISPLAY}):\n" + "\n".join(failed_chats[:MAX_FAILED_DISPLAY])
        if len(failed_chats) > MAX_FAILED_DISPLAY:
            report += f"\n(and {len(failed_chats)-MAX_FAILED_DISPLAY} more)"

    await status_msg.edit_text(report)
    del context.user_data['pending_broadcast']

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the pending broadcast"""
    query = update.callback_query
    await query.answer()

    if 'pending_broadcast' in context.user_data:
        original_message_id = context.user_data['pending_broadcast'].get('original_message_id')
        del context.user_data['pending_broadcast']

    await query.edit_message_text("❌ Broadcast canceled.")


# Yoruichi-themed assets


DATA_FILE = "bot_data.pkl"

def save_all_data():
    try:
        data = {
            "warns": {k: dict(v) for k, v in warns.items()},
            "flood_settings": dict(flood_settings),
            "user_flood_data": {k: dict(v) for k, v in user_flood_data.items()},
            "antiraid_settings": dict(antiraid_settings),
            "blocklists": dict(blocklists),
            "locks": dict(locks),
            "lockwarns_enabled": dict(lockwarns_enabled),
            "allowlists": dict(allowlists),
            "greetings_settings": dict(greetings_settings),
            "rules_settings": dict(rules_settings),
            "stats_data": {
                "groups": set(stats_data["groups"]),
                "users": set(stats_data["users"]),
            },
            "sudo_users": {
                "lord": sudo_users["lord"],
                "substitute_lords": set(sudo_users.get("substitute_lords", set())),
                "descendants": set(sudo_users.get("descendants", set())),
            },
            "global_bans": set(global_bans),
            "global_mutes": set(global_mutes),
            "afk_status": dict(afk_status),
            "sg_userdata": dict(sg_userdata),
            "sg_enabled": dict(sg_enabled),
            "couple_storage": {k: dict(v) for k, v in couple_storage.items()},
        }
        with open(DATA_FILE, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        logging.error(f"save_all_data error: {e}")

def load_all_data():
    try:
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
        warns.clear()
        warns.update({k: defaultdict(int, v) for k, v in data.get("warns", {}).items()})
        flood_settings.clear()
        flood_settings.update(data.get("flood_settings", {}))
        user_flood_data.clear()
        user_flood_data.update({k: defaultdict(lambda: {"count": 0, "last_time": None, "timer_msgs": []}, v) for k, v in data.get("user_flood_data", {}).items()})
        antiraid_settings.clear()
        antiraid_settings.update(data.get("antiraid_settings", {}))
        blocklists.clear()
        blocklists.update(data.get("blocklists", {}))
        locks.clear()
        locks.update(data.get("locks", {}))
        lockwarns_enabled.clear()
        lockwarns_enabled.update(data.get("lockwarns_enabled", {}))
        allowlists.clear()
        allowlists.update(data.get("allowlists", {}))
        greetings_settings.clear()
        greetings_settings.update(data.get("greetings_settings", {}))
        rules_settings.clear()
        rules_settings.update(data.get("rules_settings", {}))
        stats_data["groups"].clear()
        stats_data["groups"].update(data.get("stats_data", {}).get("groups", set()))
        stats_data["users"].clear()
        stats_data["users"].update(data.get("stats_data", {}).get("users", set()))
        su = data.get("sudo_users", {})
        sudo_users["lord"] = su.get("lord", sudo_users["lord"])
        sudo_users["substitute_lords"] = set(su.get("substitute_lords", set()))
        sudo_users["descendants"] = set(su.get("descendants", set()))
        global_bans.clear()
        global_bans.update(data.get("global_bans", set()))
        global_mutes.clear()
        global_mutes.update(data.get("global_mutes", set()))
        afk_status.clear()
        afk_status.update(data.get("afk_status", {}))
        sg_userdata.clear()
        sg_userdata.update(data.get("sg_userdata", {}))
        sg_enabled.clear()
        sg_enabled.update(data.get("sg_enabled", {}))
        couple_storage.clear()
        couple_storage.update({k: dict(v) for k, v in data.get("couple_storage", {}).items()})
    except FileNotFoundError:
        pass
    except Exception as e:
        logging.error(f"load_all_data error: {e}")

# Load data at startup
load_all_data()

def save_on_exit(*_):
    save_all_data()
    sys.exit(0)

signal.signal(signal.SIGINT, save_on_exit)
signal.signal(signal.SIGTERM, save_on_exit)

# Optionally, save data periodically (every 5 minutes)
async def periodic_save_task():
    while True:
        await asyncio.sleep(300)
        save_all_data()
# NOTE: Do not call asyncio.create_task here; instead, start it after the event loop is running (see below).

async def main_text_handler(update, context):
    text = update.message.text.strip()
    # 1. Blocklist check
    await blocklist_message_handler(update, context)
    # 2. Calculation check
    if re.match(r"^[\d\s\.\+\-\*\/\%\(\)\^,]+$", text):
        expr = text.replace("^", "**")
        result = safe_eval(expr)
        await update.message.reply_text(f"🧮 <b>Result:</b> <code>{result}</code>", parse_mode="HTML")
        return
    # 3. Handle links (YouTube/Instagram)
    await handle_links(update, context)
    # 4. Other handlers as needed...

# Register only this handler for text
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only the Lord can broadcast
    if update.effective_user.id != sudo_users["lord"]:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    message_to_broadcast = update.message.reply_to_message
    if message_to_broadcast is None:
        await update.message.reply_text("Please reply to a message to broadcast.")
        return

    # Gather all known groups and users
    all_chats = list(stats_data["groups"])
    all_users = list(stats_data["users"])
    targets = set(all_chats + all_users)

    failed_sends = 0
    sent = 0

    for chat_id in targets:
        try:
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=message_to_broadcast.chat_id,
                message_id=message_to_broadcast.message_id
            )
            sent += 1
        except Exception as e:
            # Optionally log: print(f"Failed to send message to {chat_id}: {e}")
            failed_sends += 1

    await update.message.reply_text(
        f"Broadcast complete.\n"
        f"Sent to {sent} chats/users.\n"
        f"Failed to send to {failed_sends} chats/users."
    )


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Start periodic save task after the event loop is running
    async def on_startup(app):
        asyncio.create_task(periodic_save_task())
        asyncio.create_task(antiraid_cleanup_task(app))

    app.post_init = on_startup

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(help_callback_handler, pattern="^help_"))
    app.add_handler(CommandHandler("ff", ff_command))
    app.add_handler(CallbackQueryHandler(refresh_ff_callback, pattern=r"^refresh_ff_\d+_\w+$"))
    app.add_handler(CommandHandler("mmf", mmf))
    app.add_handler(MessageHandler(filters.PHOTO & filters.COMMAND, mmf))
    app.add_handler(CommandHandler(["q", "r"], quote_command))
    # Moderation
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("tban", tban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("warns", warns_command))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("tmute", tmute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("id", id_command))

    # Promotion/Demotion/Admin
    app.add_handler(CommandHandler("lowpromote", lowpromote))
    app.add_handler(CommandHandler("midpromote", midpromote))
    app.add_handler(CommandHandler("fullpromote", fullpromote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("adminlist", adminlist))
    app.add_handler(CommandHandler("admincache", admincache))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_text_handler))
    # Dummy handlers for anonadmin and adminerror (not implemented)
    async def anonadmin(update, context):
        await update.message.reply_text("This feature is not implemented.", parse_mode="HTML")
    async def adminerror(update, context):
        await update.message.reply_text("This feature is not implemented.", parse_mode="HTML")

    app.add_handler(CommandHandler("anonadmin", anonadmin))
    app.add_handler(CommandHandler("adminerror", adminerror))
    app.add_handler(CommandHandler("checkrights", check_rights))

    # Pinning
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))
    app.add_handler(CommandHandler("tpin", tpin))

    # search
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("search", bingsearch_command))
    app.add_handler(CommandHandler("searchimg", bingimg_command))
    app.add_handler(CommandHandler("sauce", googleimg_command))
    async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text if update.message else ""
        yt_regex = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+"
        insta_regex = r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/[^\s]+"
        if re.search(yt_regex, text):
            await download_video(update, context)
        elif re.search(insta_regex, text):
            await download_instagram(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links))

    # Antiraid
    app.add_handler(CommandHandler("antiraid", antiraid_command))
    app.add_handler(CommandHandler("raidtime", raidtime_command))
    app.add_handler(CommandHandler("raidactiontime", raidactiontime_command))
    app.add_handler(CommandHandler("autoantiraid", autoantiraid_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, antiraid_join_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
 # Blocklist
    app.add_handler(CommandHandler("addblocklist", addblocklist))
    app.add_handler(CommandHandler("rmblocklist", rmblocklist))
    app.add_handler(CommandHandler("unblocklistall", unblocklistall))
    app.add_handler(CommandHandler("blocklist" "blacklist", blocklist))
    app.add_handler(CommandHandler("blocklistmode", blocklistmode))
    app.add_handler(CommandHandler("blocklistdelete", blocklistdelete))
    app.add_handler(CommandHandler("setblocklistreason", setblocklistreason))
    app.add_handler(CommandHandler("resetblocklistreason", resetblocklistreason))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, blocklist_message_handler), group=0)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_handler))
    # Locks/Allowlist
    app.add_handler(CommandHandler("lock", lock_command))
    app.add_handler(CommandHandler("unlock", unlock_command))
    app.add_handler(CommandHandler("locks", locks_command))
    app.add_handler(CommandHandler("lockwarns", lockwarns_command))
    app.add_handler(CommandHandler("locktypes", locktypes_command))
    app.add_handler(CommandHandler("allowlist", allowlist_command))
    app.add_handler(CommandHandler("rmallowlist", rmallowlist_command))
    app.add_handler(CommandHandler("rmallowlistall", rmallowlistall_command))
    app.add_handler(MessageHandler(filters.ALL, locks_message_handler), group=4)

    # Blacklist stickers
    app.add_handler(CommandHandler("blackliststicker", blackliststicker))
    app.add_handler(CommandHandler("addblackliststicker", add_blackliststicker))
    app.add_handler(CommandHandler("unblackliststicker", unblackliststicker))
    app.add_handler(CommandHandler("blackliststickermode", blackliststickermode))
    app.add_handler(MessageHandler(filters.Sticker.ALL, blackliststicker_message_handler), group=8)

    # Greetings
    app.add_handler(CommandHandler("welcome", welcome_command))
    app.add_handler(CommandHandler("goodbye", goodbye_command))
    app.add_handler(CommandHandler("setwelcome", setwelcome_command))
    app.add_handler(CommandHandler("resetwelcome", resetwelcome_command))
    app.add_handler(CommandHandler("setgoodbye", setgoodbye_command))
    app.add_handler(CommandHandler("resetgoodbye", resetgoodbye_command))
    app.add_handler(CommandHandler("cleanwelcome", cleanwelcome_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))

    # Rules
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CallbackQueryHandler(show_rules_callback, pattern="^show_rules$"))
    app.add_handler(CommandHandler("setrules", setrules_command))
    app.add_handler(CommandHandler("privaterules", privaterules_command))
    app.add_handler(CommandHandler("resetrules", resetrules_command))
    app.add_handler(CommandHandler("setrulesbutton", setrulesbutton_command))
    app.add_handler(CommandHandler("resetrulesbutton", resetrulesbutton_command))

    # AFK
    app.add_handler(CommandHandler("afk", afk_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, afk_message_handler), group=1)

    # Stats
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.ALL, stats_track_handler), group=2)

    # Sudo/Global
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("rmsudo", rmsudo))
    app.add_handler(CommandHandler("sudousers", sudousers))
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("ungban", ungban))
    app.add_handler(CommandHandler("gmute", gmute))
    app.add_handler(CommandHandler("ungmute", ungmute))
    app.add_handler(MessageHandler(filters.ALL, global_enforcement_handler), group=3)

    # Banall/Unbanall
    app.add_handler(CommandHandler("banall", banall))
    app.add_handler(CallbackQueryHandler(banall_confirm_callback, pattern="^banall_confirm$"))
    app.add_handler(CallbackQueryHandler(banall_cancel_callback, pattern="^banall_cancel$"))
    app.add_handler(CommandHandler("unbanall", unbanall))

    # Lord group control
    app.add_handler(CommandHandler("lgc", lgc))

    # Games: XO (Tic-Tac-Toe)
    app.add_handler(CommandHandler("xo", xo_start))
    app.add_handler(CommandHandler("joinxo", join_xo))
    app.add_handler(CommandHandler("cancelxo", cancel_xo))
    app.add_handler(CallbackQueryHandler(xo_button_handler, pattern="^xo_move:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xo_players_response), group=7)
    # Truth or Dare game handlers
    app.add_handler(CommandHandler(["truthdare", "truth_or_dare", "tod"], truthdare_command))
    app.add_handler(CallbackQueryHandler(truthdare_button_handler, pattern="^truthdare:"))
    app.add_handler(CommandHandler("truth", truth_command))
    app.add_handler(CommandHandler("dare", dare_command))
    # Games: Rock Paper Scissors
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("joinrps", joinrps))
    app.add_handler(CallbackQueryHandler(rps_button_handler, pattern="^rps_choice:"))
    app.add_handler(CommandHandler("cancelrps", cancelrps))

    # Games: Connect 4
    app.add_handler(CommandHandler("connect4", connect4_start))
    app.add_handler(CallbackQueryHandler(connect4_players_callback, pattern="^c4_players:"))
    app.add_handler(CommandHandler("joinc4", join_connect4))
    app.add_handler(CallbackQueryHandler(connect4_button_handler, pattern="^c4_move:"))
    app.add_handler(CommandHandler("cancelc4", cancel_connect4))

    # Games: Explain & Guess (Taboo)
    app.add_handler(CommandHandler("wordgame" , explainword_start))
    app.add_handler(CommandHandler("cancelwordgame" ,explainword_cancel))
    app.add_handler(CallbackQueryHandler(explainword_button_handler, pattern="^explain_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, explainword_guess), group=9)
    app.add_handler(CommandHandler("wordboard" , explain_leaderboard_command))

    # Games: Chess
    app.add_handler(CommandHandler("chess", chess_start))
    app.add_handler(CommandHandler("joinchess", join_chess))
    app.add_handler(CommandHandler("cancelchess", cancel_chess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chess_move_handler), group=6)

    # Couple of the day
    app.add_handler(CommandHandler(["couple", "couples", "shipping"], couple_command))

    # Q command (quote to sticker)

    # Upscale image
    app.add_handler(CommandHandler("upscale", upscale_command))

    # Speedtest
    app.add_handler(CommandHandler("speedtest", speedtest_command))

    # Sudo join announce
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, sudo_join_announce))

    # Wish reply (good morning/night)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, wish_reply_handler), group=5)

    # Sangmata (sg) username history
    app.add_handler(CommandHandler("sg", sg_command))
    app.add_handler(MessageHandler(filters.ALL, sg_message_handler), group=0)
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("bcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, track_chats))

    # Logging, bot-added, and antiraid cleanup already handled above

    app.run_polling()
