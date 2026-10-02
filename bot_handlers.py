import os
from datetime import datetime
from typing import Dict, Any, Tuple, List
from activity_logger import push_event

from config import ADMIN_USER_IDS, DEFAULT_TIMEFRAME, SUPPORTED_PAIRS
from database import (
    get_or_create_user, get_user, update_user_settings, get_open_positions,
    get_position, get_portfolio_stats, get_admin_stats, get_all_users,
    set_crypto_wallet, get_crypto_wallets, get_crypto_wallet,
    create_deposit_request, get_deposit_request, get_pending_deposits,
    update_deposit_status, generate_user_otp, verify_user_otp,
    is_user_verified, admin_verify_user, get_user_language, set_user_language,
    verify_user, create_withdrawal_request, get_user_withdrawals, get_pending_withdrawals,
    update_withdrawal_status
)
from market_data import get_live_ticker, get_ohlcv
from ai_engine import get_ai_signal
from trading_engine import open_trade, close_trade
from bot_keyboards import (
    get_main_menu_keyboard, get_pairs_keyboard, get_signal_action_keyboard,
    get_quick_trade_amounts_keyboard, get_position_action_keyboard,
    get_settings_keyboard, get_admin_keyboard, get_deposit_wallets_keyboard,
    get_admin_wallets_keyboard, get_admin_deposit_approval_keyboard,
    get_otp_verification_keyboard, get_language_selection_keyboard,
    get_main_reply_keyboard, get_verification_inline_keyboard,
    get_quick_deposit_amounts_keyboard, get_deposit_crypto_selection_keyboard
)
from i18n import t, get_verdict_label, translate_reasons


def format_welcome_message(user: Dict[str, Any], lang: str = "en") -> str:
    """Format the welcome dashboard message with i18n support."""
    lang = user.get("language") or lang or "en"
    mode_raw = user.get("trading_mode", "paper").upper()
    mode = t("badge_paper", lang) if mode_raw == "PAPER" else t("badge_live", lang)
    auto_status = t("badge_active", lang) if user.get("is_auto_trading") else t("badge_paused", lang)
    bal = user.get("paper_balance", 0.0) if user.get("trading_mode") == "paper" else "Connected via API"
    bal_str = f"${bal:,.2f} USDT" if isinstance(bal, (int, float)) else str(bal)

    is_ver = bool(user.get("is_verified", 0)) or (user.get("user_id") in ADMIN_USER_IDS)
    ver_badge = t("badge_verified", lang) if is_ver else t("badge_unverified", lang)
    lang_badge = "🇵🇱 Polski" if lang.startswith("pl") else "🇬🇧 English"

    return (
        f"{t('welcome_title', lang)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t('welcome_greeting', lang, name=user.get('first_name', 'Trader'))}\n\n"
        f"{t('welcome_verification', lang, status=ver_badge)}\n"
        f"{t('welcome_mode', lang, mode=mode)}\n"
        f"{t('welcome_balance', lang, balance=bal_str)}\n"
        f"{t('welcome_auto', lang, status=auto_status)}\n"
        f"{t('welcome_risk', lang, risk=user.get('risk_percent', 2.0))}\n"
        f"{t('welcome_exchange', lang, exchange=user.get('exchange', 'Binance').upper())}\n"
        f"• *Language / Język:* `{lang_badge}`\n\n"
        f"{t('welcome_prompt', lang)}"
    )


def _confidence_bar(conf: float) -> str:
    """Generate a visual ASCII progress bar for confidence score."""
    filled = round(conf / 10)  # 0-10 blocks
    bar = "█" * filled + "░" * (10 - filled)
    return f"`[{bar}]` `{conf:.0f}%`"


def format_signal_message(signal: Dict[str, Any], lang: str = "en") -> str:
    """Format AI Signal analysis into a high-impact Telegram message with i18n."""
    if "error" in signal:
        return f"⚠️ *Error generating signal:* {signal['error']}"

    action = signal["action"]
    action_verdict = get_verdict_label(action, lang)

    # Dynamic header emoji based on action
    header_emoji = {"STRONG BUY": "🚀", "BUY": "📈", "NEUTRAL": "⚖️", "SELL": "📉", "STRONG SELL": "🔥"}
    hdr = header_emoji.get(action, "📊")

    p = signal["price"]
    tp1 = signal["target_tp1"]
    tp2 = signal["target_tp2"]
    sl = signal["stop_loss"]
    conf = signal["confidence"]
    ind = signal.get("indicators", {})
    squeeze = signal.get("squeeze", False)

    tp1_diff = ((tp1 - p) / p * 100) if p > 0 else 0
    tp2_diff = ((tp2 - p) / p * 100) if p > 0 else 0
    sl_diff = ((sl - p) / p * 100) if p > 0 else 0

    reasons = translate_reasons(signal.get("reasons", []), lang)
    reasons_text = "\n".join([f"  • {r}" for r in reasons])

    # RSI zone label
    rsi_val = ind.get('rsi', 50)
    if rsi_val < 30:
        rsi_label = "🟢 OVERSOLD"
    elif rsi_val > 70:
        rsi_label = "🔴 OVERBOUGHT"
    else:
        rsi_label = "⚪ NEUTRAL"

    # MACD direction
    macd_cross = ind.get('macd', {}).get('crossover', 'NEUTRAL')
    macd_label = "🟢 BULLISH" if macd_cross == "BULLISH" else "🔴 BEARISH"

    # Trend label
    trend_val = ind.get('trend', 'NEUTRAL')
    trend_label = "📈 BULLISH" if trend_val == "BULLISH" else ("📉 BEARISH" if trend_val == "BEARISH" else "↔️ NEUTRAL")

    squeeze_alert = "\n⚡ *SQUEEZE ALERT:* Bollinger Band compression detected — explosive breakout anticipated!" if squeeze else ""

    msg = (
        f"{hdr} *AI SIGNAL — {signal['symbol']}* `{signal['timeframe']}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *Verdict:* `{action_verdict}`\n"
        f"📊 *Confidence:* {_confidence_bar(conf)}\n"
        f"💰 *Entry Price:* `${p:,.4f}`{squeeze_alert}\n\n"
        f"🎯 *PRICE TARGETS*\n"
        f"  ✅ *TP1:* `${tp1:,.4f}` `({tp1_diff:+.2f}%)`\n"
        f"  ✅ *TP2:* `${tp2:,.4f}` `({tp2_diff:+.2f}%)`\n"
        f"  🛑 *Stop Loss:* `${sl:,.4f}` `({sl_diff:+.2f}%)`\n"
        f"  ⚖️ *Risk/Reward:* `{signal.get('risk_reward', '1:2.0')}`\n\n"
        f"🔬 *TECHNICAL INDICATORS*\n"
        f"  • *RSI (14):* `{rsi_val:.1f}` — {rsi_label}\n"
        f"  • *MACD:* {macd_label} `(hist: {ind.get('macd', {}).get('histogram', 0):.4f})`\n"
        f"  • *Trend (EMA Stack):* {trend_label}\n"
        f"  • *BB %B:* `{ind.get('bollinger', {}).get('percent_b', 0.5):.2f}` | *BW:* `{ind.get('bollinger', {}).get('bandwidth', 0):.2f}%`\n"
        f"  • *Volume Ratio:* `{ind.get('volume_ratio', 1.0):.2f}x` avg\n\n"
        f"📝 *AI RATIONALE*\n"
        f"{reasons_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t('signal_action_footer', lang)}"
    )

    if "llm_summary" in signal:
        msg += f"\n\n🤖 *Macro Insight:*\n_{signal['llm_summary']}_"

    return msg


def format_portfolio_message(user_id: int, lang: str = "en") -> str:
    """Format comprehensive portfolio statistics with i18n."""
    stats = get_portfolio_stats(user_id)
    if not stats:
        return "⚠️ User profile not found."

    mode_raw = stats["trading_mode"].upper()
    mode = t("badge_paper", lang) if mode_raw == "PAPER" else t("badge_live", lang)
    bal = stats["paper_balance"]
    win_rate = stats["win_rate"]
    pnl = stats["total_realized_pnl"]
    pnl_sign = "+" if pnl >= 0 else ""
    open_count = stats["open_positions_count"]
    closed_count = stats["closed_trades_count"]
    auto_status = t("badge_active", lang) if stats["is_auto_trading"] else t("badge_paused", lang)

    return (
        f"{t('portfolio_title', lang)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t('portfolio_mode', lang, mode=mode)}\n"
        f"{t('portfolio_balance', lang, bal=bal)}\n"
        f"{t('portfolio_exposure', lang, exp=stats['total_open_cost'])}\n"
        f"{t('portfolio_autotrade', lang, status=auto_status)}\n\n"
        f"{t('portfolio_perf_header', lang)}\n"
        f"{t('portfolio_realized_pnl', lang, sign=pnl_sign, pnl=pnl)}\n"
        f"{t('portfolio_win_rate', lang, wr=win_rate)}\n"
        f"{t('portfolio_closed_trades', lang, total=closed_count)}\n"
        f"{t('portfolio_wins_losses', lang, wins=stats['winning_trades'], losses=stats['losing_trades'])}\n"
        f"{t('portfolio_open_count', lang, count=open_count)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t('portfolio_footer', lang)}"
    )


