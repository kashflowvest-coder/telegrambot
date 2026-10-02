"""
Internationalization (i18n) & Localization module for AI Automated Trading Bot.
Provides comprehensive English (en) and Polish (pl) translations for all
bot messages, menus, buttons, trading alerts, and technical analysis rationale.
"""

from typing import Dict, Any, Optional

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ------------------ Navigation & Buttons ------------------
    "btn_ai_signals": {
        "en": "📊 AI Signals",
        "pl": "📊 Sygnały AI"
    },
    "btn_portfolio": {
        "en": "💼 Portfolio",
        "pl": "💼 Portfel"
    },
    "btn_active_trades": {
        "en": "📈 Active Trades",
        "pl": "📈 Aktywne pozycje"
    },
    "btn_quick_trade": {
        "en": "⚡ Quick Trade",
        "pl": "⚡ Szybki handel"
    },
    "btn_deposit": {
        "en": "💳 Deposit & Wallets",
        "pl": "💳 Wpłaty i portfele"
    },
    "btn_settings": {
        "en": "⚙️ Settings",
        "pl": "⚙️ Ustawienia"
    },
    "btn_autotrade_active": {
        "en": "🤖 Auto-Trade: 🟢 ACTIVE",
        "pl": "🤖 Auto-handel: 🟢 AKTYWNY"
    },
    "btn_autotrade_paused": {
        "en": "🤖 Auto-Trade: 🔴 PAUSED",
        "pl": "🤖 Auto-handel: 🔴 WSTRZYMANY"
    },
    "btn_refresh": {
        "en": "🔄 Refresh Status",
        "pl": "🔄 Odśwież status"
    },
    "btn_guide": {
        "en": "📖 Guide & Help",
        "pl": "📖 Poradnik i pomoc"
    },
    "btn_admin": {
        "en": "👑 Admin Dashboard",
        "pl": "👑 Panel admina"
    },
    "btn_verify_urgent": {
        "en": "🔐 VERIFY ACCOUNT (OTP REQUIRED)",
        "pl": "🔐 ZWERYFIKUJ KONTO (WYMAGANE OTP)"
    },
    "btn_main_menu": {
        "en": "🏠 Main Menu",
        "pl": "🏠 Menu główne"
    },
    "btn_back_main": {
        "en": "🔙 Main Menu",
        "pl": "🔙 Menu główne"
    },
    "btn_back_admin": {
        "en": "🔙 Back to Admin",
        "pl": "🔙 Powrót do admina"
    },
    "btn_back_positions": {
        "en": "🔙 Back to Positions",
        "pl": "🔙 Powrót do pozycji"
    },
    "btn_close_pos": {
        "en": "🛑 Close Position Market",
        "pl": "🛑 Zamknij po cenie rynkowej"
    },
    "btn_reanalyze": {
        "en": "🔄 Re-Analyze",
        "pl": "🔄 Ponowna analiza"
    },
    "btn_other_pairs": {
        "en": "📊 Other Pairs",
        "pl": "📊 Inne pary"
    },
    "btn_cancel": {
        "en": "❌ Cancel",
        "pl": "❌ Anuluj"
    },
    "btn_language": {
        "en": "🌐 Language: 🇬🇧 English",
        "pl": "🌐 Język: 🇵🇱 Polski"
    },
    "btn_verify_activate": {
        "en": "✅ Verify & Activate",
        "pl": "✅ Zweryfikuj & Aktywuj"
    },
    "verification_prompt": {
        "en": "🔐 *One-time Verification*\nTap the button below to verify & activate your bot.",
        "pl": "🔐 *Jednorazowa Weryfikacja*\nDotknij poniższego przycisku, aby zweryfikować i aktywować bota."
    },
    "verification_welcome": {
        "en": "Welcome back! Choose an option:",
        "pl": "Witaj ponownie! Wybierz opcję:"
    },
    "deposit_cart_prompt": {
        "en": "🛒 *Deposit cart*\n\nEnter the USD amount you want to deposit.\nMinimum: $ 100.00 usd\n\nExample: `150` or `$150`",
        "pl": "🛒 *Koszyk wpłaty*\n\nWprowadź kwotę w USD, którą chcesz wpłacić.\nMinimum: $ 100.00 usd\n\nPrzykład: `150` lub `$150`"
    },
    "user_reviews_content": {
        "en": "⭐️⭐️⭐️⭐️⭐️ *VERIFIED TRADER REVIEWS & TESTIMONIALS*\n━━━━━━━━━━━━━━━━━━━━━━\n⭐️⭐️⭐️⭐️⭐️ *\"Deposited $500 3 weeks ago, currently at $1,280. The AI auto-trading signals on BTC and ETH are super accurate!\"*\n— *Alexander K.* (Verified VIP Trader) • +156% ROI\n\n⭐️⭐️⭐️⭐️⭐️ *\"Fast withdrawals. Took out $350 in USDT TRC20 and it arrived in 5 minutes.\"*\n— *Elena R.* (Active Investor) • +92% ROI\n\n⭐️⭐️⭐️⭐️⭐️ *\"Best automated crypto bot I've used. Clean UI and solid risk management.\"*\n— *Michael T.* (Institutional Trader) • +118% ROI\n\n⭐️⭐️⭐️⭐️⭐️ *\"The automated stop loss protected my funds during the market dip. 10/10 algorithm.\"*\n— *Piotr W.* (Verified Trader) • +74% ROI\n━━━━━━━━━━━━━━━━━━━━━━\n🌟 *Platform Rating:* `4.92 / 5.0 (2,410+ Verified Reviews)`",
        "pl": "⭐️⭐️⭐️⭐️⭐️ *OPINIE I REFERENCJE ZWERYFIKOWANYCH TRADERÓW*\n━━━━━━━━━━━━━━━━━━━━━━\n⭐️⭐️⭐️⭐️⭐️ *\"Wpłaciłem $500 3 tygodnie temu, obecnie mam $1,280. Sygnały AI na BTC i ETH są niezwykle precyzyjne!\"*\n— *Aleksander K.* (Zweryfikowany Trader VIP) • +156% ROI\n\n⭐️⭐️⭐️⭐️⭐️ *\"Błyskawiczne wypłaty. Wypłaciłam $350 w USDT TRC20 i środki dotarły w 5 minut.\"*\n— *Elena R.* (Aktywny Inwestor) • +92% ROI\n\n⭐️⭐️⭐️⭐️⭐️ *\"Najlepszy bot do kryptowalut, jakiego używałem. Świetny interfejs i zarządzanie ryzykiem.\"*\n— *Michał T.* (Trader Instytucjonalny) • +118% ROI\n━━━━━━━━━━━━━━━━━━━━━━\n🌟 *Średnia ocena platformy:* `4.92 / 5.0 (2,410+ Zweryfikowanych opinii)`"
    },
    "profit_calculator_content": {
        "en": "📊 *AI AUTOMATED PROFIT CALCULATOR*\n━━━━━━━━━━━━━━━━━━━━━━\nOur institutional quantitative AI engine generates an average return of *1.5% to 3.2% daily* using multi-factor algorithmic execution and strict risk control.\n\n💰 *Estimated Returns by Investment Tier:*\n\n🥉 *Starter Tier ($100 - $499)*\n• Average: *1.8% daily*\n• 7 Days: `~$113.50` (+13.5%)\n• 30 Days: `~$170.00` (+70.0%)\n\n🥈 *Advanced Tier ($500 - $1,999)*\n• Average: *2.2% daily*\n• 7 Days: `~$582.00` (+16.4%)\n• 30 Days: `~$960.00` (+92.0%)\n\n🥇 *Pro Trader Tier ($2,000 - $4,999)*\n• Average: *2.7% daily*\n• 7 Days: `~$2,410.00` (+20.5%)\n• 30 Days: `~$4,420.00` (+121.0%)\n\n💎 *VIP Whale Tier ($5,000+)*\n• Average: *3.2% daily*\n• 7 Days: `~$6,240.00` (+24.8%)\n• 30 Days: `~$12,850.00` (+157.0%)\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *All trading utilizes automated Stop-Loss (Max 2% capital risk per trade).*",
        "pl": "📊 *KALKULATOR ZYSKÓW AI*\n━━━━━━━━━━━━━━━━━━━━━━\nNasz instytucjonalny silnik ilościowy AI generuje średni zwrot na poziomie *1.5% do 3.2% dziennie* przy użyciu algorytmów wieloczynnikowych i ścisłej kontroli ryzyka.\n\n💰 *Szacowane zyski według poziomów inwestycji:*\n\n🥉 *Poziom Starter ($100 - $499)*\n• Średnio: *1.8% dziennie*\n• 7 Dni: `~$113.50` (+13.5%)\n• 30 Dni: `~$170.00` (+70.0%)\n\n🥈 *Poziom Advanced ($500 - $1,999)*\n• Średnio: *2.2% dziennie*\n• 7 Dni: `~$582.00` (+16.4%)\n• 30 Dni: `~$960.00` (+92.0%)\n\n🥇 *Poziom Pro ($2,000 - $4,999)*\n• Średnio: *2.7% dziennie*\n• 7 Dni: `~$2,410.00` (+20.5%)\n• 30 Dni: `~$4,420.00` (+121.0%)\n\n💎 *Poziom VIP Whale ($5,000+)*\n• Średnio: *3.2% dziennie*\n• 7 Dni: `~$6,240.00` (+24.8%)\n• 30 Dni: `~$12,850.00` (+157.0%)\n━━━━━━━━━━━━━━━━━━━━━━\n💡 *Wszystkie transakcje chronione są automatycznym Stop-Loss (maks. 2% ryzyka kapitału).*"
    },
    "how_it_works_content": {
        "en": "📖 *HOW THE AI AUTOMATED BOT WORKS*\n━━━━━━━━━━━━━━━━━━━━━━\n1️⃣ *Deposit & Activate* 💰\nChoose your preferred crypto network (USDT TRC20, BEP20, BTC, SOL, TON). Minimum deposit is $100.00 USD. Funds credit automatically to your trading balance.\n\n2️⃣ *AI Quantitative Market Scanning* 🧠\nThe bot's neural engine analyzes 15+ technical indicators (RSI-14, MACD Crossovers, Bollinger Squeezes, EMA trend alignments) across top tier exchanges (Binance, Bybit, OKX).\n\n3️⃣ *Autonomous Order Execution* ⚡\nWhen trade confidence exceeds 72%, the bot enters high-probability positions with calibrated 1:2 Risk/Reward ratios, dynamic Take-Profit targets, and trailing Stop-Losses.\n\n4️⃣ *Daily Compounding & Instant Withdrawals* 🕊️\nEarnings compound continuously in your portfolio. You can withdraw your earnings or initial deposit anytime directly to your personal crypto wallet with 0% platform fee.\n━━━━━━━━━━━━━━━━━━━━━━",
        "pl": "📖 *JAK DZIAŁA BOT HANDLOWY AI*\n━━━━━━━━━━━━━━━━━━━━━━\n1️⃣ *Wpłata i Aktywacja* 💰\nWybierz preferowaną sieć kryptowalut (USDT TRC20, BEP20, BTC, SOL, TON). Minimalna wpłata to $100.00 USD. Środki trafiają bezpośrednio na Twoje saldo handlowe.\n\n2️⃣ *Ilościowe Skanowanie Rynku przez AI* 🧠\nAlgorytm analizuje ponad 15 wskaźników technicznych (RSI-14, przecięcia MACD, wstęgi Bollingera, EMA) na giełdach Binance, Bybit i OKX.\n\n3️⃣ *Autonomiczna Realizacja Zleceń* ⚡\nGdy wiarygodność przekracza 72%, bot otwiera pozycje zoptymalizowane pod kątem zysku/ryzyka (1:2), Take-Profit i Stop-Loss.\n\n4️⃣ *Dzienny Procent Składany i Błyskawiczne Wypłaty* 🕊️\nZyski są natychmiast dopisywane do salda. Możesz wypłacić środki w dowolnym momencie bez prowizji platformy.\n━━━━━━━━━━━━━━━━━━━━━━"
    },
    "live_support_content": {
        "en": "💬 *24/7 LIVE SUPPORT & TRADING DESK*\n━━━━━━━━━━━━━━━━━━━━━━\nOur dedicated technical support team and trading desk are standing by 24/7 to assist you with deposits, withdrawals, verification, or questions.\n\n• *Live Support Desk:* @KELVIN\_ADMIN\_SUPPORT\n• *VIP Trader Desk:* @AITradingDesk\n• *Verification Team:* @BotVerificationDesk\n• *Average Response Time:* `< 5 minutes`\n\nClick the button below to connect with an agent:",
        "pl": "💬 *WSPARCIE NA ŻYWO & DESK HANDLOWY 24/7*\n━━━━━━━━━━━━━━━━━━━━━━\nNasz zespół wsparcia i traderzy są do Twojej dyspozycji 24/7 w sprawach wpłat, wypłat, weryfikacji i pytań technicznych.\n\n• *Oficjalne Wsparcie:* @KELVIN\_ADMIN\_SUPPORT\n• *Desk VIP:* @AITradingDesk\n• *Dział Weryfikacji:* @BotVerificationDesk\n• *Średni czas odpowiedzi:* `< 5 minut`"
    },
    "about_us_content": {
        "en": "🏛️ *ABOUT AI AUTOMATED TRADING*\n━━━━━━━━━━━━━━━━━━━━━━\nFounded by institutional algorithmic quantitative traders and AI researchers, AI Automated Trading brings Wall Street level algorithmic execution to digital asset investors.\n\n• *Strategy:* Multi-factor quantitative momentum & mean-reversion\n• *Exchanges:* Direct API low-latency connectivity to Binance, Bybit, OKX\n• *Security:* Cold storage address management, non-custodial API options, automated ATR risk containment\n• *Performance:* Over 24 months of verified backtested and live market profitability",
        "pl": "🏛️ *O NAS — AI AUTOMATED TRADING*\n━━━━━━━━━━━━━━━━━━━━━━\nStworzona przez traderów ilościowych i inżynierów sztucznej inteligencji, platforma dostarcza algorytmiczne strategie klasy instytucjonalnej na rynki kryptowalut.\n\n• *Strategia:* Ilościowy momentum i powrót do średniej\n• *Giełdy:* Bezpośrednia łączność API o niskim opóźnieniu z Binance, Bybit, OKX\n• *Bezpieczeństwo:* Ochrona kapitału Stop-Loss ATR, bezpieczne portfele\n• *Doświadczenie:* Ponad 24 miesiące zweryfikowanej rentowności w warunkach rynkowych"
    },
    "faq_content": {
        "en": "ℹ️ *FREQUENTLY ASKED QUESTIONS (FAQ)*\n━━━━━━━━━━━━━━━━━━━━━━\n*Q: What is the minimum deposit?*\nA: The minimum deposit is $100.00 USD. You can deposit in USDT (TRC20/BEP20), BTC, SOL, or TON.\n\n*Q: How fast are withdrawals processed?*\nA: Withdrawals are processed within 5 to 30 minutes.\n\n*Q: Are there any withdrawal fees?*\nA: No, 0% platform fee. Only standard blockchain network gas fees apply.\n\n*Q: How does the AI protect my balance?*\nA: Every trade has a mandatory Stop-Loss strictly capped at 2% risk of your account balance. The bot never risks excessive drawdown.\n\n*Q: Can I withdraw my initial deposit?*\nA: Yes, both profits and initial deposit can be withdrawn at any time.",
        "pl": "ℹ️ *NAJCZĘŚCIEJ ZADAWANE PYTANIA (FAQ)*\n━━━━━━━━━━━━━━━━━━━━━━\n*P: Jaka jest minimalna kwota wpłaty?*\nO: Minimalna wpłata to $100.00 USD (w USDT TRC20/BEP20, BTC, SOL lub TON).\n\n*P: Jak szybko realizowane są wypłaty?*\nO: Wypłaty są przetwarzane w ciągu 5 do 30 minut.\n\n*P: Czy są pobierane prowizje od wypłat?*\nO: Nie, prowizja platformy wynosi 0%. Obowiązują jedynie standardowe opłaty sieci blockchain (gas fee).\n\n*P: Jak AI chroni moje środki?*\nO: Każde zlecenie posiada automatyczny Stop-Loss ograniczający ryzyko do maksymalnie 2% salda na transakcję.\n\n*P: Czy mogę wypłacić wpłacony kapitał w dowolnej chwili?*\nO: Tak, zarówno wypracowany zysk, jak i kapitał początkowy można wypłacić w dowolnym momencie."
    },
    "withdraw_prompt": {
        "en": "🕊️ *WITHDRAW FUNDS*\n━━━━━━━━━━━━━━━━━━━━━━\n• *Available Balance:* `${balance:,.2f} USD`\n• *Minimum Withdrawal:* `$50.00 USD`\n• *Platform Fee:* `0% (Free)`\n• *Average Processing Time:* `5 - 30 minutes`\n\nTo submit a withdrawal, send the command:\n`/withdraw <AMOUNT> <NETWORK> <WALLET_ADDRESS>`\n\n*Example:*\n`/withdraw 150 USDT_TRC20 TXYZ1234567890ABCDEF`",
        "pl": "🕊️ *WYPŁATA ŚRODKÓW*\n━━━━━━━━━━━━━━━━━━━━━━\n• *Dostępne saldo:* `${balance:,.2f} USD`\n• *Minimalna wypłata:* `$50.00 USD`\n• *Prowizja platformy:* `0% (Darmowa)`\n• *Czas realizacji:* `5 - 30 minut`\n\nAby zlecić wypłatę, wpisz polecenie:\n`/withdraw <KWOTA> <SIEĆ> <ADRES_PORTFELA>`\n\n*Przykład:*\n`/withdraw 150 USDT_TRC20 TXYZ1234567890ABCDEF`"
    },

    # ------------------ Welcome Message ------------------
    "welcome_title": {
        "en": "🤖 *AI AUTOMATED TRADING BOT*",
        "pl": "🤖 *BOT HANDLOWY AI*"
    },
    "welcome_greeting": {
        "en": "👋 Welcome, *{name}*!",
        "pl": "👋 Witaj, *{name}*!"
    },
    "welcome_verification": {
        "en": "• *Verification:* `{status}`",
        "pl": "• *Weryfikacja:* `{status}`"
    },
    "welcome_mode": {
        "en": "• *Trading Mode:* `{mode}`",
        "pl": "• *Tryb handlu:* `{mode}`"
    },
    "welcome_balance": {
        "en": "• *Balance:* `{balance}`",
        "pl": "• *Saldo:* `{balance}`"
    },
    "welcome_auto": {
        "en": "• *Auto-Execution:* `{status}`",
        "pl": "• *Auto-wykonywanie:* `{status}`"
    },
    "welcome_risk": {
        "en": "• *Risk Profile:* `{risk}% per trade`",
        "pl": "• *Profil ryzyka:* `{risk}% na transakcję`"
    },
    "welcome_exchange": {
        "en": "• *Active Exchange:* `{exchange}`",
        "pl": "• *Aktywna giełda:* `{exchange}`"
    },
    "welcome_prompt": {
        "en": "💡 *What would you like to do?*\nTap the buttons below to generate AI signals, deposit funds, or manage your portfolio.",
        "pl": "💡 *Co chciałbyś zrobić?*\nDotknij poniższych przycisków, aby generować sygnały AI, wpłacać środki lub zarządzać portfelem."
    },
    "badge_verified": {
        "en": "🟢 VERIFIED",
        "pl": "🟢 ZWERYFIKOWANY"
    },
    "badge_unverified": {
        "en": "🔴 UNVERIFIED (OTP Required)",
        "pl": "🔴 NIEZWERYFIKOWANY (Wymagane OTP)"
    },
    "badge_active": {
        "en": "🟢 ACTIVE",
        "pl": "🟢 AKTYWNY"
    },
    "badge_paused": {
        "en": "🔴 PAUSED",
        "pl": "🔴 WSTRZYMANY"
    },
    "badge_paper": {
        "en": "🧪 PAPER TRADING (DEMO)",
        "pl": "🧪 HANDEL DEMO (PAPIEROWY)"
    },
    "badge_live": {
        "en": "⚡ LIVE TRADING (REAL)",
        "pl": "⚡ HANDEL RZECZYWISTY (LIVE)"
    },

    # ------------------ AI Signals ------------------
    "signal_title": {
        "en": "📊 *AI MARKET SIGNAL: {symbol}* ({timeframe})",
        "pl": "📊 *SYGNAŁ RYNKOWY AI: {symbol}* ({timeframe})"
    },
    "signal_verdict": {
        "en": "🎯 *VERDICT:* {verdict}",
        "pl": "🎯 *WERDYKT:* {verdict}"
    },
    "signal_confidence": {
        "en": "🧠 *AI Confidence:* `{conf}%`",
        "pl": "🧠 *Wiarygodność AI:* `{conf}%`"
    },
    "signal_price": {
        "en": "💵 *Current Price:* `${price:,.2f}`",
        "pl": "💵 *Aktualna cena:* `${price:,.2f}`"
    },
    "signal_targets_header": {
        "en": "🎯 *TARGETS & RISK MANAGEMENT:*",
        "pl": "🎯 *CELE I ZARZĄDZANIE RYZYKIEM:*"
    },
    "signal_tp1": {
        "en": "• *Take Profit 1:* `${tp1:,.2f}` (`{diff:+.2f}%`)",
        "pl": "• *Take Profit 1:* `${tp1:,.2f}` (`{diff:+.2f}%`)"
    },
    "signal_tp2": {
        "en": "• *Take Profit 2:* `${tp2:,.2f}` (`{diff:+.2f}%`)",
        "pl": "• *Take Profit 2:* `${tp2:,.2f}` (`{diff:+.2f}%`)"
    },
    "signal_sl": {
        "en": "• *Stop Loss:* `${sl:,.2f}` (`{diff:+.2f}%`)",
        "pl": "• *Stop Loss:* `${sl:,.2f}` (`{diff:+.2f}%`)"
    },
    "signal_rr": {
        "en": "• *Risk/Reward:* `{rr}`",
        "pl": "• *Stosunek zysku do ryzyka:* `{rr}`"
    },
    "signal_tech_header": {
        "en": "📈 *TECHNICAL METRICS:*",
        "pl": "📈 *WSKAŹNIKI TECHNICZNE:*"
    },
    "signal_rsi": {
        "en": "• *RSI (14):* `{val}`",
        "pl": "• *RSI (14):* `{val}`"
    },
    "signal_macd": {
        "en": "• *MACD:* `{cross}` (`{hist:+}`)",
        "pl": "• *MACD:* `{cross}` (`{hist:+}`)"
    },
    "signal_trend": {
        "en": "• *Trend:* `{trend}`",
        "pl": "• *Trend:* `{trend}`"
    },
    "signal_bb": {
        "en": "• *Bollinger %B:* `{bb}`",
        "pl": "• *Bollinger %B:* `{bb}`"
    },
    "signal_vol": {
        "en": "• *Volume Spike:* `{vol}x`",
        "pl": "• *Skok wolumenu:* `{vol}x`"
    },
    "signal_rationale_header": {
        "en": "💡 *AI RATIONALE:*",
        "pl": "💡 *ARGUMENTACJA AI:*"
    },
    "signal_action_footer": {
        "en": "⚡ _Use buttons below to execute this trade or analyze another pair._",
        "pl": "⚡ _Użyj poniższych przycisków, aby zrealizować transakcję lub wybrać inną parę._"
    },
    "signal_select_pair": {
        "en": "📊 *Select a cryptocurrency pair to generate AI trading signal:*",
        "pl": "📊 *Wybierz parę kryptowalutową do analizy sygnału AI:*"
    },

    # ------------------ Verdict Translations ------------------
    "verdict_strong_buy": {
        "en": "🚀 *STRONG BUY*",
        "pl": "🚀 *SILNY ZAKUP (STRONG BUY)*"
    },
    "verdict_buy": {
        "en": "🟢 *BUY / LONG*",
        "pl": "🟢 *ZAKUP / LONG*"
    },
    "verdict_neutral": {
        "en": "⚪ *NEUTRAL / WAIT*",
        "pl": "⚪ *NEUTRALNIE / CZEKAJ*"
    },
    "verdict_sell": {
        "en": "🔴 *SELL / SHORT*",
        "pl": "🔴 *SPRZEDAŻ / SHORT*"
    },
    "verdict_strong_sell": {
        "en": "💥 *STRONG SELL*",
        "pl": "💥 *SILNA SPRZEDAŻ (STRONG SELL)*"
    },

    # ------------------ Portfolio ------------------
    "portfolio_title": {
        "en": "💼 *TRADING PORTFOLIO & PERFORMANCE*",
        "pl": "💼 *PORTFEL HANDLOWY I WYNIKI*"
    },
    "portfolio_mode": {
        "en": "• *Trading Mode:* `{mode}`",
        "pl": "• *Tryb handlu:* `{mode}`"
    },
    "portfolio_balance": {
        "en": "• *Cash Balance:* `${bal:,.2f} USDT`",
        "pl": "• *Dostępne saldo:* `${bal:,.2f} USDT`"
    },
    "portfolio_exposure": {
        "en": "• *Open Exposure:* `${exp:,.2f} USDT`",
        "pl": "• *Aktywna ekspozycja:* `${exp:,.2f} USDT`"
    },
    "portfolio_autotrade": {
        "en": "• *Auto-Trading:* `{status}`",
        "pl": "• *Auto-handel:* `{status}`"
    },
    "portfolio_perf_header": {
        "en": "🏆 *PERFORMANCE METRICS:*",
        "pl": "🏆 *WSKAŹNIKI WYNIKÓW:*"
    },
    "portfolio_realized_pnl": {
        "en": "• *Realized PnL:* `{sign}${pnl:,.2f}`",
        "pl": "• *Zrealizowany PnL:* `{sign}${pnl:,.2f}`"
    },
    "portfolio_win_rate": {
        "en": "• *Win Rate:* `{wr}%`",
        "pl": "• *Skuteczność (Win Rate):* `{wr}%`"
    },
    "portfolio_closed_trades": {
        "en": "• *Total Closed Trades:* `{total}`",
        "pl": "• *Zamknięte transakcje:* `{total}`"
    },
    "portfolio_wins_losses": {
        "en": "  └ ✅ Wins: `{wins}` | ❌ Losses: `{losses}`",
        "pl": "  └ ✅ Wygrane: `{wins}` | ❌ Przegrane: `{losses}`"
    },
    "portfolio_open_count": {
        "en": "• *Active Open Positions:* `{count}`",
        "pl": "• *Aktywne otwarte pozycje:* `{count}`"
    },
    "portfolio_footer": {
        "en": "💡 _Tip: Switch between Paper and Live mode anytime in Settings._",
        "pl": "💡 _Wskazówka: W każdej chwili możesz zmienić tryb Demo/Live w Ustawieniach._"
    },

    # ------------------ Positions ------------------
    "positions_title": {
        "en": "📈 *ACTIVE OPEN POSITIONS*",
        "pl": "📈 *AKTYWNE OTWARTE POZYCJE*"
    },
    "positions_none": {
        "en": "📈 *ACTIVE POSITIONS*\n━━━━━━━━━━━━━━━━━━━━━━\n_No open positions currently._\nUse *Quick Trade* or *AI Signals* to open one!",
        "pl": "📈 *AKTYWNE POZYCJE*\n━━━━━━━━━━━━━━━━━━━━━━\n_Brak otwartych pozycji._\nUżyj *Szybki handel* lub *Sygnały AI*, aby otworzyć nową pozycję!"
    },
    "positions_footer": {
        "en": "Tap a button below to close an individual trade instantly at market price.",
        "pl": "Dotknij poniższego przycisku, aby natychmiast zamknąć pozycję po cenie rynkowej."
    },
    "pos_entry_now": {
        "en": "  • Entry: `${entry:,.2f}` ➔ Now: `${now:,.2f}`",
        "pl": "  • Wejście: `${entry:,.2f}` ➔ Teraz: `${now:,.2f}`"
    },
    "pos_size": {
        "en": "  • Size: `${cost:.2f}` ({amount:.4f})",
        "pl": "  • Wielkość: `${cost:.2f}` ({amount:.4f})"
    },
    "pos_pnl": {
        "en": "  • PnL: {badge} `{pnl:+.2f} USDT ({pct:+.2f}%)`",
        "pl": "  • PnL: {badge} `{pnl:+.2f} USDT ({pct:+.2f}%)`"
    },
    "pos_tp_sl": {
        "en": "  • TP: `${tp:,.2f}` | SL: `${sl:,.2f}`",
        "pl": "  • TP: `${tp:,.2f}` | SL: `${sl:,.2f}`"
    },
    "pos_close_btn": {
        "en": "🛑 Close #{pid} {sym} ({pnl:+.1f}$)",
        "pl": "🛑 Zamknij #{pid} {sym} ({pnl:+.1f}$)"
    },

    # ------------------ Settings ------------------
    "settings_title": {
        "en": "⚙️ *BOT CONFIGURATION & SETTINGS*",
        "pl": "⚙️ *KONFIGURACJA I USTAWIENIA BOTA*"
    },
    "settings_mode": {
        "en": "• *Trading Mode:* `{mode}`",
        "pl": "• *Tryb handlu:* `{mode}`"
    },
    "settings_risk": {
        "en": "• *Risk per Trade:* `{risk}%`",
        "pl": "• *Ryzyko na transakcję:* `{risk}%`"
    },
    "settings_exchange": {
        "en": "• *Exchange:* `{exchange}`",
        "pl": "• *Giełda:* `{exchange}`"
    },
    "settings_language": {
        "en": "• *Language:* `{lang}`",
        "pl": "• *Język:* `{lang}`"
    },
    "settings_btn_switch_mode": {
        "en": "🔀 Switch to {mode} Mode",
        "pl": "🔀 Przełącz na tryb {mode}"
    },
    "settings_btn_risk": {
        "en": "Risk: {risk}% (Click to cycle)",
        "pl": "Ryzyko: {risk}% (Kliknij by zmienić)"
    },
    "settings_btn_exchange": {
        "en": "Exchange: {ex}",
        "pl": "Giełda: {ex}"
    },
    "settings_btn_reset_paper": {
        "en": "💳 Reset Paper Balance ($10k)",
        "pl": "💳 Resetuj saldo Demo ($10k)"
    },
    "settings_btn_toggle_lang": {
        "en": "🌐 Język: 🇵🇱 Polski",
        "pl": "🌐 Language: 🇬🇧 English"
    },

    # ------------------ Trade Execution ------------------
    "trade_prep_title": {
        "en": "⚡ *ORDER EXECUTION CONFIRMATION*\n━━━━━━━━━━━━━━━━━━━━━━\n• Pair: `{symbol}`\n• Direction: *{side}*\n• Market Price: `${price:,.2f}`\n\nSelect order size in USDT:",
        "pl": "⚡ *POTWIERDZENIE ZLECENIA HANDLOWEGO*\n━━━━━━━━━━━━━━━━━━━━━━\n• Para: `{symbol}`\n• Kierunek: *{side}*\n• Cena rynkowa: `${price:,.2f}`\n\nWybierz wielkość pozycji w USDT:"
    },
    "trade_success_title": {
        "en": "🚀 *TRADE EXECUTED SUCCESSFULLY!*\n━━━━━━━━━━━━━━━━━━━━━━\n• Position ID: `#{pid}`\n• Pair: `{symbol}` ({side})\n• Entry Price: `${entry:,.2f}`\n• Position Size: `${cost:.2f} USDT` ({amount:.4f})\n• Take Profit: `${tp:,.2f}`\n• Stop Loss: `${sl:,.2f}`\n━━━━━━━━━━━━━━━━━━━━━━\nTrack live updates in /positions.",
        "pl": "🚀 *TRANSAKCJA ZREALIZOWANA POMYŚLNIE!*\n━━━━━━━━━━━━━━━━━━━━━━\n• ID Pozycji: `#{pid}`\n• Para: `{symbol}` ({side})\n• Cena wejścia: `${entry:,.2f}`\n• Wielkość pozycji: `${cost:.2f} USDT` ({amount:.4f})\n• Take Profit: `${tp:,.2f}`\n• Stop Loss: `${sl:,.2f}`\n━━━━━━━━━━━━━━━━━━━━━━\nŚledź wyniki na bieżąco w /positions."
    },
    "trade_close_success": {
        "en": "✅ *POSITION CLOSED SUCCESSFULLY*\n━━━━━━━━━━━━━━━━━━━━━━\n• Position: `#{pid} {symbol}` ({side})\n• Entry Price: `${entry:,.2f}`\n• Exit Price: `${exit:,.2f}`\n• Realized PnL: {badge} `${pnl:+.2f} ({pct:+.2f}%)`\n━━━━━━━━━━━━━━━━━━━━━━\nUpdated balance is visible in /portfolio.",
        "pl": "✅ *POZYCJA ZAMKNIĘTA POMYŚLNIE*\n━━━━━━━━━━━━━━━━━━━━━━\n• Pozycja: `#{pid} {symbol}` ({side})\n• Cena wejścia: `${entry:,.2f}`\n• Cena wyjścia: `${exit:,.2f}`\n• Zrealizowany PnL: {badge} `${pnl:+.2f} ({pct:+.2f}%)`\n━━━━━━━━━━━━━━━━━━━━━━\nZaktualizowane saldo widoczne w /portfolio."
    },

    # ------------------ OTP & Verification ------------------
    "otp_title": {
        "en": "🔐 *SECURITY VERIFICATION — ONE-TIME PASSWORD (OTP)*\n━━━━━━━━━━━━━━━━━━━━━━\nYour verification code is: `{otp}`\n\nTo activate your account, send:\n`/otp {otp}`\n\n⏱ _This OTP is valid for 10 minutes._",
        "pl": "🔐 *WERYFIKACJA BEZPIECZEŃSTWA — KOD JEDNORAZOWY (OTP)*\n━━━━━━━━━━━━━━━━━━━━━━\nTwój kod weryfikacyjny: `{otp}`\n\nAby aktywować konto, wyślij:\n`/otp {otp}`\n\n⏱ _Kod jest ważny przez 10 minut._"
    },
    "otp_success": {
        "en": "🎉 *ACCOUNT VERIFIED SUCCESSFULLY!*\nYour account has been confirmed. Full trading access is now unlocked.",
        "pl": "🎉 *KONTO POMYŚLNIE ZWERYFIKOWANE!*\nTwoje konto zostało zatwierdzone. Pełny dostęp do handlu został odblokowany."
    },
    "otp_invalid": {
        "en": "❌ *Invalid or expired OTP code.* Please request a new one via /verify.",
        "pl": "❌ *Nieprawidłowy lub wygasły kod OTP.* Wygeneruj nowy kod komendą /verify."
    },
    "btn_otp_generate": {
        "en": "📩 Generate New 6-Digit OTP",
        "pl": "📩 Wygeneruj nowy 6-cyfrowy kod OTP"
    },
    "btn_otp_onetap": {
        "en": "⚡ One-Tap Verify ({otp})",
        "pl": "⚡ Zweryfikuj jednym kliknięciem ({otp})"
    },

    # ------------------ Deposit & Wallets ------------------
    "deposit_menu_title": {
        "en": "💳 *DEPOSIT CRYPTO FUNDS*\n━━━━━━━━━━━━━━━━━━━━━━\nSelect network to view deposit address:",
        "pl": "💳 *WPŁATA ŚRODKÓW KRYPTO*\n━━━━━━━━━━━━━━━━━━━━━━\nWybierz sieć, aby wyświetlić adres do wpłaty:"
    },
    "deposit_address_info": {
        "en": "📥 *DEPOSIT TO {network}*\n━━━━━━━━━━━━━━━━━━━━━━\n• Address: `{address}`\n{memo_line}\n⚠️ *Send only assets on the {network} network to this address.*\n\nAfter sending, tap *Submit Deposit Proof* below.",
        "pl": "📥 *WPŁATA W SIECI {network}*\n━━━━━━━━━━━━━━━━━━━━━━\n• Adres: `{address}`\n{memo_line}\n⚠️ *Wysyłaj wyłącznie środki w sieci {network} na ten adres.*\n\nPo dokonaniu wpłaty kliknij poniżej *Prześlij potwierdzenie (TXID)*."
    },
    "btn_deposit_proof": {
        "en": "📤 Submit Deposit Proof (TXID)",
        "pl": "📤 Prześlij potwierdzenie (TXID)"
    },
    "deposit_submit_help": {
        "en": "📤 *SUBMIT DEPOSIT TRANSACTION PROOF*\n━━━━━━━━━━━━━━━━━━━━━━\nSend deposit details in this format:\n`/deposit <NETWORK> <AMOUNT> <TXID>`\n\nExample:\n`/deposit USDT_TRC20 500 4a9f3b2...`",
        "pl": "📤 *PRZEŚLIJ POTWIERDZENIE WPŁATY (TXID)*\n━━━━━━━━━━━━━━━━━━━━━━\nWyślij szczegóły wpłaty w formacie:\n`/deposit <SIEĆ> <KWOTA> <TXID>`\n\nPrzykład:\n`/deposit USDT_TRC20 500 4a9f3b2...`"
    },
    "deposit_submitted_ack": {
        "en": "✅ *Deposit Request Submitted!*\nID: `#{id}` | Amount: `{amount}` {network}\nOur team/admin will verify the on-chain transaction shortly.",
        "pl": "✅ *Zgłoszenie wpłaty zostało przyjęte!*\nID: `#{id}` | Kwota: `{amount}` {network}\nAdministrator zweryfikuje transakcję w blockchainie."
    },

    # ------------------ Trade Alerts & Background ------------------
    "alert_tp_title": {
        "en": "🎯 TAKE PROFIT REACHED",
        "pl": "🎯 OSIĄGNIĘTO TAKE PROFIT"
    },
    "alert_sl_title": {
        "en": "🛑 STOP LOSS TRIGGERED",
        "pl": "🛑 AKTYWOWANO STOP LOSS"
    },
    "alert_trade_header": {
        "en": "🚨 *TRADE ALERT: {status}*\n━━━━━━━━━━━━━━━━━━━━━━\n• Pair: `{symbol}` ({side})\n• Entry: `${entry:,.2f}`\n• Exit: `${exit:,.2f}`\n• Realized PnL: {badge} `${pnl:+.2f} ({pct:+.2f}%)`\n━━━━━━━━━━━━━━━━━━━━━━\nCheck your /portfolio for updated balance.",
        "pl": "🚨 *ALERT HANDLOWY: {status}*\n━━━━━━━━━━━━━━━━━━━━━━\n• Para: `{symbol}` ({side})\n• Wejście: `${entry:,.2f}`\n• Wyjście: `${exit:,.2f}`\n• Zrealizowany PnL: {badge} `${pnl:+.2f} ({pct:+.2f}%)`\n━━━━━━━━━━━━━━━━━━━━━━\nSprawdź swój /portfolio, aby zobaczyć zaktualizowane saldo."
    },
    "alert_autotrade_header": {
        "en": "🤖 *AUTO-TRADE EXECUTED BY AI*\n━━━━━━━━━━━━━━━━━━━━━━\n• Pair: `{symbol}` ({side})\n• Entry: `${entry:,.2f}`\n• AI Confidence: `{conf}%`\n• Take Profit: `${tp:,.2f}`\n• Stop Loss: `${sl:,.2f}`\n━━━━━━━━━━━━━━━━━━━━━━\nView details in /positions.",
        "pl": "🤖 *ZLECENIE WYKONANE AUTOMATYCZNIE PRZEZ AI*\n━━━━━━━━━━━━━━━━━━━━━━\n• Para: `{symbol}` ({side})\n• Wejście: `${entry:,.2f}`\n• Wiarygodność AI: `{conf}%`\n• Take Profit: `${tp:,.2f}`\n• Stop Loss: `${sl:,.2f}`\n━━━━━━━━━━━━━━━━━━━━━━\nSzczegóły w zakładce /positions."
    },

    # ------------------ Admin Dashboard ------------------
    "admin_title": {
        "en": "👑 *ADMIN COMMAND DASHBOARD*",
        "pl": "👑 *PANEL DOWODZENIA ADMINISTRATORA*"
    },
    "admin_dashboard_title": {
        "en": "👑 *ADMIN DASHBOARD*\n━━━━━━━━━━━━━━━━━━━━━━\nSelect an action from the panel below:",
        "pl": "👑 *PANEL ADMINISTRATORA*\n━━━━━━━━━━━━━━━━━━━━━━\nWybierz akcję z panelu poniżej:"
    },
    "admin_stats": {
        "en": "• Total Users: `{users}` (Verified: `{verified}`)\n• Open Positions: `{positions}`\n• Total Volume: `${vol:,.2f} USDT`\n• Pending Deposits: `{deposits}`",
        "pl": "• Użytkownicy: `{users}` (Zweryfikowani: `{verified}`)\n• Otwarte pozycje: `{positions}`\n• Całkowity wolumen: `${vol:,.2f} USDT`\n• Oczekujące wpłaty: `{deposits}`"
    },
    "admin_btn_users": {
        "en": "👥 User Directory & OTP",
        "pl": "👥 Lista użytkowników i OTP"
    },
    "admin_btn_positions": {
        "en": "📈 Global Open Positions",
        "pl": "📈 Globalne otwarte pozycje"
    },
    "admin_btn_wallets": {
        "en": "💳 Manage Crypto Addresses",
        "pl": "💳 Zarządzaj adresami krypto"
    },
    "admin_btn_deposits": {
        "en": "📋 Deposits ({count} PENDING)",
        "pl": "📋 Wpłaty ({count} OCZEKUJE)"
    },

    # ------------------ Guide & Help ------------------
    "guide_content": {
        "en": (
            "📖 *AI AUTOMATED TRADING BOT — USER GUIDE*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "This bot combines quantitative algorithms, indicators (RSI, MACD, Bollinger Bands, EMA trends), "
            "and risk-managed order execution.\n\n"
            "🔹 *Key Commands:*\n"
            "• `/start` — Open main dashboard\n"
            "• `/signal` — Scan market for high-probability setups\n"
            "• `/portfolio` — Track balance, win rate, and PnL\n"
            "• `/positions` — View and close open positions\n"
            "• `/verify` — Request security OTP code\n"
            "• `/deposit` — View crypto deposit addresses\n"
            "• `/lang <en|pl>` — Change language (English / Polski)\n\n"
            "💡 *Tip:* By default, the bot runs in **Paper Trading Mode** with virtual USDT so you can test safely!"
        ),
        "pl": (
            "📖 *BOT HANDLOWY AI — INSTRUKCJA UŻYTKOWNIKA*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bot łączy zaawansowane algorytmy ilościowe, wskaźniki (RSI, MACD, Wstęgi Bollingera, wstęgi EMA) "
            "oraz ścisłe zarządzanie ryzykiem pozycji.\n\n"
            "🔹 *Kluczowe komendy:*\n"
            "• `/start` — Otwórz panel główny\n"
            "• `/signal` — Skanuj rynek w poszukiwaniu okazji transakcyjnych\n"
            "• `/portfolio` — Sprawdź saldo, skuteczność i historię zysków\n"
            "• `/positions` — Podgląd i zamykanie aktywnych zleceń\n"
            "• `/verify` — Wygeneruj kod OTP weryfikacji\n"
            "• `/deposit` — Wyświetl adresy do wpłat krypto\n"
            "• `/lang <pl|en>` — Zmiana języka (Polski / English)\n\n"
            "💡 *Wskazówka:* Domyślnie bot działa w **Trybie Demo (Paper Trading)** z wirtualnymi środkami USDT!"
        )
    }
}


