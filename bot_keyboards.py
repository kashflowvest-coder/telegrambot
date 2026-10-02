from typing import List
from config import SUPPORTED_PAIRS
from i18n import t

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
except ImportError:
    # Lightweight mock for headless / non-telegram testing
    class InlineKeyboardButton:
        def __init__(self, text, callback_data=None, url=None):
            self.text = text
            self.callback_data = callback_data
            self.url = url

    class InlineKeyboardMarkup:
        def __init__(self, inline_keyboard):
            self.inline_keyboard = inline_keyboard

    class KeyboardButton:
        def __init__(self, text):
            self.text = text

    class ReplyKeyboardMarkup:
        def __init__(self, keyboard, resize_keyboard=True, is_persistent=True):
            self.keyboard = keyboard
            self.resize_keyboard = resize_keyboard
            self.is_persistent = is_persistent


def get_main_reply_keyboard(lang: str = "en", is_admin: bool = False) -> ReplyKeyboardMarkup:
    """
    Main persistent custom reply keyboard matching the exact layout in the user interface screenshot:
    Row 1: [ 💰 Deposit ]
    Row 2: [ ✅ User Reviews ]    [ 📊 Profit Calculator ]
    Row 3: [ 📖 How It Works ]    [ 💬 Live Support ]
    Row 4: [ 📊 Live Charts ]
    Row 5: [ 👤 My Account & Balance ]
    Row 6: [ 🏛️ About Us ]        [ ℹ️ FAQ ]
    Row 7: [ 🕊️ Withdraw Funds ]
    """
    keyboard = [
        [KeyboardButton("💰 Deposit")],
        [KeyboardButton("✅ User Reviews"), KeyboardButton("📊 Profit Calculator")],
        [KeyboardButton("📖 How It Works"), KeyboardButton("💬 Live Support")],
        [KeyboardButton("📊 Live Charts")],
        [KeyboardButton("👤 My Account & Balance")],
        [KeyboardButton("🏛️ About Us"), KeyboardButton("ℹ️ FAQ")],
        [KeyboardButton("🕊️ Withdraw Funds")]
    ]
    if is_admin:
        admin_btn_text = "👑 Admin Dashboard" if not lang.startswith("pl") else "👑 Panel Administratora"
        keyboard.append([KeyboardButton(admin_btn_text)])
        
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


def get_verification_inline_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """The single high-impact verification button from the screenshot."""
    btn_text = "🔑 Generate OTP to Verify" if not lang.startswith("pl") else "🔑 Wygeneruj OTP, aby zweryfikować"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_text, callback_data="req_otp")]
    ])


def get_quick_deposit_amounts_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Quick deposit amount selection chips."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("$100", callback_data="dep_amount:100"),
            InlineKeyboardButton("$150", callback_data="dep_amount:150"),
            InlineKeyboardButton("$250", callback_data="dep_amount:250")
        ],
        [
            InlineKeyboardButton("$500", callback_data="dep_amount:500"),
            InlineKeyboardButton("$1,000", callback_data="dep_amount:1000"),
            InlineKeyboardButton("$2,500", callback_data="dep_amount:2500")
        ]
    ])