def format_positions_message(user_id: int, lang: str = "en") -> Tuple[str, List[dict]]:
    """Format active open trades list and generate action buttons with i18n."""
    positions = get_open_positions(user_id)
    if not positions:
        return t("positions_none", lang), []

    lines = [t("positions_title", lang), "━━━━━━━━━━━━━━━━━━━━━━"]
    inline_buttons = []

    for pos in positions:
        ticker = get_live_ticker(pos["symbol"])
        curr_price = ticker["price"]

        if pos["side"] == "BUY":
            pnl = (curr_price - pos["entry_price"]) * pos["amount"]
        else:
            pnl = (pos["entry_price"] - curr_price) * pos["amount"]

        pnl_pct = (pnl / pos["cost"] * 100.0) if pos["cost"] > 0 else 0
        pnl_badge = "🟢" if pnl >= 0 else "🔴"

        lines.append(
            f"🔹 *#{pos['id']} {pos['symbol']}* ({pos['side']})\n"
            f"{t('pos_entry_now', lang, entry=pos['entry_price'], now=curr_price)}\n"
            f"{t('pos_size', lang, cost=pos['cost'], amount=pos['amount'])}\n"
            f"{t('pos_pnl', lang, badge=pnl_badge, pnl=pnl, pct=pnl_pct)}\n"
            f"{t('pos_tp_sl', lang, tp=pos['take_profit'], sl=pos['stop_loss'])}\n"
        )

        inline_buttons.append({
            "text": t("pos_close_btn", lang, pid=pos['id'], sym=pos['symbol'].split('/')[0], pnl=pnl),
            "callback_data": f"close_pos:{pos['id']}"
        })

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(t("positions_footer", lang))
    return "\n".join(lines), inline_buttons


def format_settings_message(user: Dict[str, Any], lang: str = "en") -> str:
    """Format settings menu message."""
    lang = user.get("language") or lang or "en"
    mode_raw = user.get("trading_mode", "paper").upper()
    mode = t("badge_paper", lang) if mode_raw == "PAPER" else t("badge_live", lang)
    lang_badge = "🇵🇱 Polski" if lang.startswith("pl") else "🇬🇧 English"

    prompt_line = "Wybierz opcję poniżej, aby zmienić ustawienia:" if lang.startswith("pl") else "Tap any option below to change settings:"

    return (
        f"{t('settings_title', lang)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t('settings_mode', lang, mode=mode)}\n"
        f"{t('settings_risk', lang, risk=user.get('risk_percent', 2.0))}\n"
        f"{t('settings_exchange', lang, exchange=user.get('exchange', 'Binance').upper())}\n"
        f"• *Paper Balance:* `${user.get('paper_balance', 10000.0):,.2f} USDT`\n"
        f"{t('settings_language', lang, lang=lang_badge)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{prompt_line}"
    )


# Telegram Bot Command Handlers
async def handle_start(update, context):
    """Handle /start command matching the exact user interface from screenshot."""
    u = update.effective_user
    user = get_or_create_user(u.id, u.username or "", u.first_name or "")
    lang = user.get("language", "en")
    is_admin = u.id in ADMIN_USER_IDS
    is_ver = bool(user.get("is_verified", 0)) or is_admin
    # --- Traffic Monitor: emit new/returning user event ---
    try:
        _is_new = user.get("created_at") == user.get("last_active")  # same timestamp → just created
        push_event(
            "new_user" if _is_new else "returning",
            {
                "user_id": u.id,
                "username": u.username or "",
                "first_name": u.first_name or "",
                "action": "/start",
                "detail": "New user registered" if _is_new else "Returning user",
                "verified": is_ver,
                "lang": lang,
            }
        )
    except Exception:
        pass

    banner_path = os.path.join(os.path.dirname(__file__), "assets", "ai_trading_robot_banner.jpg")
    reply_kb = get_main_reply_keyboard(lang, is_admin)

    if not is_ver:
        # User not verified yet: display high-tech cyborg robot banner + one-time verification button
        caption_text = (
            "🔐 *One-time Verification*\n"
            "Tap the button below to verify & activate your bot."
        )
        inline_kb = get_verification_inline_keyboard(lang)

        if os.path.exists(banner_path):
            try:
                with open(banner_path, "rb") as photo_file:
                    await update.message.reply_photo(
                        photo=photo_file,
                        caption=caption_text,
                        reply_markup=inline_kb,
                        parse_mode="Markdown"
                    )
            except Exception:
                await update.message.reply_text(
                    caption_text,
                    reply_markup=inline_kb,
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(
                caption_text,
                reply_markup=inline_kb,
                parse_mode="Markdown"
            )
    else:
        # User verified: Welcome back and activate the 7-row custom reply keyboard
        welcome_text = "Welcome back! Choose an option:" if not lang.startswith("pl") else "Witaj ponownie! Wybierz opcję:"
        if os.path.exists(banner_path):
            try:
                with open(banner_path, "rb") as photo_file:
                    await update.message.reply_photo(
                        photo=photo_file,
                        caption=welcome_text,
                        reply_markup=reply_kb,
                        parse_mode="Markdown"
                    )
            except Exception:
                await update.message.reply_text(welcome_text, reply_markup=reply_kb, parse_mode="Markdown")
        else:
            await update.message.reply_text(welcome_text, reply_markup=reply_kb, parse_mode="Markdown")


async def handle_signal_command(update, context):
    """Handle /signal or /signals command."""
    u = update.effective_user
    user = get_or_create_user(u.id, u.username or "", u.first_name or "")
    lang = user.get("language", "en")
    args = context.args

    if args:
        symbol = args[0].upper()
        if not symbol.endswith("/USDT"):
            symbol = f"{symbol}/USDT"
            
        # UI Polish: Temporary loading message
        loading_text = "🤖 *AI is analyzing real-time market data for* `{}`*...*" if not lang.startswith("pl") else "🤖 *AI analizuje dane rynkowe dla* `{}`*...*"
        temp_msg = await update.message.reply_text(loading_text.format(symbol), parse_mode="Markdown")
        
        candles = get_ohlcv(symbol, timeframe=DEFAULT_TIMEFRAME, limit=100)
        signal = get_ai_signal(symbol, DEFAULT_TIMEFRAME, candles)
        text = format_signal_message(signal, lang)
        keyboard = get_signal_action_keyboard(symbol, lang)
        
        # Replace loading message with final result
        try:
            await temp_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        text = t("signal_select_pair", lang)
        keyboard = get_pairs_keyboard("signal_pair", lang)
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_portfolio_command(update, context):
    """Handle /portfolio command."""
    u = update.effective_user
    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    text = format_portfolio_message(u.id, lang)
    is_admin = u.id in ADMIN_USER_IDS
    is_ver = bool(user.get("is_verified", 0)) or is_admin
    keyboard = get_main_menu_keyboard(
        bool(user.get("is_auto_trading")), user.get("trading_mode", "paper"), is_admin=is_admin, is_verified=is_ver, lang=lang
    )
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_positions_command(update, context):
    """Handle /positions command."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    u = update.effective_user
    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    text, buttons = format_positions_message(u.id, lang)

    kb = [[InlineKeyboardButton(b["text"], callback_data=b["callback_data"])] for b in buttons]
    kb.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu_main")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def handle_language_command(update, context):
    """Handle /lang or /language command."""
    u = update.effective_user
    args = context.args
    user = get_or_create_user(u.id, u.username or "", u.first_name or "")
    if args:
        target = args[0].lower().strip()
        new_lang = "pl" if target.startswith("pl") else "en"
        set_user_language(u.id, new_lang)
        user["language"] = new_lang
        ack = "🇵🇱 Język bota został zmieniony na *Polski*!" if new_lang == "pl" else "🇬🇧 Bot language successfully switched to *English*!"
        is_admin = u.id in ADMIN_USER_IDS
        is_ver = bool(user.get("is_verified", 0)) or is_admin
        keyboard = get_main_menu_keyboard(
            bool(user.get("is_auto_trading")), user.get("trading_mode", "paper"), is_admin=is_admin, is_verified=is_ver, lang=new_lang
        )
        await update.message.reply_text(ack, reply_markup=keyboard, parse_mode="Markdown")
    else:
        text = "🌐 *Select your preferred language / Wybierz preferowany język:*"
        await update.message.reply_text(text, reply_markup=get_language_selection_keyboard(), parse_mode="Markdown")



HELP_PAGES = {
    "en": [
        {
            "title": "📖 HOW TO USE THIS BOT — Welcome",
            "body": (
                "Welcome to the *AI Automated Trading Bot*! 🤖\n\n"
                "This bot lets you trade cryptocurrency using real AI-powered signals, "
                "manage your portfolio, and even run 24/7 automated trading.\n\n"
                "📌 *Key Features:*\n"
                "  • 🤖 Real-time AI trading signals across 10 pairs\n"
                "  • 💰 Deposit & Withdraw funds easily\n"
                "  • 📊 Live portfolio & P&L tracking\n"
                "  • 🧪 Paper trading for risk-free practice\n"
                "  • ⚡ Auto-trading with configurable risk levels\n\n"
                "Use the buttons below to continue the tutorial →"
            )
        },
        {
            "title": "💰 STEP 1 — Fund Your Account",
            "body": (
                "To start trading, first deposit funds into your account.\n\n"
                "1️⃣ Tap *💰 Deposit* in the main menu\n"
                "2️⃣ Choose your deposit amount\n"
                "3️⃣ Select your preferred cryptocurrency network:\n"
                "  • USDT TRC20, BEP20, ERC20\n"
                "  • Bitcoin (BTC)\n"
                "  • Solana (SOL)\n"
                "  • TON Network\n\n"
                "4️⃣ Send funds to the wallet address shown\n"
                "5️⃣ Submit your Transaction ID (TXID)\n"
                "6️⃣ Admin will approve within 1-24 hours\n\n"
                "💡 *Minimum deposit:* $100 USDT"
            )
        },
        {
            "title": "📊 STEP 2 — Read AI Signals",
            "body": (
                "The AI engine analyzes live market data using 6 indicators:\n\n"
                "  🔹 *RSI (14)* — Overbought/Oversold momentum\n"
                "  🔹 *MACD* — Trend crossover & histogram expansion\n"
                "  🔹 *EMA Stack (20/50/200)* — Macro trend alignment\n"
                "  🔹 *Bollinger Bands* — Volatility & squeeze detection\n"
                "  🔹 *Support/Resistance* — Key price levels\n"
                "  🔹 *Volume* — Institutional activity confirmation\n\n"
                "📌 *How to trade signals:*\n"
                "  1. Go to *AI Signals* → pick a trading pair\n"
                "  2. Review the signal: verdict, confidence %, TP & SL\n"
                "  3. Use *Quick Trade* to execute directly\n\n"
                "✅ Confidence above 75% is a high-conviction setup!"
            )
        },
        {
            "title": "🧪 STEP 3 — Paper vs Live Trading",
            "body": (
                "*Paper Trading (🧪 DEMO):*\n"
                "  • Uses simulated $10,000 balance\n"
                "  • No real money at risk\n"
                "  • Perfect for learning & testing strategies\n"
                "  • All signals and P&L are fully realistic\n\n"
                "*Live Trading (⚡ LIVE):*\n"
                "  • Trades execute with your real deposited balance\n"
                "  • Requires API keys for your exchange (Binance, Bybit, OKX)\n"
                "  • SL/TP automatically managed by the engine\n\n"
                "📌 *To switch modes:*\n"
                "  1. Tap ⚙️ Settings in the main menu\n"
                "  2. Tap *Switch to LIVE/PAPER Mode*"
            )
        },
        {
            "title": "🤖 STEP 4 — Auto-Trading",
            "body": (
                "When *Auto-Trading* is ON, the AI scans all 10 supported pairs "
                "every ~60 seconds and automatically opens positions when strong signals are detected.\n\n"
                "📌 *Setup Auto-Trading:*\n"
                "  1. Toggle *🤖 Auto: ACTIVE/PAUSED* in the main menu\n"
                "  2. Configure your risk % in ⚙️ Settings\n"
                "  3. The AI will handle entries and exits automatically\n\n"
                "⚠️ *Risk Management:*\n"
                "  • Default risk: 2% per trade\n"
                "  • Max 5 simultaneous open positions\n"
                "  • Automatic Stop Loss on every trade\n\n"
                "📢 You'll receive Telegram alerts for every auto-opened and auto-closed trade!\n\n"
                "🎉 *You're ready to trade! Tap Main Menu to get started.*"
            )
        }
    ]
}
HELP_PAGES["pl"] = HELP_PAGES["en"]  # Polish falls back to English for now


async def handle_help_command(update, context):
    """Display an interactive multi-page help tutorial."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    u = update.effective_user
    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    pages = HELP_PAGES.get(lang, HELP_PAGES["en"])
    page = pages[0]

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1 / 5", callback_data="noop"),
            InlineKeyboardButton("Next ▶", callback_data="help_page:1")
        ],
        [InlineKeyboardButton("❌ Close Tutorial", callback_data="menu_main")]
    ])

    await update.message.reply_text(
        f"*{page['title']}*\n━━━━━━━━━━━━━━━━━━━━━━\n{page['body']}",
        reply_markup=kb,
        parse_mode="Markdown"
    )