def t(key: str, lang_code: str = "en", **kwargs) -> str:
    """
    Get localized string by translation key and format with kwargs.
    Falls back gracefully to English if key or language is missing.
    """
    lang_key = "pl" if lang_code and str(lang_code).lower().startswith("pl") else "en"
    item = TRANSLATIONS.get(key)
    if not item:
        return key

    text = item.get(lang_key) or item.get("en", key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def get_verdict_label(action: str, lang: str = "en") -> str:
    """Format AI verdict in target language."""
    action_clean = action.upper().strip()
    key_map = {
        "STRONG BUY": "verdict_strong_buy",
        "BUY": "verdict_buy",
        "NEUTRAL": "verdict_neutral",
        "SELL": "verdict_sell",
        "STRONG SELL": "verdict_strong_sell"
    }
    key = key_map.get(action_clean)
    if key:
        return t(key, lang)
    return f"*{action}*"


def translate_reasons(reasons: list, lang: str = "en") -> list:
    """
    Translate quantitative AI rationale points into Polish if requested.
    """
    if not lang.startswith("pl"):
        return reasons

    translated = []
    for r in reasons:
        text = r
        # RSI mappings
        if "RSI oversold" in text:
            text = text.replace("RSI oversold", "RSI wyprzedany").replace("indicating strong upside bounce potential", "wskazuje na silny potencjał odbicia w górę")
        elif "RSI recovering from lower zone" in text:
            text = text.replace("RSI recovering from lower zone", "RSI wychodzi z dolnej strefy wyprzedania")
        elif "Healthy bullish momentum sustained on RSI" in text:
            text = text.replace("Healthy bullish momentum sustained on RSI", "Utrzymana silna dynamika wzrostowa na RSI")
        elif "RSI overbought" in text:
            text = text.replace("RSI overbought", "RSI wykupiony").replace("risking imminent pullback/correction", "ryzyko natychmiastowej korekty")
        elif "RSI neutral" in text:
            text = text.replace("RSI neutral", "RSI neutralny").replace("consolidating in mid-range", "konsolidacja w strefie środkowej")

        # MACD mappings
        if "MACD bullish histogram expansion" in text:
            text = text.replace("MACD bullish histogram expansion", "Rozszerzenie wzrostowego histogramu MACD")
        elif "MACD bearish divergence/negative histogram" in text:
            text = text.replace("MACD bearish divergence/negative histogram", "Niedźwiedzia dywergencja / ujemny histogram MACD")

        # Trend & EMA mappings
        if "Price positioned firmly above EMA 20 & EMA 50 trendlines" in text:
            text = "Cena stabilnie powyżej linii trendu EMA 20 i EMA 50"
        elif "Price trading below declining EMA 20 & EMA 50 trendlines" in text:
            text = "Cena notowana poniżej opadających linii EMA 20 i EMA 50"

        # Bollinger Bands
        if "Price tagged lower Bollinger Band" in text:
            text = text.replace("Price tagged lower Bollinger Band", "Cena dotknęła dolnej Wstęgi Bollingera").replace("oversold compression", "kompresja wyprzedania")
        elif "Price stretched against upper Bollinger Band" in text:
            text = text.replace("Price stretched against upper Bollinger Band", "Cena naciągnięta przy górnej Wstędze Bollingera")

        # Volume
        if "Significant volume surge" in text:
            text = text.replace("Significant volume surge", "Znaczący wzrost wolumenu").replace("above 20-period average", "ponad średnią 20-okresową")

        translated.append(text)
    return translated
