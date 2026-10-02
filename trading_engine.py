from typing import Dict, Any, Optional, List
from config import DEFAULT_RISK_PERCENT, MAX_OPEN_POSITIONS, SUPPORTED_PAIRS, DEFAULT_TIMEFRAME
from database import (
    get_user, create_position, get_open_positions, get_position,
    close_position_in_db, update_position_extremes, log_trade_action,
    save_signal
)
from market_data import get_live_ticker, get_ohlcv
from ai_engine import get_ai_signal

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False


def calculate_position_size(user: Dict[str, Any], symbol: str, current_price: float, risk_percent: float = None) -> float:
    """Calculate trade amount in USDT based on risk management rules."""
    if risk_percent is None:
        risk_percent = user.get("risk_percent", DEFAULT_RISK_PERCENT)

    if user.get("trading_mode") == "paper":
        balance = user.get("paper_balance", 10000.0)
    else:
        # For live trading, default to a safe $50 allocation or fraction of balance
        balance = 1000.0

    trade_cost_usdt = balance * (risk_percent / 100.0)
    trade_cost_usdt = max(10.0, min(trade_cost_usdt, balance))  # Min $10 trade
    return round(trade_cost_usdt, 2)


def open_trade(
    user_id: int,
    symbol: str,
    side: str,  # 'BUY' or 'SELL'
    amount_usdt: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    trailing_stop: float = 0.0
) -> Dict[str, Any]:
    """
    Execute order (Paper or Live) and record open position.
    """
    user = get_user(user_id)
    if not user:
        return {"success": False, "error": "User account not found."}

    # Verify open positions limit
    user_positions = get_open_positions(user_id)
    if len(user_positions) >= MAX_OPEN_POSITIONS:
        return {
            "success": False,
            "error": f"Maximum open positions ({MAX_OPEN_POSITIONS}) reached. Close a position first."
        }

    # Fetch live price
    ticker = get_live_ticker(symbol)
    entry_price = ticker["price"]
    if entry_price <= 0:
        return {"success": False, "error": f"Unable to fetch live price for {symbol}."}

    # Determine cost in USDT
    if amount_usdt is None or amount_usdt <= 0:
        cost = calculate_position_size(user, symbol, entry_price)
    else:
        cost = float(amount_usdt)

    mode = user.get("trading_mode", "paper")

    # Paper mode balance check
    if mode == "paper":
        current_balance = user.get("paper_balance", 0.0)
        if current_balance < cost:
            return {
                "success": False,
                "error": f"Insufficient paper balance. Required: ${cost:.2f}, Available: ${current_balance:.2f}"
            }
    else:
        # Live mode execution via CCXT
        if not user.get("api_key") or not user.get("api_secret"):
            return {
                "success": False,
                "error": "Live trading requires API keys. Configure them in Settings or switch to Paper Trading."
            }
        # In live mode, connect to exchange
        try:
            exchange_name = user.get("exchange", "binance")
            ex_class = getattr(ccxt, exchange_name, None)
            if not ex_class:
                return {"success": False, "error": f"Unsupported exchange: {exchange_name}"}
            client = ex_class({
                "apiKey": user["api_key"],
                "secret": user["api_secret"],
                "enableRateLimit": True
            })
            amount_coin = cost / entry_price
            order = client.create_order(symbol, "market", side.lower(), amount_coin)
            entry_price = float(order.get("price", entry_price))
        except Exception as e:
            return {"success": False, "error": f"Exchange order failed: {str(e)}"}

    amount_coin = cost / entry_price

    # Auto calculate SL / TP if not provided
    if stop_loss is None or take_profit is None:
        if side.upper() == "BUY":
            stop_loss = round(entry_price * 0.97, 2)
            take_profit = round(entry_price * 1.05, 2)
        else:
            stop_loss = round(entry_price * 1.03, 2)
            take_profit = round(entry_price * 0.95, 2)

    pos_id = create_position(
        user_id=user_id,
        symbol=symbol,
        side=side.upper(),
        entry_price=entry_price,
        amount=amount_coin,
        cost=cost,
        take_profit=take_profit,
        stop_loss=stop_loss,
        mode=mode,
        trailing_stop=trailing_stop
    )

    log_trade_action(
        user_id, symbol, f"OPEN_{side.upper()}",
        f"Position #{pos_id} opened at ${entry_price:,.2f} (Cost: ${cost:.2f})"
    )

    return {
        "success": True,
        "position_id": pos_id,
        "symbol": symbol,
        "side": side.upper(),
        "entry_price": entry_price,
        "amount": amount_coin,
        "cost": cost,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "mode": mode
    }


