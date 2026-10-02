import math
from typing import List, Dict, Any


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average (EMA)."""
    if len(prices) < period:
        return [prices[-1]] * len(prices)
    
    multiplier = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]
    
    for price in prices[period:]:
        new_val = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(new_val)
        
    padding = [ema[0]] * (len(prices) - len(ema))
    return padding + ema


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate Relative Strength Index (RSI)."""
    if len(prices) <= period:
        return 50.0

    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [c if c > 0 else 0.0 for c in changes]
    losses = [-c if c < 0 else 0.0 for c in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(changes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return round(rsi, 2)


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal_span: int = 9) -> Dict[str, float]:
    """Calculate MACD Line, Signal Line, and Histogram."""
    if len(prices) < slow + signal_span:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_series = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_series = calculate_ema(macd_series, signal_span)

    macd_val = round(macd_series[-1], 4)
    sig_val = round(signal_series[-1], 4)
    hist_val = round(macd_val - sig_val, 4)

    return {
        "macd": macd_val,
        "signal": sig_val,
        "histogram": hist_val,
        "crossover": "BULLISH" if hist_val > 0 else "BEARISH"
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, num_std: float = 2.0) -> Dict[str, float]:
    """Calculate Bollinger Bands (Upper, Middle, Lower, %B)."""
    if len(prices) < period:
        p = prices[-1] if prices else 0.0
        return {"upper": p * 1.02, "middle": p, "lower": p * 0.98, "percent_b": 0.5}

    slice_prices = prices[-period:]
    middle = sum(slice_prices) / period
    variance = sum((x - middle) ** 2 for x in slice_prices) / period
    std_dev = math.sqrt(variance)

    upper = middle + (std_dev * num_std)
    lower = middle - (std_dev * num_std)
    current = prices[-1]

    percent_b = (current - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

    return {
        "upper": round(upper, 2),
        "middle": round(middle, 2),
        "lower": round(lower, 2),
        "bandwidth": round((upper - lower) / middle * 100, 2) if middle > 0 else 0,
        "percent_b": round(percent_b, 2)
    }


def calculate_atr(candles: List[List[float]], period: int = 14) -> float:
    """
    Calculate Average True Range (ATR).
    Candle format: [time, open, high, low, close, volume]
    """
    if len(candles) < period + 1:
        return (candles[-1][2] - candles[-1][3]) if candles else 1.0

    tr_list = []
    for i in range(1, len(candles)):
        current_high = candles[i][2]
        current_low = candles[i][3]
        prev_close = candles[i - 1][4]

        tr = max(
            current_high - current_low,
            abs(current_high - prev_close),
            abs(current_low - prev_close)
        )
        tr_list.append(tr)

    atr = sum(tr_list[-period:]) / period
    return round(atr, 4)


def analyze_market_indicators(candles: List[List[float]]) -> Dict[str, Any]:
    """
    Run comprehensive technical analysis on candle data.
    Candles: [ [timestamp, open, high, low, close, volume], ... ]
    """
    if not candles or len(candles) < 20:
        return {"error": "Insufficient candle data"}

    close_prices = [c[4] for c in candles]
    high_prices = [c[2] for c in candles]
    low_prices = [c[3] for c in candles]
    volumes = [c[5] for c in candles]

    current_price = close_prices[-1]

    # Indicators
    rsi = calculate_rsi(close_prices, 14)
    macd = calculate_macd(close_prices)
    bb = calculate_bollinger_bands(close_prices, 20)
    atr = calculate_atr(candles, 14)

    ema20 = calculate_ema(close_prices, 20)[-1]
    ema50 = calculate_ema(close_prices, 50)[-1]
    ema200 = calculate_ema(close_prices, 200)[-1] if len(close_prices) >= 200 else ema50

    # Trend determination
    trend = "NEUTRAL"
    if current_price > ema20 > ema50:
        trend = "BULLISH"
    elif current_price < ema20 < ema50:
        trend = "BEARISH"

    # Volume spike
    avg_vol = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else volumes[-1]
    last_vol = volumes[-1]
    vol_ratio = round(last_vol / avg_vol, 2) if avg_vol > 0 else 1.0

    # Support / Resistance (Pivot points & local extremes)
    recent_high = max(high_prices[-20:])
    recent_low = min(low_prices[-20:])

    pivot = (recent_high + recent_low + current_price) / 3
    resistance_1 = (2 * pivot) - recent_low
    support_1 = (2 * pivot) - recent_high

    return {
        "current_price": current_price,
        "rsi": rsi,
        "macd": macd,
        "bollinger": bb,
        "atr": atr,
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "ema200": round(ema200, 2),
        "trend": trend,
        "volume_ratio": vol_ratio,
        "support": round(support_1, 2),
        "resistance": round(resistance_1, 2),
        "recent_high": round(recent_high, 2),
        "recent_low": round(recent_low, 2)
    }
