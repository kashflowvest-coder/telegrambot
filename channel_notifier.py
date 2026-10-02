"""
channel_notifier.py — Telegram Private Channel Alert System
============================================================
Sends formatted traffic alert messages to a private Telegram channel
whenever key user events occur (new client, deposit, withdrawal, etc.).

Setup:
1. Create a private Telegram channel
2. Add your bot as an Administrator with "Post Messages" permission
3. Get the channel's chat ID (use @userinfobot or forward a channel msg to it)
   Channel IDs always start with -100...  e.g. -1001234567890
4. Set MONITOR_CHANNEL_ID=-1001234567890 in your .env file
5. Restart the bot

The bot then silently pushes alerts to that channel in real-time.
"""

import asyncio
import logging
import threading
import queue as queue_module
from datetime import datetime

logger = logging.getLogger("ChannelNotifier")

# ─── Global bot reference (set once when bot starts) ──────────────────────────
_bot = None          # telegram.Bot instance
_channel_id = None   # int channel ID from config
_loop = None         # asyncio event loop the bot runs on

# Queue of messages to send (str)
_msg_queue: queue_module.Queue = queue_module.Queue()


def init_notifier(bot, channel_id, loop: asyncio.AbstractEventLoop):
    """
    Call this once after the Telegram Application is built.
    bot        — application.bot
    channel_id — integer chat ID or string channel handle (e.g. @alertsnotices)
    loop       — the running asyncio event loop
    """
    global _bot, _channel_id, _loop
    _bot = bot
    _channel_id = channel_id
    _loop = loop
    logger.info(f"[ChannelNotifier] Initialized. Sending alerts to channel {channel_id}")


def _enqueue(text: str):
    """Thread-safe: push a message onto the send queue."""
    _msg_queue.put_nowait(text)


async def _drain_queue():
    """Coroutine that drains the message queue and sends to channel."""
    while True:
        try:
            text = _msg_queue.get_nowait()
            try:
                await _bot.send_message(
                    chat_id=_channel_id,
                    text=text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.warning(f"[ChannelNotifier] Failed to send: {e}")
        except queue_module.Empty:
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"[ChannelNotifier] Drain error: {e}")
            await asyncio.sleep(1)


def start_drain_task():
    """Schedule the drain coroutine onto the bot's event loop."""
    if _loop and _bot and _channel_id:
        asyncio.run_coroutine_threadsafe(_drain_queue(), _loop)


# ─── Event formatters ─────────────────────────────────────────────────────────

def _user_line(data: dict) -> str:
    name = data.get("first_name") or data.get("username") or f"User {data.get('user_id','?')}"
    handle = f"@{data['username']}" if data.get("username") else f"<code>{data.get('user_id','?')}</code>"
    return f"<b>{name}</b> {handle}"


def _ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def notify_new_user(data: dict):
    text = (
        "🆕 <b>NEW CLIENT JOINED</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: {_user_line(data)}\n"
        f"🌐 Lang: <code>{data.get('lang','en').upper()}</code>\n"
        f"✅ Verified: {'Yes' if data.get('verified') else 'No'}\n"
        f"🕐 Time: <code>{_ts()}</code>"
    )
    _enqueue(text)


def notify_returning_user(data: dict):
    text = (
        "↩️ <b>Returning User</b>\n"
        f"👤 {_user_line(data)}\n"
        f"🕐 <code>{_ts()}</code>"
    )
    _enqueue(text)


def notify_deposit(data: dict):
    text = (
        "💰 <b>DEPOSIT REQUEST</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: {_user_line(data)}\n"
        f"📋 Detail: <code>{data.get('detail','')}</code>\n"
        f"🕐 Time: <code>{_ts()}</code>"
    )
    _enqueue(text)


def notify_withdraw(data: dict):
    text = (
        "🕊️ <b>WITHDRAWAL REQUEST</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: {_user_line(data)}\n"
        f"📋 Detail: <code>{data.get('detail','')}</code>\n"
        f"🕐 Time: <code>{_ts()}</code>"
    )
    _enqueue(text)


def notify_message(data: dict):
    """Only send message events if they look interesting (not every single tap)."""
    detail = data.get("detail", "")
    # Skip very common low-value taps to avoid spam
    skip_keywords = ["how it works", "about us", "faq", "live charts", "user reviews"]
    if any(k in detail.lower() for k in skip_keywords):
        return
    text = (
        f"💬 <b>User Action</b>\n"
        f"👤 {_user_line(data)}\n"
        f"📌 <code>{detail[:80]}</code>\n"
        f"🕐 <code>{_ts()}</code>"
    )
    _enqueue(text)


# ─── Main dispatch ─────────────────────────────────────────────────────────────

def dispatch(event_type: str, data: dict):
    """
    Called by activity_logger.push_event() for every bot event.
    Routes to the correct formatter based on event type.
    Only runs if notifier is properly initialized.
    """
    if not _bot or not _channel_id:
        return
    try:
        if event_type == "new_user":
            notify_new_user(data)
        elif event_type == "returning":
            notify_returning_user(data)
        elif event_type == "deposit":
            notify_deposit(data)
        elif event_type == "withdraw":
            notify_withdraw(data)
        elif event_type == "message":
            notify_message(data)
        # trade_open / trade_close can be added here if needed
    except Exception as e:
        logger.warning(f"[ChannelNotifier] dispatch error: {e}")
