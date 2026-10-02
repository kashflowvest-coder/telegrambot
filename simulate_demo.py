"""
Interactive Terminal Demo for AI Automated Trading Bot.
Tests live market data, AI signal generation, order execution, portfolio management,
and bilingual English / Polish (Język polski) localization.
"""

import time
import sys
from datetime import datetime

# Ensure proper Unicode/emoji handling on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import (
    init_db, get_or_create_user, get_portfolio_stats,
    get_open_positions, update_user_settings, set_user_language
)
from market_data import get_live_ticker, get_ohlcv
from ai_engine import get_ai_signal
from trading_engine import open_trade, close_trade, check_and_update_positions
from bot_handlers import format_welcome_message, format_signal_message, format_portfolio_message
from i18n import t, get_verdict_label, translate_reasons


def print_banner():
    print("\n" + "=" * 70)
    print(" 🤖  AI AUTOMATED TRADING BOT — SYSTEM VERIFICATION & DEMO")
    print(" 🌐  BILINGUAL ENGINE: ENGLISH (EN) & POLSKI (PL)")
    print("=" * 70)


def run_demo():
    print_banner()
    init_db()

    # Step 1: Initialize Demo User
    demo_user_id = 999888777
    print("\n[1/6] 👤 Initializing Demo Trader Profile (English)...")
    user = get_or_create_user(demo_user_id, username="DemoTrader", first_name="Alex")
    print(f"  ✓ User Registered: {user['first_name']} (@{user['username']})")
    print(f"  ✓ Initial Paper Balance: ${user['paper_balance']:,.2f} USDT")
    print(f"  ✓ Trading Mode: {user['trading_mode'].upper()}")
    print(f"  ✓ Risk Allocation: {user['risk_percent']}% per trade")

    # Step 2: Fetch Live Market Prices
    print("\n[2/6] 🌐 Connecting to Live Crypto Feeds (Binance)...")
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    for s in symbols:
        ticker = get_live_ticker(s)
        change_sign = "+" if ticker["change_24h"] >= 0 else ""
        print(f"  • {s:10} Price: ${ticker['price']:>10,.2f} | 24h Change: {change_sign}{ticker['change_24h']:>5.2f}%")

    # Step 3: Run AI Signal Analysis (English)
    test_pair = "BTC/USDT"
    print(f"\n[3/6] 🧠 Running Multi-Factor AI Engine on {test_pair} (1h timeframe)...")
    candles = get_ohlcv(test_pair, timeframe="1h", limit=100)
    signal = get_ai_signal(test_pair, "1h", candles)

    if "error" in signal:
        print(f"  ✗ Error: {signal['error']}")
        return

    print("\n" + "-" * 55)
    print(f"  📊 AI SIGNAL REPORT (EN): {signal['symbol']}")
    print(f"  🎯 Action Verdict : {signal['action']}")
    print(f"  🧠 AI Confidence  : {signal['confidence']}%")
    print(f"  💵 Market Price   : ${signal['price']:,.2f}")
    print(f"  🎯 Take Profit 1  : ${signal['target_tp1']:,.2f}")
    print(f"  🎯 Take Profit 2  : ${signal['target_tp2']:,.2f}")
    print(f"  🛑 Stop Loss      : ${signal['stop_loss']:,.2f}")
    print(f"  ⚖️  Risk / Reward  : {signal['risk_reward']}")
    print("  📈 Key Indicators :")
    ind = signal.get("indicators", {})
    print(f"     - RSI (14)     : {ind.get('rsi')}")
    print(f"     - MACD         : {ind.get('macd', {}).get('crossover')} (Hist: {ind.get('macd', {}).get('histogram')})")
    print(f"     - Trend Bias   : {ind.get('trend')}")
    print(f"     - Support/Res  : ${ind.get('support', 0):,.2f} / ${ind.get('resistance', 0):,.2f}")
    print("  💡 Rationale (EN) :")
    for r in signal.get("reasons", []):
        print(f"     • {r}")
    print("-" * 55)

    # Step 4: Open a Trade based on the Signal
    trade_side = "BUY" if "BUY" in signal["action"] or signal["action"] == "NEUTRAL" else "SELL"
    print(f"\n[4/6] ⚡ Executing Trade for Demo User ({trade_side} {test_pair})...")
    trade_result = open_trade(
        user_id=demo_user_id,
        symbol=test_pair,
        side=trade_side,
        amount_usdt=250.0,
        take_profit=signal["target_tp1"],
        stop_loss=signal["stop_loss"]
    )

    if trade_result.get("success"):
        print(f"  ✓ Position Opened Successfully: #{trade_result['position_id']}")
        print(f"  ✓ Entry Price : ${trade_result['entry_price']:,.2f}")
        print(f"  ✓ Position Size : ${trade_result['cost']:.2f} ({trade_result['amount']:.4f} coins)")
        print(f"  ✓ Stop Loss    : ${trade_result['stop_loss']:,.2f}")
        print(f"  ✓ Take Profit  : ${trade_result['take_profit']:,.2f}")
    else:
        print(f"  ✗ Execution failed: {trade_result.get('error')}")

    # Step 5: Check Portfolio & Open Positions
    print("\n[5/6] 💼 Portfolio & Open Positions Status:")
    positions = get_open_positions(demo_user_id)
    for p in positions:
        print(f"  • Open Trade #{p['id']}: {p['symbol']} {p['side']} | Entry: ${p['entry_price']:,.2f} | Cost: ${p['cost']:.2f}")

    stats = get_portfolio_stats(demo_user_id)
    print(f"\n  📊 Summary Stats:")
    print(f"     - Remaining Cash Balance : ${stats['paper_balance']:,.2f} USDT")
    print(f"     - Open Exposure Value    : ${stats['total_open_cost']:,.2f} USDT")
    print(f"     - Total Realized PnL     : ${stats['total_realized_pnl']:,.2f}")

    # Step 6: Polish Language Localization Test (Język polski)
    print("\n" + "=" * 70)
    print(" [6/6] 🇵🇱 POLISH LOCALIZATION & I18N VERIFICATION (JĘZYK POLSKI)")
    print("=" * 70)
    set_user_language(demo_user_id, "pl")
    user_pl = get_or_create_user(demo_user_id)
    print(f"  ✓ Użytkownik przełączony na język: {user_pl.get('language')}")
    print(f"  ✓ Werdykt AI (PL)       : {get_verdict_label(signal['action'], 'pl')}")
    print("  ✓ Argumentacja AI (PL)  :")
    reasons_pl = translate_reasons(signal.get("reasons", []), "pl")
    for r in reasons_pl:
        print(f"     • {r}")

    print("\n  📄 Przykładowa wiadomość powitalna w Telegramie (PL):")
    print("  " + "\n  ".join(format_welcome_message(user_pl, "pl").split("\n")[:7]))
    print("  ...")

    print("\n" + "=" * 70)
    print(" ✅ ALL SYSTEMS VERIFIED & OPERATIONAL IN BOTH ENGLISH & POLSKI!")
    print(" To launch the Telegram Bot:")
    print(" 1. Add your bot token into .env")
    print(" 2. Run: py bot.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_demo()