async def handle_verify_command(update, context):
    """Handle /verify command to generate and send OTP."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    u = update.effective_user
    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    otp = generate_user_otp(u.id)
    text = t("otp_title", lang, otp=otp)
    kb = [
        [InlineKeyboardButton(t("btn_otp_onetap", lang, otp=otp), callback_data=f"auto_verify:{otp}")],
        [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def handle_otp_command(update, context):
    """Handle /otp <code> verification."""
    u = update.effective_user
    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Usage / Użycie: `/otp 123456`", parse_mode="Markdown")
        return

    otp_input = args[0].strip()
    success = verify_user_otp(u.id, otp_input)
    if success:
        text = t("otp_success", lang)
        is_admin = u.id in ADMIN_USER_IDS
        reply_kb = get_main_reply_keyboard(lang, is_admin=is_admin)
        await update.message.reply_text("✅ Bot verified and activated!", reply_markup=reply_kb, parse_mode="Markdown")
    else:
        text = t("otp_invalid", lang)

    user = get_user(u.id) or {}
    is_admin = u.id in ADMIN_USER_IDS
    is_ver = bool(user.get("is_verified", 0)) or is_admin
    keyboard = get_main_menu_keyboard(
        bool(user.get("is_auto_trading", 0)), user.get("trading_mode", "paper"), is_admin=is_admin, is_verified=is_ver, lang=lang
    )
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_setwallet_command(update, context):
    """Handle /setwallet <network> <address> [memo] (Admin only)."""
    u = update.effective_user
    if u.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized. Administrator access only.")
        return

    text = update.message.text or ""
    # Strip command prefix
    for cmd in ["/setwallet", "/setaddress", "setwallet", "setaddress"]:
        if text.lower().startswith(cmd):
            text = text[len(cmd):].strip()
            break

    # Normalize delimiters
    tokens = text.replace("=", " ").replace(":", " ").replace(",", " ").split()
    if len(tokens) < 2:
        wallets = get_crypto_wallets(active_only=False)
        w_list = "\n".join([f"• `{w['network']}`: `{w['address']}`" for w in wallets])
        await update.message.reply_text(
            "💳 *SET PLATFORM CRYPTO DEPOSIT ADDRESS*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Usage:\n"
            "`/setwallet <NETWORK> <ADDRESS> [MEMO]`\n\n"
            "Examples:\n"
            "`/setwallet USDT_TRC20 TXYZ1234567890ABC`\n"
            "`/setwallet USDT_BEP20 0x1234567890ABCDEF`\n"
            "`/setwallet BTC bc1q1234567890abc`\n"
            "`/setwallet SOL 7XYZ1234567890abc`\n\n"
            "*Current Configured Addresses:*\n"
            f"{w_list}",
            parse_mode="Markdown"
        )
        return

    network = tokens[0].upper()
    address = tokens[1]
    memo = tokens[2] if len(tokens) > 2 else ""

    set_crypto_wallet(network, address, memo)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 View All Wallets", callback_data="admin_wallets")],
        [InlineKeyboardButton("👑 Admin Dashboard", callback_data="menu_admin")]
    ])
    await update.message.reply_text(
        f"✅ *Crypto Address Saved!*\n"
        f"• *Network:* `{network}`\n"
        f"• *Address:* `{address}`\n"
        f"• *Memo:* `{memo or 'None'}`\n\n"
        "All traders can now view this address in the Deposit menu.",
        reply_markup=kb,
        parse_mode="Markdown"
    )


async def handle_deposit_command(update, context):
    """Handle /deposit [network] [amount] [txid] submission."""
    u = update.effective_user
    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    args = context.args
    if len(args) < 3:
        # Show amount picker (consistent with reply keyboard "💰 Deposit" button flow)
        prompt = t("deposit_cart_prompt", lang)
        keyboard = get_quick_deposit_amounts_keyboard(lang)
        await update.message.reply_text(prompt, reply_markup=keyboard, parse_mode="Markdown")
        return

    network = args[0].upper()
    try:
        amount = float(args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Invalid amount. Example: `/deposit USDT_TRC20 500 0xTXID`", parse_mode="Markdown")
        return

    txid = args[2].strip()
    dep_id = create_deposit_request(u.id, network, amount, txid)

    await update.message.reply_text(
        t("deposit_submitted_ack", lang, id=dep_id, amount=amount, network=network),
        parse_mode="Markdown"
    )
    # --- Traffic Monitor ---
    try:
        push_event("deposit", {
            "user_id": u.id, "username": u.username or "", "first_name": u.first_name or "",
            "action": "Deposit Request",
            "detail": f"${amount:,.2f} via {network} (TxID: {txid[:12]}…)",
        })
    except Exception:
        pass

    # Notify all admins
    alert_text = (
        f"🚨 *NEW DEPOSIT PENDING APPROVAL*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• Deposit ID: `#{dep_id}`\n"
        f"• User: *{u.first_name}* (@{u.username or 'none'})\n"
        f"• User ID: `{u.id}`\n"
        f"• Network: `{network}`\n"
        f"• Amount: `${amount:,.2f}`\n"
        f"• TXID: `{txid}`"
    )
    for admin_id in ADMIN_USER_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=alert_text,
                reply_markup=get_admin_deposit_approval_keyboard(dep_id),
                parse_mode="Markdown"
            )
        except Exception:
            pass


async def handle_verifyuser_command(update, context):
    """Handle /verifyuser <user_id> (Admin only)."""
    u = update.effective_user
    if u.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return

    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("Usage: `/verifyuser <telegram_user_id>`", parse_mode="Markdown")
        return

    target_id = int(args[0])
    admin_verify_user(target_id, 1)
    await update.message.reply_text(f"✅ User `{target_id}` verified successfully!", parse_mode="Markdown")
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text="🎉 *Your account has been officially verified by Administrator!*",
            parse_mode="Markdown"
        )
    except Exception:
        pass


async def handle_admin_command(update, context):
    """Handle /admin command."""
    u = update.effective_user
    if u.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized. Administrator access only.")
        return

    user = get_user(u.id) or {}
    lang = user.get("language", "en")
    stats = get_admin_stats()
    pending_deps = len(get_pending_deposits())

    stats_block = t(
        "admin_stats", lang,
        users=stats['total_users'],
        verified=stats.get('verified_users', stats['total_users']),
        positions=stats['open_trades'],
        vol=stats.get('total_volume', 125000.0),
        deposits=pending_deps
    )

    text = (
        f"{t('admin_title', lang)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{stats_block}\n"
        f"• *Server Time:* `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(text, reply_markup=get_admin_keyboard(pending_deps, lang=lang), parse_mode="Markdown")


# Interactive Callback Query Handler
async def handle_callback_query(update, context):
    """Handle interactive inline keyboard button clicks."""
    import logging
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.error import BadRequest
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id
    user = get_or_create_user(user_id, query.from_user.username or "", query.from_user.first_name or "")
    lang = user.get("language", "en")

    is_admin = user_id in ADMIN_USER_IDS
    is_ver = bool(user.get("is_verified", 0)) or is_admin

    # ── safe_edit: handles photo-message fallback & "not modified" errors ──
    async def safe_edit(text, reply_markup=None, parse_mode="Markdown"):
        try:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except BadRequest as e:
            err = str(e)
            if "Message is not modified" in err:
                return  # Already showing same content — harmless
            if "There is no text in the message to edit" in err or "Message can't be edited" in err:
                # Photo/caption message — send a fresh reply instead
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                raise  # Re-raise for global handler

    try:
        if data == "verify_and_activate":
            verify_user(user_id)
            user["is_verified"] = 1
            await query.answer("✅ Bot verified and activated!")
            reply_kb = get_main_reply_keyboard(lang, is_admin=is_admin)
            welcome_txt = "Welcome back! Choose an option:" if not lang.startswith("pl") else "Witaj ponownie! Wybierz opcję:"
            await query.message.reply_text(welcome_txt, reply_markup=reply_kb, parse_mode="Markdown")
            return

        elif data.startswith("dep_amount:"):
            amount = float(data.split(":")[1])
            context.user_data["deposit_amount"] = amount
            cart_msg = (
                f"🛒 *Deposit Cart Created*\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Target Amount:* `${amount:,.2f} USD`\n"
                f"• *Minimum:* `$100.00 USD`\n"
                f"• *Status:* ⏳ `Select Payment Network`\n\n"
                "Please select your deposit cryptocurrency network below:"
            )
            await query.message.reply_text(
                cart_msg,
                reply_markup=get_deposit_crypto_selection_keyboard(amount, lang),
                parse_mode="Markdown"
            )
            return

        elif data.startswith("dep_network:"):
            _, network, amount_str = data.split(":")
            amount = float(amount_str)
            wallet = get_crypto_wallet(network)
            addr = wallet['address'] if wallet else 'TXYZ1234567890ABCDEF123456'
            memo_str = f"\n• *Memo / Destination Tag:* `{wallet['memo']}`" if wallet and wallet.get('memo') else ""

            invoice_msg = (
                f"🛒 *DEPOSIT PAYMENT INVOICE*\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Amount to Transfer:* `${amount:,.2f} USD`\n"
                f"• *Crypto Network:* `{network}`\n"
                f"• *Deposit Address:*\n`{addr}`{memo_str}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 *Step-by-Step Instructions:*\n"
                f"1. Open your crypto exchange or wallet app (e.g. Binance, TrustWallet, OKX, Telegram Wallet).\n"
                f"2. Send exactly `${amount:,.2f}` equivalent in `{network}` to the address above.\n"
                "3. Once sent, tap the *'Submit TXID'* button below and paste your transaction hash.\n"
                "4. Your balance will be credited automatically upon 1 network confirmation."
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Submit TXID / Payment Proof", callback_data=f"submit_dep_txid:{network}:{amount}")],
                [InlineKeyboardButton("🔙 Back to Amounts", callback_data="menu_deposit")]
            ])

            await query.message.reply_text(invoice_msg, reply_markup=kb, parse_mode="Markdown")
            return

        elif data.startswith("submit_dep_txid:"):
            _, network, amount_str = data.split(":")
            context.user_data["dep_network"] = network
            context.user_data["dep_amount"] = float(amount_str)
            context.user_data["awaiting_step"] = "awaiting_txid"
            prompt = (
                "📝 *SUBMIT TRANSACTION HASH (TXID)*\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Please paste and send your transaction hash (TXID) in the chat input below now:"
            )
            await query.message.reply_text(prompt, parse_mode="Markdown")
            return

        elif data == "cancel_deposit":
            await query.message.reply_text("❌ Deposit process cancelled.", reply_markup=get_main_reply_keyboard(lang, is_admin=is_admin), parse_mode="Markdown")
            return

        elif data == "btn_calculator":
            await query.message.reply_text(t("profit_calculator_content", lang), parse_mode="Markdown")
            return

        elif data == "prompt_withdraw":
            bal = user.get("paper_balance", 0.0)
            await query.message.reply_text(t("withdraw_prompt", lang, balance=bal), parse_mode="Markdown")
            return

        elif data == "menu_main" or data == "menu_refresh":
            text = format_welcome_message(user, lang)
            keyboard = get_main_menu_keyboard(bool(user["is_auto_trading"]), user["trading_mode"], is_admin=is_admin, is_verified=is_ver, lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "noop":
            await query.answer()
            return

        elif data == "menu_help":
            pages = HELP_PAGES.get(lang, HELP_PAGES["en"])
            page = pages[0]
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("1 / 5", callback_data="noop"),
                    InlineKeyboardButton("Next ▶", callback_data="help_page:1")
                ],
                [InlineKeyboardButton("❌ Close Tutorial", callback_data="menu_main")]
            ])
            await safe_edit(
                f"*{page['title']}*\n━━━━━━━━━━━━━━━━━━━━━━\n{page['body']}",
                reply_markup=kb, parse_mode="Markdown"
            )

        elif data.startswith("help_page:"):
            page_idx = int(data.split(":")[1])
            pages = HELP_PAGES.get(lang, HELP_PAGES["en"])
            page_idx = max(0, min(page_idx, len(pages) - 1))
            page = pages[page_idx]
            total = len(pages)
            nav = []
            if page_idx > 0:
                nav.append(InlineKeyboardButton("◀ Back", callback_data=f"help_page:{page_idx - 1}"))
            nav.append(InlineKeyboardButton(f"{page_idx + 1} / {total}", callback_data="noop"))
            if page_idx < total - 1:
                nav.append(InlineKeyboardButton("Next ▶", callback_data=f"help_page:{page_idx + 1}"))
            kb = InlineKeyboardMarkup([
                nav,
                [InlineKeyboardButton("❌ Close Tutorial", callback_data="menu_main")]
            ])
            await safe_edit(
                f"*{page['title']}*\n━━━━━━━━━━━━━━━━━━━━━━\n{page['body']}",
                reply_markup=kb, parse_mode="Markdown"
            )

        elif data == "toggle_language":
            new_lang = "pl" if lang == "en" else "en"
            set_user_language(user_id, new_lang)
            user["language"] = new_lang
            lang = new_lang
            text = format_settings_message(user, lang)
            keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data.startswith("set_lang:"):
            new_lang = data.split(":")[1]
            set_user_language(user_id, new_lang)
            user["language"] = new_lang
            lang = new_lang
            text = format_welcome_message(user, lang)
            keyboard = get_main_menu_keyboard(bool(user["is_auto_trading"]), user["trading_mode"], is_admin=is_admin, is_verified=is_ver, lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "menu_signals":
            text = t("signal_select_pair", lang)
            keyboard = get_pairs_keyboard("signal_pair", lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data.startswith("signal_pair:"):
            symbol = data.split(":", 1)[1]
            analyzing_txt = f"⏳ *Analiza w toku: {symbol}...*" if lang.startswith("pl") else f"⏳ *AI Engine analyzing {symbol}...*"
            await safe_edit(analyzing_txt, parse_mode="Markdown")
            candles = get_ohlcv(symbol, timeframe=DEFAULT_TIMEFRAME, limit=100)
            signal = get_ai_signal(symbol, DEFAULT_TIMEFRAME, candles)
            text = format_signal_message(signal, lang)
            keyboard = get_signal_action_keyboard(symbol, lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "menu_portfolio":
            text = format_portfolio_message(user_id, lang)
            keyboard = get_main_menu_keyboard(bool(user["is_auto_trading"]), user["trading_mode"], is_admin=is_admin, is_verified=is_ver, lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "menu_positions":
            text, buttons = format_positions_message(user_id, lang)
            kb = [[InlineKeyboardButton(b["text"], callback_data=b["callback_data"])] for b in buttons]
            kb.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu_main")])
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data.startswith("close_pos:"):
            pos_id = int(data.split(":")[1])
            res = close_trade(user_id, pos_id, reason="CLOSED_MANUAL")
            if res.get("success"):
                pnl_badge = "🟢" if res["pnl"] >= 0 else "🔴"
                msg = t(
                    "trade_close_success", lang,
                    pid=pos_id,
                    symbol=res['symbol'],
                    side=res['side'],
                    entry=res['entry_price'],
                    exit=res['exit_price'],
                    badge=pnl_badge,
                    pnl=res['pnl'],
                    pct=res['pnl_percent']
                )
            else:
                msg = f"❌ *Failed to close position:* {res.get('error')}"

            view_pos_text = "📈 Aktywne pozycje" if lang.startswith("pl") else "📈 View Open Positions"
            kb = [
                [InlineKeyboardButton(view_pos_text, callback_data="menu_positions")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "menu_trade":
            text = "⚡ *Wybierz parę do szybkiego zlecenia:*" if lang.startswith("pl") else "⚡ *Select a pair for Quick Trade:*"
            keyboard = get_pairs_keyboard("trade_select", lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data.startswith("trade_select:"):
            symbol = data.split(":", 1)[1]
            ticker = get_live_ticker(symbol)
            dir_prompt = "Wybierz kierunek zlecenia:" if lang.startswith("pl") else "Choose order direction:"
            text = (
                f"⚡ *Quick Trade: {symbol}*\n"
                f"💵 Current Price: `${ticker['price']:,.2f}`\n\n"
                f"{dir_prompt}"
            )
            keyboard = get_signal_action_keyboard(symbol, lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data.startswith("trade_prep:"):
            _, symbol, side = data.split(":")
            ticker = get_live_ticker(symbol)
            text = t("trade_prep_title", lang, symbol=symbol, side=side, price=ticker['price'])
            keyboard = get_quick_trade_amounts_keyboard(symbol, side, lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data.startswith("exec_trade:"):
            _, symbol, side, amount_str = data.split(":")
            amount = None if amount_str == "auto" else float(amount_str)
            res = open_trade(user_id, symbol, side, amount_usdt=amount)
            if res.get("success"):
                text = t(
                    "trade_success_title", lang,
                    pid=res['position_id'],
                    symbol=res['symbol'],
                    side=res['side'],
                    entry=res['entry_price'],
                    cost=res['cost'],
                    amount=res['amount'],
                    tp=res['take_profit'],
                    sl=res['stop_loss']
                )
            else:
                text = f"❌ *Trade Execution Failed:* {res.get('error')}"

            view_pos_text = "📈 Aktywne pozycje" if lang.startswith("pl") else "📈 View Open Positions"
            kb = [
                [InlineKeyboardButton(view_pos_text, callback_data="menu_positions")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "toggle_autotrade":
            new_val = 0 if user.get("is_auto_trading") else 1
            update_user_settings(user_id, is_auto_trading=new_val)
            user["is_auto_trading"] = new_val
            if lang.startswith("pl"):
                status_text = "🟢 *Automatyczny handel WŁĄCZONY!*\nAlgorytm AI będzie autonomicznie otwierał zlecenia." if new_val else "🔴 *Automatyczny handel WSTRZYMANY.*"
            else:
                status_text = "🟢 *Automated Trading ENABLED!*\nThe AI engine will autonomously scan and open trades." if new_val else "🔴 *Automated Trading PAUSED.*"

            kb = [[InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]]
            await safe_edit(status_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "menu_settings":
            text = format_settings_message(user, lang)
            keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data.startswith("set_mode:"):
            new_mode = data.split(":")[1]
            update_user_settings(user_id, trading_mode=new_mode)
            user["trading_mode"] = new_mode
            mode_icon = "⚡" if new_mode == "live" else "🧪"
            toast = f"{mode_icon} Mode: *{new_mode.upper()}* activated!" if not lang.startswith("pl") else f"{mode_icon} Tryb *{new_mode.upper()}* aktywowany!"
            await query.answer(toast, show_alert=True)
            # Re-display settings screen so user sees the change live
            text = format_settings_message(user, lang)
            keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "cycle_risk":
            current_risk = user.get("risk_percent", 2.0)
            next_risk = 5.0 if current_risk == 2.0 else (1.0 if current_risk == 5.0 else 2.0)
            update_user_settings(user_id, risk_percent=next_risk)
            user["risk_percent"] = next_risk
            await query.answer(f"🎯 Risk set to {next_risk}%", show_alert=False)
            text = format_settings_message(user, lang)
            keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "cycle_exchange":
            exchanges = ["binance", "bybit", "okx"]
            curr_idx = exchanges.index(user.get("exchange", "binance")) if user.get("exchange") in exchanges else 0
            next_ex = exchanges[(curr_idx + 1) % len(exchanges)]
            update_user_settings(user_id, exchange=next_ex)
            user["exchange"] = next_ex
            await query.answer(f"🔄 Exchange: {next_ex.upper()}", show_alert=False)
            text = format_settings_message(user, lang)
            keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
            await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")

        elif data == "reset_paper_balance":
            update_user_settings(user_id, paper_balance=10000.0)
            text = "✅ Saldo demo zresetowane do *$10,000.00 USDT*." if lang.startswith("pl") else "✅ Paper trading balance reset to *$10,000.00 USDT*."
            kb = [
                [InlineKeyboardButton(t("btn_portfolio", lang), callback_data="menu_portfolio")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "menu_admin":
            if user_id not in ADMIN_USER_IDS:
                await safe_edit("⛔ Unauthorized. Administrator access only.")
                return

            stats = get_admin_stats()
            pending_deps = len(get_pending_deposits())
            stats_block = t(
                "admin_stats", lang,
                users=stats['total_users'],
                verified=stats.get('verified_users', stats['total_users']),
                positions=stats['open_trades'],
                vol=stats.get('total_volume', 125000.0),
                deposits=pending_deps
            )
            text = (
                f"{t('admin_title', lang)}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{stats_block}\n"
                f"• *Server Time:* `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            await safe_edit(text, reply_markup=get_admin_keyboard(pending_deps, lang=lang), parse_mode="Markdown")

        elif data == "admin_users":
            if user_id not in ADMIN_USER_IDS:
                await safe_edit("⛔ Unauthorized.")
                return

            users = get_all_users()
            lines = ["👥 *REGISTERED PLATFORM USERS & VERIFICATION*", "━━━━━━━━━━━━━━━━━━━━━━"]
            kb = []
            for u in users:
                uname = f"@{u['username']}" if u['username'] else "No username"
                ver_status = "🟢 Verified" if u.get("is_verified") else "🔴 Unverified"
                lines.append(
                    f"• *{u.get('first_name', 'Trader')}* ({uname})\n"
                    f"  ID: `{u['user_id']}` | Status: {ver_status}\n"
                    f"  Mode: `{u['trading_mode'].upper()}` | Bal: `${u['paper_balance']:,.2f}`\n"
                )
                if not u.get("is_verified"):
                    kb.append([InlineKeyboardButton(f"✅ Verify User {u['user_id']}", callback_data=f"admin_toggle_ver:{u['user_id']}:1")])

            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
            kb.append([InlineKeyboardButton(t("btn_back_admin", lang), callback_data="menu_admin")])
            kb.append([InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")])
            await safe_edit("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data.startswith("admin_toggle_ver:"):
            _, target_id_str, status_str = data.split(":")
            target_id = int(target_id_str)
            admin_verify_user(target_id, int(status_str))
            await query.answer(f"User {target_id} verification updated!")
            try:
                await context.bot.send_message(
                    chat_id=target_id,
                    text="🎉 *Your account has been officially verified by Administrator!*",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            users = get_all_users()
            lines = ["👥 *REGISTERED PLATFORM USERS & VERIFICATION*", "━━━━━━━━━━━━━━━━━━━━━━"]
            kb = []
            for u in users:
                uname = f"@{u['username']}" if u['username'] else "No username"
                ver_status = "🟢 Verified" if u.get("is_verified") else "🔴 Unverified"
                lines.append(
                    f"• *{u.get('first_name', 'Trader')}* ({uname})\n"
                    f"  ID: `{u['user_id']}` | Status: {ver_status}\n"
                    f"  Mode: `{u['trading_mode'].upper()}` | Bal: `${u['paper_balance']:,.2f}`\n"
                )
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
            kb.append([InlineKeyboardButton(t("btn_back_admin", lang), callback_data="menu_admin")])
            await safe_edit("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "admin_positions":
            if user_id not in ADMIN_USER_IDS:
                await safe_edit("⛔ Unauthorized.")
                return

            all_pos = get_open_positions()
            if not all_pos:
                msg = "📈 *GLOBAL OPEN POSITIONS*\n━━━━━━━━━━━━━━━━━━━━━━\n_No open positions across the platform._"
            else:
                lines = ["📈 *GLOBAL OPEN POSITIONS ACROSS ALL TRADERS*", "━━━━━━━━━━━━━━━━━━━━━━"]
                for p in all_pos:
                    lines.append(
                        f"• *#{p['id']} {p['symbol']}* ({p['side']})\n"
                        f"  User ID: `{p['user_id']}` | Mode: `{p['mode'].upper()}`\n"
                        f"  Entry: `${p['entry_price']:,.2f}` | Cost: `${p['cost']:.2f}`\n"
                        f"  TP: `${p['take_profit']:,.2f}` | SL: `${p['stop_loss']:,.2f}`\n"
                    )
                lines.append("━━━━━━━━━━━━━━━━━━━━━━")
                msg = "\n".join(lines)

            kb = [
                [InlineKeyboardButton(t("btn_back_admin", lang), callback_data="menu_admin")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        # OTP Verification Callbacks
        elif data == "req_otp":
            otp = generate_user_otp(user_id)
            text = t("otp_title", lang, otp=otp)
            kb = [
                [InlineKeyboardButton(t("btn_otp_onetap", lang, otp=otp), callback_data=f"auto_verify:{otp}")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data.startswith("auto_verify:"):
            otp_code = data.split(":")[1]
            success = verify_user_otp(user_id, otp_code)
            if success:
                text = t("otp_success", lang)
                kb = [[InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]]
                await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
                # Ensure they get the full keyboard now that they are verified
                reply_kb = get_main_reply_keyboard(lang, is_admin=is_admin)
                welcome_txt = "✅ Bot verified and activated!\nChoose an option from the menu below:" if not lang.startswith("pl") else "✅ Bot zweryfikowany i aktywny!\nWybierz opcję z menu poniżej:"
                await query.message.reply_text(welcome_txt, reply_markup=reply_kb, parse_mode="Markdown")
            else:
                text = t("otp_invalid", lang)
                kb = [[InlineKeyboardButton(t("btn_otp_generate", lang), callback_data="req_otp")]]
                await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        # Deposit Callbacks
        elif data == "menu_deposit":
            # Show amount picker first (consistent with reply keyboard "💰 Deposit" flow)
            prompt = t("deposit_cart_prompt", lang)
            await safe_edit(prompt, reply_markup=get_quick_deposit_amounts_keyboard(lang), parse_mode="Markdown")

        elif data == "menu_deposit_wallets":
            # Show the raw wallet list (admin-facing or from /deposit command)
            wallets = get_crypto_wallets()
            text = t("deposit_menu_title", lang)
            await safe_edit(text, reply_markup=get_deposit_wallets_keyboard(wallets, lang=lang), parse_mode="Markdown")

        elif data.startswith("view_wallet:"):
            network = data.split(":")[1]
            wallet = get_crypto_wallet(network)
            if wallet:
                memo_str = f"• *Memo / Tag:* `{wallet['memo']}`" if wallet.get("memo") else ""
                text = t("deposit_address_info", lang, network=wallet['network'], address=wallet['address'], memo_line=memo_str)
                kb = [
                    [InlineKeyboardButton(t("btn_deposit_proof", lang), callback_data="submit_deposit_prompt")],
                    [InlineKeyboardButton("🔙 Back to Networks" if not lang.startswith("pl") else "🔙 Powrót do sieci", callback_data="menu_deposit_wallets")],
                    [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
                ]
                await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            else:
                await query.answer(f"⚠️ Wallet for {network} not configured yet.", show_alert=True)

        elif data == "submit_deposit_prompt":
            text = t("deposit_submit_help", lang)
            kb = [
                [InlineKeyboardButton("🔙 Back to Deposit" if not lang.startswith("pl") else "🔙 Powrót do wpłaty", callback_data="menu_deposit")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        # Admin Wallets & Deposits
        elif data == "admin_wallets":
            if user_id not in ADMIN_USER_IDS:
                await safe_edit("⛔ Unauthorized.")
                return

            wallets = get_crypto_wallets(active_only=False)
            text = (
                "💳 *ADMIN CRYPTO ADDRESS MANAGEMENT*\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Select any network below to update its deposit address, or add a new network:"
            )
            await safe_edit(text, reply_markup=get_admin_wallets_keyboard(wallets, lang=lang), parse_mode="Markdown")

        elif data.startswith("admin_edit_wallet:"):
            network = data.split(":")[1]
            wallet = get_crypto_wallet(network)
            curr_addr = wallet['address'] if wallet else 'None'
            context.user_data["awaiting_step"] = f"awaiting_wallet_addr:{network}"
            text = (
                f"✏️ *UPDATE WALLET: {network}*\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Current Address:*\n`{curr_addr}`\n\n"
                "👉 *Paste the new deposit address directly into this chat to save it.*\n\n"
                "_(Optional: separate with a space if there is a MEMO or TAG)_\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            kb = [
                [InlineKeyboardButton("🔙 Cancel & Back to Wallets", callback_data="admin_wallets")],
                [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
            ]
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "admin_add_wallet_prompt":
            context.user_data["awaiting_step"] = "awaiting_new_wallet"
            text = (
                "➕ *ADD NEW CRYPTO WALLET NETWORK*\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "👉 *Send the network and address directly in this chat:*\n\n"
                "Format: `<NETWORK> <ADDRESS> [OPTIONAL_MEMO]`\n\n"
                "*Example:*\n"
                "`TON UQABC1234567890 98765`\n"
                "`USDT_ERC20 0x1234567890abcdef1234`\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            kb = [[InlineKeyboardButton("🔙 Cancel & Back to Wallets", callback_data="admin_wallets")]]
            await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "admin_deposits":
            if user_id not in ADMIN_USER_IDS:
                await safe_edit("⛔ Unauthorized.")
                return

            pending = get_pending_deposits()
            if not pending:
                text = "📋 *PENDING DEPOSITS*\n━━━━━━━━━━━━━━━━━━━━━━\n_No deposits awaiting approval._"
                kb = [[InlineKeyboardButton(t("btn_back_admin", lang), callback_data="menu_admin")]]
                await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            else:
                await safe_edit(
                    f"📋 *PENDING DEPOSITS ({len(pending)} AWAITING APPROVAL)*\n"
                    "Review each deposit below:",
                    parse_mode="Markdown"
                )
                for d in pending[:5]:
                    d_msg = (
                        f"💳 *DEPOSIT #{d['id']}*\n"
                        f"• User: *{d.get('first_name', 'Trader')}* (ID: `{d['user_id']}`)\n"
                        f"• Network: `{d['network']}`\n"
                        f"• Amount: `${d['amount']:,.2f} USDT`\n"
                        f"• TXID: `{d['txid']}`\n"
                        f"• Submitted: `{d['created_at']}`"
                    )
                    await query.message.reply_text(
                        d_msg,
                        reply_markup=get_admin_deposit_approval_keyboard(d['id'], lang=lang),
                        parse_mode="Markdown"
                    )

        elif data.startswith("dep_approve:"):
            if user_id not in ADMIN_USER_IDS:
                await query.answer("Unauthorized.")
                return

            dep_id = int(data.split(":")[1])
            dep = get_deposit_request(dep_id)
            if dep and update_deposit_status(dep_id, "APPROVED"):
                await safe_edit(
                    f"✅ *Deposit #{dep_id} APPROVED!*\n"
                    f"Credited `${dep['amount']:,.2f} USDT` to User `{dep['user_id']}`.",
                    parse_mode="Markdown"
                )
                try:
                    target_lang = get_user_language(dep["user_id"])
                    user_notif = (
                        "🎉 *WPŁATA ZATWIERDZONA I ZAKSIĘGOWANA!*\n"
                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• Kwota: `${dep['amount']:,.2f} USDT`\n"
                        f"• Sieć: `{dep['network']}`\n"
                        "• Status: `DODANO DO SALDA`\n\n"
                        "Sprawdź swój /portfolio, aby rozpocząć handel!"
                    ) if target_lang.startswith("pl") else (
                        "🎉 *DEPOSIT APPROVED & CREDITED!*\n"
                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• Amount: `${dep['amount']:,.2f} USDT`\n"
                        f"• Network: `{dep['network']}`\n"
                        "• Status: `CREDITED TO BALANCE`\n\n"
                        "Check your /portfolio to start trading!"
                    )
                    await context.bot.send_message(
                        chat_id=dep["user_id"],
                        text=user_notif,
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass
            else:
                await safe_edit(f"⚠️ Deposit #{dep_id} already processed or not found.")

        elif data.startswith("dep_reject:"):
            if user_id not in ADMIN_USER_IDS:
                await query.answer("Unauthorized.")
                return

            dep_id = int(data.split(":")[1])
            dep = get_deposit_request(dep_id)
            if dep and update_deposit_status(dep_id, "REJECTED"):
                await safe_edit(f"❌ *Deposit #{dep_id} REJECTED.*", parse_mode="Markdown")
                try:
                    target_lang = get_user_language(dep["user_id"])
                    reject_msg = (
                        f"⚠️ *Powiadomienie o wpłacie (#DEP-{dep_id})*\n"
                        "Wpłata nie mogła zostać zweryfikowana w blockchainie. Skontaktuj się z administratorem."
                    ) if target_lang.startswith("pl") else (
                        f"⚠️ *Deposit Notice (#DEP-{dep_id})*\n"
                        "Your deposit could not be verified on the blockchain. Please contact administration."
                    )
                    await context.bot.send_message(
                        chat_id=dep["user_id"],
                        text=reject_msg,
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass


    except BadRequest as e:
        err = str(e)
        if "Message is not modified" not in err:
            logging.getLogger("AITradingBot").warning(f"Telegram BadRequest [{data}]: {e}")
            try:
                await query.answer(f"⚠️ Error: {err[:120]}", show_alert=True)
            except Exception:
                pass
    except Exception as e:
        logging.getLogger("AITradingBot").error(f"Callback error [{data}]: {e}", exc_info=True)
        try:
            await query.answer("⚠️ Something went wrong. Please try again.", show_alert=True)
        except Exception:
            pass

async def handle_withdraw_command(update, context):
    """Handle /withdraw <amount> <network> <wallet_address>."""
    u = update.effective_user
    user = get_or_create_user(u.id, u.username or "", u.first_name or "")
    lang = user.get("language", "en")
    args = context.args

    if len(args) < 3:
        bal = user.get("paper_balance", 0.0)
        msg = (
            f"⚠️ *Usage / Użycie:*\n"
            f"`/withdraw <AMOUNT> <NETWORK> <WALLET_ADDRESS>`\n\n"
            f"• *Available Balance:* `${bal:,.2f} USD`\n"
            f"• *Minimum Withdrawal:* `$50.00 USD`\n\n"
            f"*Example:*\n"
            f"`/withdraw 150 USDT_TRC20 TXYZ1234567890ABCDEF`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    try:
        amount = float(args[0])
    except ValueError:
        await update.message.reply_text("⚠️ Invalid withdrawal amount.", parse_mode="Markdown")
        return

    if amount < 50.0:
        await update.message.reply_text("⚠️ Minimum withdrawal is $50.00 USD.", parse_mode="Markdown")
        return

    network = args[1].upper()
    address = args[2].strip()

    req_id = create_withdrawal_request(u.id, network, amount, address)
    if not req_id:
        await update.message.reply_text("⚠️ Insufficient available balance for this withdrawal.", parse_mode="Markdown")
        return

    ack = (
        f"🕊️ *WITHDRAWAL REQUEST SUBMITTED (#WDR-{req_id})*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Amount:* `${amount:,.2f} USD`\n"
        f"• *Destination Network:* `{network}`\n"
        f"• *Wallet Address:* `{address}`\n"
        f"• *Status:* ⏳ `PROCESSING`\n\n"
        "Your withdrawal request has been placed into the automated payout queue (typically 5 to 30 minutes)."
    )
    is_sender_admin = u.id in ADMIN_USER_IDS
    await update.message.reply_text(ack, reply_markup=get_main_reply_keyboard(lang, is_admin=is_sender_admin), parse_mode="Markdown")
    # --- Traffic Monitor ---
    try:
        push_event("withdraw", {
            "user_id": u.id, "username": u.username or "", "first_name": u.first_name or "",
            "action": "Withdrawal Request",
            "detail": f"${amount:,.2f} via {network} to {address[:10]}…",
        })
    except Exception:
        pass

    for admin_id in ADMIN_USER_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🚨 *NEW WITHDRAWAL REQUEST (#WDR-{req_id})*\n• User: {u.first_name} (`{u.id}`)\n• Amount: `${amount:,.2f}`\n• Network: `{network}`\n• Address: `{address}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass


async def handle_text_message(update, context):
    """
    Handle incoming text messages from custom reply keyboards or user input.
    Matches the exact Telegram interface shown in the screenshot:
    - 💰 Deposit
    - ✅ User Reviews
    - 📊 Profit Calculator
    - 📖 How It Works
    - 💬 Live Support
    - 📊 Live Charts
    - 👤 My Account & Balance
    - 🏛️ About Us
    - ℹ️ FAQ
    - 🕊️ Withdraw Funds
    """
    u = update.effective_user
    user = get_or_create_user(u.id, u.username or "", u.first_name or "")
    lang = user.get("language", "en")
    raw_text = update.message.text.strip()
    text = raw_text
    # --- Traffic Monitor: emit message/menu-tap event ---
    try:
        push_event("message", {
            "user_id": u.id,
            "username": u.username or "",
            "first_name": u.first_name or "",
            "action": "Menu Tap",
            "detail": raw_text[:80],
        })
    except Exception:
        pass

    # Admin: Awaiting new wallet address input
    step = context.user_data.get("awaiting_step")
    if step and step.startswith("awaiting_wallet_addr:"):
        network = step.split(":", 1)[1]
        tokens = text.replace("=", " ").replace(":", " ").replace(",", " ").split()
        if not tokens:
            await update.message.reply_text("⚠️ Address cannot be empty. Please send a valid address:")
            return
        new_address = tokens[0]
        memo = tokens[1] if len(tokens) > 1 else ""
        set_crypto_wallet(network, new_address, memo)
        context.user_data["awaiting_step"] = None

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 View All Wallets", callback_data="admin_wallets")],
            [InlineKeyboardButton("👑 Admin Dashboard", callback_data="menu_admin")]
        ])
        await update.message.reply_text(
            f"✅ *Deposit Address Updated for {network}!*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Network:* `{network}`\n"
            f"• *New Address:* `{new_address}`\n"
            f"• *Memo / Tag:* `{memo or 'None'}`\n\n"
            "All traders will now receive this address in the Deposit menu.",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        return

    if step == "awaiting_new_wallet":
        tokens = text.replace("=", " ").replace(":", " ").replace(",", " ").split()
        if len(tokens) < 2:
            await update.message.reply_text(
                "⚠️ Please provide both network and address separated by a space.\n"
                "*Example:*\n`TON UQABC1234567890 98765`",
                parse_mode="Markdown"
            )
            return
        network = tokens[0].upper()
        new_address = tokens[1]
        memo = tokens[2] if len(tokens) > 2 else ""
        set_crypto_wallet(network, new_address, memo)
        context.user_data["awaiting_step"] = None

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 View All Wallets", callback_data="admin_wallets")],
            [InlineKeyboardButton("👑 Admin Dashboard", callback_data="menu_admin")]
        ])
        await update.message.reply_text(
            f"✅ *New Crypto Network Added!*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Network:* `{network}`\n"
            f"• *Address:* `{new_address}`\n"
            f"• *Memo / Tag:* `{memo or 'None'}`\n\n"
            "All traders can now deposit using this network.",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        return

    # Admin: Direct setwallet text command without leading slash
    if text.lower().startswith("setwallet ") or text.lower().startswith("setaddress "):
        if u.id in ADMIN_USER_IDS:
            await handle_setwallet_command(update, context)
            return

    # 1. 💰 Deposit Button
    if text in ["💰 Deposit", "Deposit", "💰 Wpłata", "Wpłata"]:
        context.user_data["awaiting_step"] = "deposit_amount"
        prompt = t("deposit_cart_prompt", lang)
        quick_kb = get_quick_deposit_amounts_keyboard(lang)
        await update.message.reply_text(prompt, reply_markup=quick_kb, parse_mode="Markdown")
        return

    # 2. Check if user sent an amount (e.g. 150 or $150 or 500)
    cleaned_amount = text.replace("$", "").replace(",", "").strip()
    is_numeric = False
    try:
        val = float(cleaned_amount)
        is_numeric = True
    except ValueError:
        is_numeric = False

    if is_numeric and (context.user_data.get("awaiting_step") == "deposit_amount" or text.startswith("$") or cleaned_amount.isdigit()):
        amount = float(cleaned_amount)
        if amount < 100.0:
            await update.message.reply_text(
                "⚠️ *Minimum: $ 100.00 usd*\n\nPlease enter an amount equal to or above $100 (e.g. `150` or `$150`).",
                parse_mode="Markdown"
            )
            return

        context.user_data["deposit_amount"] = amount
        context.user_data["awaiting_step"] = "select_network"
        cart_msg = (
            f"🛒 *Deposit Cart Created*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Deposit Amount:* `${amount:,.2f} USD`\n"
            f"• *Minimum:* `$100.00 USD`\n"
            f"• *Status:* ⏳ `Awaiting Payment Network`\n\n"
            "Please choose your preferred deposit cryptocurrency network below:"
        )
        await update.message.reply_text(
            cart_msg,
            reply_markup=get_deposit_crypto_selection_keyboard(amount, lang),
            parse_mode="Markdown"
        )
        return

    # 3. Handle TXID submission
    if context.user_data.get("awaiting_step") == "awaiting_txid":
        txid = text
        network = context.user_data.get("dep_network", "USDT_TRC20")
        amount = context.user_data.get("dep_amount", 100.0)
        dep_id = create_deposit_request(u.id, network, amount, txid)
        context.user_data["awaiting_step"] = None

        ack = (
            f"✅ *Deposit TXID Submitted (#DEP-{dep_id})*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Amount:* `${amount:,.2f} USD`\n"
            f"• *Network:* `{network}`\n"
            f"• *TXID:* `{txid}`\n\n"
            "Your transaction is currently being verified on the blockchain. Your balance will be credited automatically upon confirmation (usually 5-15 minutes)."
        )
        is_sender_admin = u.id in ADMIN_USER_IDS
        await update.message.reply_text(ack, reply_markup=get_main_reply_keyboard(lang, is_admin=is_sender_admin), parse_mode="Markdown")

        for admin_id in ADMIN_USER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🚨 *NEW DEPOSIT PENDING APPROVAL*\n• ID: `#{dep_id}`\n• User: {u.first_name} (`{u.id}`)\n• Network: `{network}`\n• Amount: `${amount:,.2f}`\n• TXID: `{txid}`",
                    reply_markup=get_admin_deposit_approval_keyboard(dep_id, lang=lang),
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        return

    # 4. ✅ User Reviews
    if text in ["✅ User Reviews", "User Reviews", "✅ Opinie użytkowników", "Opinie"]:
        reviews_text = "👉 Check out our latest user reviews and verified profit results on our official channel!" if not lang.startswith("pl") else "👉 Sprawdź nasze najnowsze opinie użytkowników na naszym oficjalnym kanale!"
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ View Verified Reviews", url="https://t.me/automatedtrading2")]
        ])
        await update.message.reply_text(reviews_text, reply_markup=kb, parse_mode="Markdown")
        return

    # 5. 📊 Profit Calculator
    if text in ["📊 Profit Calculator", "Profit Calculator", "📊 Kalkulator zysków", "Kalkulator"]:
        calc_text = t("profit_calculator_content", lang)
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 Deposit $100", callback_data="dep_amount:100"),
                InlineKeyboardButton("💰 Deposit $500", callback_data="dep_amount:500")
            ],
            [
                InlineKeyboardButton("💰 Deposit $1,000", callback_data="dep_amount:1000"),
                InlineKeyboardButton("💰 Deposit $5,000", callback_data="dep_amount:5000")
            ]
        ])
        await update.message.reply_text(calc_text, reply_markup=kb, parse_mode="Markdown")
        return

    # 6. 📖 How It Works
    if text in ["📖 How It Works", "How It Works", "📖 Jak to działa", "Jak to działa"]:
        msg = t("how_it_works_content", lang)
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Start With Deposit ($100)", callback_data="menu_deposit")]
        ])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
        return

    # 7. 💬 Live Support
    if text in ["💬 Live Support", "Live Support", "💬 Wsparcie na żywo", "Wsparcie"]:
        msg = t("live_support_content", lang)
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Open Support Chat", url="tg://resolve?domain=KELVIN_ADMIN_SUPPORT")]
        ])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
        return

    # 8. 📊 Live Charts
    if text in ["📊 Live Charts", "Live Charts", "📊 Wykresy na żywo", "Wykresy"]:
        pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
        lines = [
            "📊 *REAL-TIME CRYPTO MARKET CHARTS & SIGNALS*",
            "━━━━━━━━━━━━━━━━━━━━━━"
        ]
        for p in pairs:
            tick = get_live_ticker(p)
            chg = tick.get("change_24h", 0.0)
            chg_sign = "+" if chg >= 0 else ""
            badge = "🟢" if chg >= 0 else "🔴"
            lines.append(f"{badge} *{p}:* `${tick['price']:,.2f}` ({chg_sign}{chg:.2f}%)")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("💡 *AI Engine is continuously tracking order flow and momentum.*")
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Detailed AI Analysis", callback_data="menu_signals")],
            [InlineKeyboardButton("⚡ Quick Trade", callback_data="menu_trade")]
        ])
        await update.message.reply_text("\n".join(lines), reply_markup=kb, parse_mode="Markdown")
        return

    # 9. 👤 My Account & Balance
    if text in ["👤 My Account & Balance", "My Account & Balance", "👤 Moje konto & Saldo", "Moje konto"]:
        stats = get_portfolio_stats(u.id) or {}
        bal = stats.get("paper_balance", user.get("paper_balance", 10000.0))
        pnl = stats.get("total_realized_pnl", 0.0)
        pnl_sign = "+" if pnl >= 0 else ""
        win_rate = stats.get("win_rate", 87.5)
        open_pos = stats.get("open_positions_count", 0)
        is_ver = bool(user.get("is_verified", 0)) or (u.id in ADMIN_USER_IDS)
        ver_badge = "🟢 Verified & Active" if is_ver else "🔴 Unverified"
        auto_badge = "🟢 ACTIVE" if user.get("is_auto_trading") else "🔴 PAUSED"

        acc_msg = (
            "👤 *MY ACCOUNT & BALANCE*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• *User:* *{u.first_name}* (@{u.username or 'none'})\n"
            f"• *Account ID:* `{u.id}`\n"
            f"• *Status:* `{ver_badge}`\n"
            f"• *Trading Mode:* `{user.get('trading_mode', 'paper').upper()}`\n"
            f"• *Total Available Balance:* `${bal:,.2f} USD`\n"
            f"• *Total Realized Profit:* `{pnl_sign}${pnl:,.2f} USD`\n"
            f"• *AI Win Rate:* `{win_rate:.1f}%`\n"
            f"• *Active Open Trades:* `{open_pos}`\n"
            f"• *Automated Trading:* `{auto_badge}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 Deposit Funds", callback_data="menu_deposit"),
                InlineKeyboardButton("🕊️ Withdraw Funds", callback_data="prompt_withdraw")
            ],
            [
                InlineKeyboardButton("⚙️ Trading Settings", callback_data="menu_settings")
            ]
        ])
        await update.message.reply_text(acc_msg, reply_markup=kb, parse_mode="Markdown")
        return

    # 10. 🏛️ About Us
    if text in ["🏛️ About Us", "About Us", "🏛️ O nas", "O nas"]:
        msg = t("about_us_content", lang)
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # 11. ℹ️ FAQ
    if text in ["ℹ️ FAQ", "FAQ"]:
        msg = t("faq_content", lang)
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # 12. 🕊️ Withdraw Funds
    if text in ["🕊️ Withdraw Funds", "Withdraw Funds", "🕊️ Wypłać środki", "Wypłać"]:
        bal = user.get("paper_balance", 0.0)
        msg = t("withdraw_prompt", lang, balance=bal)
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # 13. 👑 Admin Dashboard (Only for admins)
    if text.lower() in ["👑 admin dashboard", "admin dashboard", "admin", "/admin", "👑 panel administratora", "panel administratora"]:
        if u.id not in ADMIN_USER_IDS:
            await update.message.reply_text("⛔ Unauthorized. Administrator access only.")
            return
        await handle_admin_command(update, context)
        return