def get_deposit_crypto_selection_keyboard(amount: float, lang: str = "en") -> InlineKeyboardMarkup:
    """Cryptocurrency network options when depositing."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 USDT (TRC20)", callback_data=f"dep_network:USDT_TRC20:{amount}"),
            InlineKeyboardButton("🪙 USDT (BEP20)", callback_data=f"dep_network:USDT_BEP20:{amount}")
        ],
        [
            InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data=f"dep_network:BTC:{amount}"),
            InlineKeyboardButton("⚡ Solana (SOL)", callback_data=f"dep_network:SOL:{amount}")
        ],
        [
            InlineKeyboardButton("💎 TON Network", callback_data=f"dep_network:TON:{amount}"),
            InlineKeyboardButton("🔷 Ethereum (ERC20)", callback_data=f"dep_network:USDT_ERC20:{amount}")
        ],
        [
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_deposit")
        ]
    ])



def get_main_menu_keyboard(
    is_auto_trading: bool = False,
    trading_mode: str = "paper",
    is_admin: bool = False,
    is_verified: bool = False,
    lang: str = "en"
) -> InlineKeyboardMarkup:
    """Primary navigation menu for the bot with bilingual support."""
    auto_status_icon = "🟢 ACTIVE" if is_auto_trading else "🔴 PAUSED"
    if lang.startswith("pl"):
        auto_status_icon = "🟢 AKTYWNY" if is_auto_trading else "🔴 WSTRZYMANY"

    mode_label = "🧪 PAPER" if trading_mode == "paper" else "⚡ LIVE"
    if lang.startswith("pl"):
        mode_label = "🧪 DEMO" if trading_mode == "paper" else "⚡ LIVE"

    keyboard = []

    # If unverified, show urgent OTP verification badge at the top
    if not is_verified and not is_admin:
        keyboard.append([InlineKeyboardButton(t("btn_verify_urgent", lang), callback_data="req_otp")])

    keyboard.extend([
        [
            InlineKeyboardButton(t("btn_ai_signals", lang), callback_data="menu_signals"),
            InlineKeyboardButton(t("btn_portfolio", lang), callback_data="menu_portfolio")
        ],
        [
            InlineKeyboardButton(t("btn_active_trades", lang), callback_data="menu_positions"),
            InlineKeyboardButton(t("btn_quick_trade", lang), callback_data="menu_trade")
        ],
        [
            InlineKeyboardButton(t("btn_deposit", lang), callback_data="menu_deposit"),
            InlineKeyboardButton(f"⚙️ {mode_label}", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton(f"🤖 Auto: {auto_status_icon}", callback_data="toggle_autotrade"),
            InlineKeyboardButton(t("btn_refresh", lang), callback_data="menu_refresh")
        ],
        [
            InlineKeyboardButton(t("btn_guide", lang), callback_data="menu_help")
        ]
    ])

    if is_admin:
        keyboard.append([InlineKeyboardButton(t("btn_admin", lang), callback_data="menu_admin")])

    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard(pending_count: int = 0, lang: str = "en") -> InlineKeyboardMarkup:
    """Admin dashboard keyboard controls."""
    if pending_count > 0:
        dep_text = f"📋 Deposits ({pending_count} PENDING)" if not lang.startswith("pl") else f"📋 Wpłaty ({pending_count} OCZEKUJE)"
    else:
        dep_text = "📋 Pending Deposits" if not lang.startswith("pl") else "📋 Oczekujące wpłaty"

    users_text = "👥 User Directory & OTP" if not lang.startswith("pl") else "👥 Użytkownicy & OTP"
    positions_text = "📈 Global Open Positions" if not lang.startswith("pl") else "📈 Globalne pozycje"
    wallets_text = "💳 Manage Crypto Addresses" if not lang.startswith("pl") else "💳 Zarządzaj portfelami"
    refresh_text = "🔄 Refresh Admin Stats" if not lang.startswith("pl") else "🔄 Odśwież statystyki"

    keyboard = [
        [
            InlineKeyboardButton(users_text, callback_data="admin_users"),
            InlineKeyboardButton(positions_text, callback_data="admin_positions")
        ],
        [
            InlineKeyboardButton(wallets_text, callback_data="admin_wallets"),
            InlineKeyboardButton(dep_text, callback_data="admin_deposits")
        ],
        [
            InlineKeyboardButton(refresh_text, callback_data="menu_admin"),
            InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_deposit_wallets_keyboard(wallets: List[dict], lang: str = "en") -> InlineKeyboardMarkup:
    """User deposit menu showing available networks."""
    keyboard = []
    for w in wallets:
        keyboard.append([InlineKeyboardButton(f"📥 {w['network']}", callback_data=f"view_wallet:{w['network']}")])

    keyboard.append([InlineKeyboardButton(t("btn_deposit_proof", lang), callback_data="submit_deposit_prompt")])
    keyboard.append([InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")])
    return InlineKeyboardMarkup(keyboard)


def get_admin_wallets_keyboard(wallets: List[dict], lang: str = "en") -> InlineKeyboardMarkup:
    """Admin crypto wallet management list."""
    keyboard = []
    for w in wallets:
        edit_text = f"✏️ Edit {w['network']}" if not lang.startswith("pl") else f"✏️ Edytuj {w['network']}"
        keyboard.append([InlineKeyboardButton(edit_text, callback_data=f"admin_edit_wallet:{w['network']}")])

    add_text = "➕ Add New Crypto Network" if not lang.startswith("pl") else "➕ Dodaj nową sieć"
    keyboard.append([InlineKeyboardButton(add_text, callback_data="admin_add_wallet_prompt")])
    keyboard.append([InlineKeyboardButton(t("btn_back_admin", lang), callback_data="menu_admin")])
    return InlineKeyboardMarkup(keyboard)


def get_admin_deposit_approval_keyboard(deposit_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Approval buttons for deposit transaction review."""
    approve_text = "✅ Approve & Credit Balance" if not lang.startswith("pl") else "✅ Zatwierdź i doładuj saldo"
    reject_text = "❌ Reject Deposit" if not lang.startswith("pl") else "❌ Odrzuć wpłatę"
    keyboard = [
        [
            InlineKeyboardButton(approve_text, callback_data=f"dep_approve:{deposit_id}"),
            InlineKeyboardButton(reject_text, callback_data=f"dep_reject:{deposit_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_otp_verification_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """OTP Verification prompt keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(t("btn_otp_generate", lang), callback_data="req_otp")
        ],
        [
            InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_pairs_keyboard(action_prefix: str = "signal_pair", lang: str = "en") -> InlineKeyboardMarkup:
    """Grid of top supported trading pairs."""
    keyboard = []
    row = []
    for i, pair in enumerate(SUPPORTED_PAIRS):
        row.append(InlineKeyboardButton(pair, callback_data=f"{action_prefix}:{pair}"))
        if len(row) == 2 or i == len(SUPPORTED_PAIRS) - 1:
            keyboard.append(row)
            row = []

    keyboard.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu_main")])
    return InlineKeyboardMarkup(keyboard)


def get_signal_action_keyboard(symbol: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Actions available directly under an AI Signal report."""
    base = symbol.split('/')[0]
    buy_text = f"🟢 Long / Buy {base}" if not lang.startswith("pl") else f"🟢 Kup / Long {base}"
    sell_text = f"🔴 Short / Sell {base}" if not lang.startswith("pl") else f"🔴 Sprzedaj / Short {base}"

    keyboard = [
        [
            InlineKeyboardButton(buy_text, callback_data=f"trade_prep:{symbol}:BUY"),
            InlineKeyboardButton(sell_text, callback_data=f"trade_prep:{symbol}:SELL")
        ],
        [
            InlineKeyboardButton(t("btn_reanalyze", lang), callback_data=f"signal_pair:{symbol}"),
            InlineKeyboardButton(t("btn_other_pairs", lang), callback_data="menu_signals")
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_quick_trade_amounts_keyboard(symbol: str, side: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Pre-set position size buttons in USDT."""
    auto_risk_text = "🎯 Auto Risk (2%)" if not lang.startswith("pl") else "🎯 Auto Ryzyko (2%)"
    keyboard = [
        [
            InlineKeyboardButton("$25 USDT", callback_data=f"exec_trade:{symbol}:{side}:25"),
            InlineKeyboardButton("$50 USDT", callback_data=f"exec_trade:{symbol}:{side}:50")
        ],
        [
            InlineKeyboardButton("$100 USDT", callback_data=f"exec_trade:{symbol}:{side}:100"),
            InlineKeyboardButton("$250 USDT", callback_data=f"exec_trade:{symbol}:{side}:250")
        ],
        [
            InlineKeyboardButton(auto_risk_text, callback_data=f"exec_trade:{symbol}:{side}:auto")
        ],
        [
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="menu_trade")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_position_action_keyboard(position_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Actions for managing a single open position."""
    keyboard = [
        [
            InlineKeyboardButton(t("btn_close_pos", lang), callback_data=f"close_pos:{position_id}")
        ],
        [
            InlineKeyboardButton(t("btn_back_positions", lang), callback_data="menu_positions"),
            InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard(trading_mode: str, risk_percent: float, exchange: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Configuration menu with language switcher."""
    next_mode = "live" if trading_mode == "paper" else "paper"
    switch_label = t("settings_btn_switch_mode", lang, mode=next_mode.upper())
    risk_label = t("settings_btn_risk", lang, risk=risk_percent)
    exchange_label = t("settings_btn_exchange", lang, ex=exchange.upper())
    reset_label = t("settings_btn_reset_paper", lang)
    lang_btn_text = "🌐 Język: 🇵🇱 Polski" if not lang.startswith("pl") else "🌐 Language: 🇬🇧 English"

    keyboard = [
        [
            InlineKeyboardButton(switch_label, callback_data=f"set_mode:{next_mode}")
        ],
        [
            InlineKeyboardButton(risk_label, callback_data="cycle_risk"),
            InlineKeyboardButton(exchange_label, callback_data="cycle_exchange")
        ],
        [
            InlineKeyboardButton(lang_btn_text, callback_data="toggle_language")
        ],
        [
            InlineKeyboardButton(reset_label, callback_data="reset_paper_balance")
        ],
        [
            InlineKeyboardButton(t("btn_back_main", lang), callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Explicit language picker keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en"),
            InlineKeyboardButton("🇵🇱 Polski", callback_data="set_lang:pl")
        ],
        [
            InlineKeyboardButton("🏠 Main Menu / Menu główne", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
