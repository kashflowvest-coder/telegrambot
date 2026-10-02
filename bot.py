import asyncio
import logging
import sys
from datetime import datetime

# Ensure proper Unicode/emoji handling on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import TELEGRAM_BOT_TOKEN, CHECK_INTERVAL_SECONDS, MONITOR_CHANNEL_ID
from database import init_db, get_user_language
from i18n import t
from bot_handlers import (
    handle_start,
    handle_signal_command,
    handle_portfolio_command,
    handle_positions_command,
    handle_admin_command,
    handle_callback_query,
    handle_verify_command,
    handle_otp_command,
    handle_deposit_command,
    handle_setwallet_command,
    handle_verifyuser_command,
    handle_language_command,
    handle_text_message,
    handle_withdraw_command,
    handle_help_command
)
from trading_engine import check_and_update_positions, execute_auto_trading_cycle

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("AITradingBot")


async def position_monitor_worker(application):
    """
    Background worker that continuously monitors open positions for SL/TP triggers
    and scans markets for automated trade executions with bilingual user notifications.
    """
    logger.info("Position monitoring & Auto-Trading background worker started.")
    auto_cycle_counter = 0

    while True:
        try:
            # 1. Check Take Profit and Stop Loss triggers on open positions
            closed_events = check_and_update_positions()
            for ev in closed_events:
                user_id = ev.get("user_id")
                if user_id:
                    user_lang = get_user_language(user_id)
                    status_name = t("alert_tp_title", user_lang) if ev["status"] == "CLOSED_TP" else t("alert_sl_title", user_lang)
                    pnl_emoji = "🟢" if ev["pnl"] >= 0 else "🔴"
                    alert_msg = t(
                        "alert_trade_header", user_lang,
                        status=status_name,
                        symbol=ev['symbol'],
                        side=ev['side'],
                        entry=ev['entry_price'],
                        exit=ev['exit_price'],
                        badge=pnl_emoji,
                        pnl=ev['pnl'],
                        pct=ev['pnl_percent']
                    )
                    try:
                        await application.bot.send_message(
                            chat_id=user_id,
                            text=alert_msg,
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        logger.warning(f"Could not deliver notification to user {user_id}: {e}")

            # 2. Run automated AI trading scanner every 4 intervals (~60 seconds)
            auto_cycle_counter += 1
            if auto_cycle_counter >= 4:
                auto_cycle_counter = 0
                opened_trades = execute_auto_trading_cycle()
                for trade in opened_trades:
                    user_id = trade.get("user_id")
                    if user_id:
                        user_lang = get_user_language(user_id)
                        notif = t(
                            "alert_autotrade_header", user_lang,
                            symbol=trade['symbol'],
                            side=trade['side'],
                            entry=trade['entry_price'],
                            conf=trade.get('confidence', 75),
                            tp=trade['take_profit'],
                            sl=trade['stop_loss']
                        )
                        try:
                            await application.bot.send_message(
                                chat_id=user_id,
                                text=notif,
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.warning(f"Could not deliver auto-trade notification: {e}")

        except Exception as e:
            logger.error(f"Error in background monitor cycle: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


def main():
    """Main application launcher."""
    # Ensure database tables exist
    init_db()

    # Validate bot token
    if not TELEGRAM_BOT_TOKEN or "your_telegram_bot_token" in TELEGRAM_BOT_TOKEN:
        print("\n" + "=" * 70)
        print("⚠️  TELEGRAM_BOT_TOKEN IS NOT CONFIGURED YET!")
        print("=" * 70)
        print("To connect your Telegram bot:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot and choose a name & username (e.g. MyAITradingBot)")
        print("3. Copy the HTTP API token BotFather gives you")
        print("4. Paste your token into the .env file:")
        print("   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
        print("\n💡 In the meantime, you can test the entire trading engine,")
        print("   live price feeds, AI signals, and paper trading without Telegram by running:")
        print("   py simulate_demo.py")
        print("=" * 70 + "\n")
        sys.exit(1)

    try:
        from telegram.ext import (
            ApplicationBuilder,
            CommandHandler,
            CallbackQueryHandler,
            MessageHandler,
            filters
        )
    except ImportError:
        print("Error: python-telegram-bot is not installed. Run: py -m pip install -r requirements.txt")
        sys.exit(1)

    # Build Telegram Bot application with generous timeouts for unstable connections
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Register Command Handlers
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("help", handle_help_command))
    app.add_handler(CommandHandler("signal", handle_signal_command))
    app.add_handler(CommandHandler("signals", handle_signal_command))
    app.add_handler(CommandHandler("portfolio", handle_portfolio_command))
    app.add_handler(CommandHandler("positions", handle_positions_command))
    app.add_handler(CommandHandler("admin", handle_admin_command))
    app.add_handler(CommandHandler("verify", handle_verify_command))
    app.add_handler(CommandHandler("otp", handle_otp_command))
    app.add_handler(CommandHandler("deposit", handle_deposit_command))
    app.add_handler(CommandHandler("withdraw", handle_withdraw_command))
    app.add_handler(CommandHandler("setwallet", handle_setwallet_command))
    app.add_handler(CommandHandler("setaddress", handle_setwallet_command))
    app.add_handler(CommandHandler("verifyuser", handle_verifyuser_command))
    app.add_handler(CommandHandler("lang", handle_language_command))
    app.add_handler(CommandHandler("language", handle_language_command))

    # Register Interactive Callback Query Handler
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Register Custom Reply Keyboard / Text Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Background task hook
    async def post_init(application):
        asyncio.create_task(position_monitor_worker(application))
        # Initialize Telegram channel notifier if configured
        if MONITOR_CHANNEL_ID:
            try:
                import channel_notifier
                loop = asyncio.get_running_loop()
                channel_notifier.init_notifier(application.bot, MONITOR_CHANNEL_ID, loop)
                channel_notifier.start_drain_task()
                logger.info(f"[ChannelNotifier] Live alerts -> channel {MONITOR_CHANNEL_ID}")
            except Exception as e:
                logger.warning(f"[ChannelNotifier] Init failed: {e}")

    app.post_init = post_init

    print("\n🚀 AI Automated Trading Bot is starting up...")
    print(f"⏰ Server time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("🤖 Polling Telegram for incoming user commands...\n")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