def close_trade(user_id: int, position_id: int, reason: str = "CLOSED_MANUAL") -> Dict[str, Any]:
    """Close an existing trade at market price and record final PnL."""
    pos = get_position(position_id)
    if not pos:
        return {"success": False, "error": "Position not found."}
    if pos["user_id"] != user_id:
        return {"success": False, "error": "Unauthorized position access."}
    if pos["status"] != "OPEN":
        return {"success": False, "error": f"Position already closed with status: {pos['status']}"}

    ticker = get_live_ticker(pos["symbol"])
    exit_price = ticker["price"]

    # Calculate PnL
    if pos["side"] == "BUY":
        pnl = (exit_price - pos["entry_price"]) * pos["amount"]
    else:  # SHORT / SELL
        pnl = (pos["entry_price"] - exit_price) * pos["amount"]

    pnl_percent = (pnl / pos["cost"] * 100.0) if pos["cost"] > 0 else 0.0

    # If live mode, place closing order
    if pos["mode"] == "live":
        user = get_user(user_id)
        if user and user.get("api_key"):
            try:
                ex_class = getattr(ccxt, user.get("exchange", "binance"))
                client = ex_class({"apiKey": user["api_key"], "secret": user["api_secret"]})
                closing_side = "sell" if pos["side"] == "BUY" else "buy"
                client.create_order(pos["symbol"], "market", closing_side, pos["amount"])
            except Exception as e:
                print(f"Error closing live order on exchange: {e}")

    close_position_in_db(
        position_id=position_id,
        exit_price=round(exit_price, 2),
        pnl=round(pnl, 2),
        pnl_percent=round(pnl_percent, 2),
        status=reason
    )

    log_trade_action(
        user_id, pos["symbol"], reason,
        f"Position #{position_id} closed at ${exit_price:,.2f} | PnL: ${pnl:+.2f} ({pnl_percent:+.2f}%)"
    )

    return {
        "success": True,
        "position_id": position_id,
        "symbol": pos["symbol"],
        "side": pos["side"],
        "entry_price": pos["entry_price"],
        "exit_price": exit_price,
        "pnl": round(pnl, 2),
        "pnl_percent": round(pnl_percent, 2),
        "status": reason
    }


def check_and_update_positions() -> List[Dict[str, Any]]:
    """
    Scans all open positions across the database.
    Evaluates Take-Profit and Stop-Loss triggers.
    Returns list of triggered closure events.
    """
    open_positions = get_open_positions()
    triggered_events = []

    # Cache tickers to minimize API requests
    cached_prices = {}

    for pos in open_positions:
        symbol = pos["symbol"]
        if symbol not in cached_prices:
            ticker = get_live_ticker(symbol)
            cached_prices[symbol] = ticker["price"]

        current_price = cached_prices[symbol]
        if current_price <= 0:
            continue

        update_position_extremes(pos["id"], current_price)

        side = pos["side"]
        tp = pos["take_profit"]
        sl = pos["stop_loss"]

        closed_reason = None

        if side == "BUY":
            if tp and current_price >= tp:
                closed_reason = "CLOSED_TP"
            elif sl and current_price <= sl:
                closed_reason = "CLOSED_SL"
        elif side == "SELL":
            if tp and current_price <= tp:
                closed_reason = "CLOSED_TP"
            elif sl and current_price >= sl:
                closed_reason = "CLOSED_SL"

        if closed_reason:
            res = close_trade(pos["user_id"], pos["id"], reason=closed_reason)
            if res.get("success"):
                res["user_id"] = pos["user_id"]
                triggered_events.append(res)

    return triggered_events


def execute_auto_trading_cycle() -> List[Dict[str, Any]]:
    """
    Executes automated AI trading scans for all opted-in users.
    Opens trades when high-confidence signals trigger.
    """
    from database import get_connection
    auto_trades_opened = []

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE is_auto_trading = 1")
        active_users = [dict(r) for r in cursor.fetchall()]

    if not active_users:
        return []

    # Check top pairs
    pairs_to_check = SUPPORTED_PAIRS[:5]

    for symbol in pairs_to_check:
        candles = get_ohlcv(symbol, timeframe=DEFAULT_TIMEFRAME, limit=100)
        signal = get_ai_signal(symbol, DEFAULT_TIMEFRAME, candles)

        if "error" in signal:
            continue

        # Save signal in DB
        save_signal(
            symbol=symbol,
            timeframe=DEFAULT_TIMEFRAME,
            action=signal["action"],
            price=signal["price"],
            target_tp1=signal["target_tp1"],
            target_tp2=signal["target_tp2"],
            stop_loss=signal["stop_loss"],
            confidence=signal["confidence"],
            indicators_dict=signal["indicators"],
            analysis_text=signal["analysis_text"]
        )

        # High confidence triggers
        action = signal["action"]
        if action in ["STRONG BUY", "BUY", "STRONG SELL", "SELL"] and signal["confidence"] >= 72.0:
            side = "BUY" if "BUY" in action else "SELL"

            for user in active_users:
                user_id = user["user_id"]
                existing_positions = [
                    p for p in get_open_positions(user_id) if p["symbol"] == symbol
                ]
                # Avoid duplicate position on same symbol
                if not existing_positions and len(get_open_positions(user_id)) < MAX_OPEN_POSITIONS:
                    res = open_trade(
                        user_id=user_id,
                        symbol=symbol,
                        side=side,
                        stop_loss=signal["stop_loss"],
                        take_profit=signal["target_tp1"]
                    )
                    if res.get("success"):
                        res["signal_action"] = action
                        res["confidence"] = signal["confidence"]
                        auto_trades_opened.append(res)

    return auto_trades_opened
