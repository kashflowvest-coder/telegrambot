import json
import requests
from typing import Dict, Any, Optional
from config import AI_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY
from technical_analysis import analyze_market_indicators


def generate_quantitative_ai_signal(symbol: str, timeframe: str, indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Multi-Factor Quantitative AI Signal Engine.
    Evaluates momentum, trend, volatility, and volume indicators.
    """
    price = indicators["current_price"]
    rsi = indicators["rsi"]
    macd = indicators["macd"]
    trend = indicators["trend"]
    bb = indicators["bollinger"]
    atr = indicators["atr"]
    vol_ratio = indicators["volume_ratio"]
    ema20 = indicators.get("ema20", price)
    ema50 = indicators.get("ema50", price)
    ema200 = indicators.get("ema200", price)
    support = indicators.get("support", price * 0.97)
    resistance = indicators.get("resistance", price * 1.03)

    # Scoring mechanism (-12 to +12 expanded)
    score = 0
    reasons = []

    # 1. RSI Factor (with divergence-like zone awareness)
    if rsi < 28:
        score += 3.5
        reasons.append(f"RSI extreme oversold ({rsi:.1f}) — deep bounce / reversal setup")
    elif rsi < 38:
        score += 1.5
        reasons.append(f"RSI recovering from oversold zone ({rsi:.1f})")
    elif 55 < rsi <= 68:
        score += 1.5
        reasons.append(f"Healthy bullish momentum sustained on RSI ({rsi:.1f})")
    elif rsi > 72:
        score -= 3.5
        reasons.append(f"RSI extreme overbought ({rsi:.1f}) — pullback/reversal risk")
    elif rsi > 62:
        score -= 1.5
        reasons.append(f"RSI approaching overbought zone ({rsi:.1f})")
    elif 42 <= rsi <= 55:
        reasons.append(f"RSI neutral ({rsi:.1f}) — no directional edge")

    # 2. MACD Factor (histogram momentum strength)
    hist = macd.get("histogram", 0)
    if macd.get("crossover") == "BULLISH":
        if hist > 0.001 * price:
            score += 3.0
            reasons.append(f"MACD strong bullish crossover with expanding histogram (+{hist:.4f})")
        else:
            score += 1.5
            reasons.append(f"MACD bullish crossover (early-stage, histogram: +{hist:.4f})")
    elif macd.get("crossover") == "BEARISH":
        if abs(hist) > 0.001 * price:
            score -= 3.0
            reasons.append(f"MACD strong bearish crossover with expanding negative histogram ({hist:.4f})")
        else:
            score -= 1.5
            reasons.append(f"MACD bearish crossover (early-stage, histogram: {hist:.4f})")

    # 3. EMA Trend Stack (EMA 20/50/200)
    if price > ema20 > ema50 > ema200:
        score += 3.0
        reasons.append("Price above EMA 20/50/200 — full bullish trend stack confirmed")
    elif price > ema20 > ema50:
        score += 2.0
        reasons.append("Price above EMA 20 & EMA 50 — short-to-mid term bullish trend")
    elif price < ema20 < ema50 < ema200:
        score -= 3.0
        reasons.append("Price below EMA 20/50/200 — full bearish trend stack confirmed")
    elif price < ema20 < ema50:
        score -= 2.0
        reasons.append("Price below EMA 20 & EMA 50 — short-to-mid term bearish trend")

    # 4. Bollinger Band Position + Squeeze Detection
    bandwidth = bb.get("bandwidth", 5.0)
    pct_b = bb.get("percent_b", 0.5)

    # Squeeze: bandwidth < 2% signals potential breakout setup
    squeeze = bandwidth < 2.0
    if squeeze:
        reasons.append(f"⚡ Bollinger Band SQUEEZE detected (BW: {bandwidth:.2f}%) — breakout imminent")
        # Amplify score slightly since a breakout is expected in current direction
        if score > 0:
            score += 1.0
        elif score < 0:
            score -= 1.0

    if pct_b < 0.10:
        score += 2.5
        reasons.append(f"Price tagged lower Bollinger Band ({bb['lower']:,.2f}) — oversold compression")
    elif pct_b < 0.20:
        score += 1.0
        reasons.append(f"Price near lower Bollinger Band (BB %B: {pct_b:.2f}) — potential bounce zone")
    elif pct_b > 0.90:
        score -= 2.5
        reasons.append(f"Price stretched against upper Bollinger Band ({bb['upper']:,.2f}) — extended")
    elif pct_b > 0.80:
        score -= 1.0
        reasons.append(f"Price near upper Bollinger Band (BB %B: {pct_b:.2f}) — exhaustion risk")

    # 5. Support / Resistance proximity
    dist_to_support = abs(price - support) / price
    dist_to_resistance = abs(resistance - price) / price
    if dist_to_support < 0.008:
        score += 1.5
        reasons.append(f"Price testing key support level at ${support:,.2f} — high-probability bounce zone")
    if dist_to_resistance < 0.008:
        score -= 1.5
        reasons.append(f"Price approaching resistance at ${resistance:,.2f} — potential supply/rejection zone")

    # 6. Volume Confirmation (amplifies existing bias)
    if vol_ratio >= 2.0:
        reasons.append(f"🔥 Extreme volume spike ({vol_ratio:.1f}x avg) — institutional activity detected")
        score += 2.0 if score > 0 else -2.0
    elif vol_ratio >= 1.5:
        reasons.append(f"Elevated volume ({vol_ratio:.1f}x avg) confirms directional pressure")
        score += 1.0 if score > 0 else -1.0
    elif vol_ratio < 0.6:
        reasons.append(f"Low volume ({vol_ratio:.1f}x avg) — low conviction, treat signal cautiously")
        score *= 0.7  # Dampen signal on low volume

    # Determine Action and Confidence
    confidence = min(97.0, max(45.0, 50.0 + (abs(score) / 12.0) * 47.0))

    if score >= 6.0:
        action = "STRONG BUY"
    elif score >= 2.5:
        action = "BUY"
    elif score <= -6.0:
        action = "STRONG SELL"
    elif score <= -2.5:
        action = "SELL"
    else:
        action = "NEUTRAL"
        confidence = min(55.0, confidence)

    # Dynamic ATR-based Risk Management with R:R calibration
    # Strong signals get wider TP targets (1:3 R:R)
    atr_multiplier_sl = 1.5
    atr_multiplier_tp1 = 1.5
    atr_multiplier_tp2 = 3.0 if "STRONG" in action else 2.0
    rr_ratio = "1:3.0" if "STRONG" in action else "1:2.0"

    atr_buffer_sl = max(atr * atr_multiplier_sl, price * 0.008)
    atr_buffer_tp1 = max(atr * atr_multiplier_tp1, price * 0.01)
    atr_buffer_tp2 = max(atr * atr_multiplier_tp2, price * 0.02)

    if "BUY" in action:
        stop_loss = round(price - atr_buffer_sl, 2)
        tp1 = round(price + atr_buffer_tp1, 2)
        tp2 = round(price + atr_buffer_tp2, 2)
    elif "SELL" in action:
        stop_loss = round(price + atr_buffer_sl, 2)
        tp1 = round(price - atr_buffer_tp1, 2)
        tp2 = round(price - atr_buffer_tp2, 2)
    else:
        stop_loss = round(price * 0.985, 2)
        tp1 = round(price * 1.015, 2)
        tp2 = round(price * 1.03, 2)
        rr_ratio = "1:1.0"

    analysis_text = "\n".join([f"• {r}" for r in reasons])

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "action": action,
        "price": price,
        "target_tp1": tp1,
        "target_tp2": tp2,
        "stop_loss": stop_loss,
        "risk_reward": rr_ratio,
        "confidence": round(confidence, 1),
        "score": round(score, 2),
        "reasons": reasons,
        "analysis_text": analysis_text,
        "indicators": indicators,
        "squeeze": squeeze
    }


def analyze_with_llm(symbol: str, timeframe: str, quant_signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhances quantitative signal using OpenAI or Gemini if API keys are configured.
    """
    if AI_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            prompt = f"""
            You are a senior algorithmic crypto trader.
            Analyze this setup for {symbol} on {timeframe} timeframe:
            Current Price: {quant_signal['price']}
            RSI (14): {quant_signal['indicators']['rsi']}
            MACD: {quant_signal['indicators']['macd']}
            Trend: {quant_signal['indicators']['trend']}
            Bollinger Bands: {quant_signal['indicators']['bollinger']}
            Quantitative Action: {quant_signal['action']} (Confidence: {quant_signal['confidence']}%)

            Provide a concise 2-sentence executive summary and validation of Entry, SL, and TP targets.
            Return plain text.
            """
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                summary = resp.json()["choices"][0]["message"]["content"].strip()
                quant_signal["llm_summary"] = summary
        except Exception as e:
            print(f"OpenAI analysis call skipped: {e}")

    return quant_signal


def get_ai_signal(symbol: str, timeframe: str, candles: list) -> Dict[str, Any]:
    """
    Main entrypoint to generate an AI trading signal.
    """
    indicators = analyze_market_indicators(candles)
    if "error" in indicators:
        return {"error": indicators["error"]}

    signal = generate_quantitative_ai_signal(symbol, timeframe, indicators)

    if (AI_PROVIDER in ["openai", "gemini"]) and (OPENAI_API_KEY or GEMINI_API_KEY):
        signal = analyze_with_llm(symbol, timeframe, signal)

    return signal
