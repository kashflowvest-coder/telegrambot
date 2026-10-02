# 🤖 AI Automated Trading Telegram Bot

A complete, production-ready **AI Automated Crypto Trading Bot** built with Python (`python-telegram-bot`, `ccxt`, and quantitative technical analysis) with **Full Polish (Język polski) & English Bilingual Support**.

---

## 🌟 Key Features

### 1. 🌐 Full Bilingual Support (English 🇬🇧 & Polski 🇵🇱)
- **Instant Language Switching**: Toggle between English and Polish anytime via Settings, the `/lang` or `/language` command, or directly on the web dashboard `[🇬🇧 EN | 🇵🇱 PL]`.
- **Localized Technical Rationale & Verdicts**: All AI signals, verdicts (*SILNY ZAKUP / STRONG BUY*, *SPRZEDAŻ / SELL*), RSI/MACD/Bollinger explanations, target alerts, and portfolio stats display in the user's preferred language.
- **Persistent User Language**: Preferences are stored per user in SQLite (`users.language`).

### 2. 📊 AI Market Analysis & Signal Engine
- **Multi-Factor Quantitative Reasoning**: Evaluates RSI (14), MACD crossovers, Bollinger Band compressions, 20/50/200 EMA trends, and volume expansion spikes.
- **Dynamic Risk Management**: Calculates precise **Entry Price**, **Take Profit 1 (50% target)**, **Take Profit 2 (Runners)**, and **ATR-based Stop Loss**.
- **Confidence Scoring**: Computes a probabilistic confidence score (0% to 100%) and provides clear, human-readable rationale bullet points.
- **Optional LLM Integration**: Can plug into OpenAI or Gemini for macroeconomic synthesis.

### 3. 📱 Interactive Telegram UI
- **Inline Keyboards**: One-tap trading menus without typing long commands.
- **Real-Time Portfolio Tracking**: View live cash balance, open risk exposure, realized PnL, and win-rate percentage.
- **Active Trades Manager**: Track live unrealized PnL with green/red badges and close positions at market price with a single tap.

### 4. ⚡ Automated Trade Execution
- **🧪 Paper Trading Mode (Default)**: Practice with **$10,000.00 virtual USDT** using live Binance market prices. Zero financial risk.
- **⚡ Live Trading Mode**: Connect your Binance, Bybit, or OKX API keys to execute real exchange orders.
- **Automated Take Profit & Stop Loss**: Continuous background worker monitors all active positions and auto-closes trades when targets or stop losses are hit.
- **Autonomous AI Auto-Trading**: When toggled ON, the AI scanner automatically opens trades whenever confidence exceeds 72%.

### 5. 👑 Multi-User, Security & Admin Support
- **OTP Verification**: 6-digit One-Time Password verification workflow (`/verify` and `/otp <code>`).
- **Crypto Deposits**: Direct deposit flow with TXID submission and admin approval (`/deposit`).
- **Admin Dashboard**: Dedicated `/admin` dashboard for administrators to view platform-wide statistics, approve deposits, and manage wallets.

---

## 📁 Project Architecture

```
ai-trading-bot/
├── config.py                 # Loads settings, environment variables, pairs & timeframes
├── database.py               # SQLite schema (users, positions, signals, trade logs, languages)
├── i18n.py                   # Bilingual English & Polish translation system
├── market_data.py            # CCXT live price ticker & OHLCV candle fetcher
├── technical_analysis.py     # RSI, MACD, Bollinger Bands, ATR, EMA, Support/Resistance
├── ai_engine.py              # Multi-factor quantitative AI reasoning & LLM synthesis
├── trading_engine.py         # Paper & live order execution, SL/TP monitoring loop
├── bot_keyboards.py          # Telegram inline buttons and menus with bilingual support
├── bot_handlers.py           # Telegram command & callback query handlers
├── bot.py                    # Main Telegram bot runner & background monitoring worker
├── simulate_demo.py          # Standalone CLI test & verification script (EN + PL)
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
├── web_dashboard/            # Visual web command center & Telegram simulator
│   └── index.html
└── README.md
```

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### Step 2: Test Immediately with the Built-in Simulator
You can test the entire trading engine, live price feeds, indicator calculations, AI signals, paper trading, and Polish localization without needing a Telegram token right away:
```bash
py simulate_demo.py
```

### Step 3: Connect Your Telegram Bot
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the instructions to create your bot name and username (e.g. `MyAITrading_bot`).
3. Copy the HTTP API token provided by BotFather.
4. Create a `.env` file in the project folder (or copy `.env.example` to `.env`):
   ```bash
   copy .env.example .env
   ```
5. Open `.env` and paste your token:
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

### Step 4: Run the Bot
```bash
py bot.py
```
Open Telegram, search for your bot's username, and send `/start`!

---

## 💬 Telegram Bot Commands

| Command | English Description | Opis w języku polskim |
|---|---|---|
| `/start` | Open the main dashboard & interactive menus | Otwórz główny panel bota i menu |
| `/lang [en\|pl]` | Switch language between English and Polish | Zmień język na Polski lub Angielski |
| `/signal [PAIR]` | Run AI quantitative market scan | Skanuj rynek w poszukiwaniu sygnałów AI |
| `/portfolio` | View cash balance, open risk exposure, PnL | Sprawdź saldo, otwarte pozycje i zysk |
| `/positions` | View active open trades with 1-tap close | Podgląd i zamykanie aktywnych zleceń |
| `/verify` | Request 6-digit OTP security code | Wygeneruj kod OTP weryfikacji konta |
| `/otp <code>` | Authenticate account with OTP | Potwierdź konto kodem OTP |
| `/deposit` | View crypto deposit addresses & submit TXID | Wyświetl adresy do wpłat i prześlij TXID |
| `/admin` | Platform statistics (Admin only) | Panel administracyjny platformy |

---

## 🌐 Web Dashboard & Interactive Simulator
To preview the Telegram Bot interface, test quick trade execution with leverage sliders, and inspect live Binance charts in your browser:

Open `web_dashboard/index.html` in your web browser.
- **Bilingual Switcher**: Tap `[🇬🇧 EN / 🇵🇱 PL]` at top right to instantly switch the entire interface between English and Polish.
- **Audio Feedback**: Built-in sound effects (synthesized via Web Audio API, zero downloads) with mute toggle 🔊/🔇.
- **Simulate Trades**: Click `+ Simulate Quick Trade` to test custom sizes ($25, $50, $100, $250, $500) and leverage (1x - 20x).
- **Interactive Telegram Mockup**: Tap buttons inside the phone frame to test `/signal`, `/portfolio`, `/positions`, and auto-trading.
