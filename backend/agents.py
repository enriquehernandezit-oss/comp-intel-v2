# agents.py
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import anthropic
from tools import (
    search_company_news,
    search_competitors,
    search_sentiment_signals,
    search_swot_context,
    search_stock_data,
    search_stock_price,
    search_stock_fundamentals,
    search_analyst_ratings,
)

load_dotenv()

# ── Load API key ────────────────────────────────────────────────────────────
try:
    import streamlit as st
    ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL  = "claude-haiku-4-5-20251001"


# ── Shared date string ───────────────────────────────────────────────────────
TODAY_STR = datetime.now(timezone.utc).strftime("%B %d, %Y")


# ── JSON parser ──────────────────────────────────────────────────────────────
def parse_json(text: str, client_ref=None, prompt_ref=None) -> dict:
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        fix_prompt = f"""The following JSON is malformed. Fix it and return ONLY valid JSON, nothing else:

{text[start:end]}"""
        fix_response = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": fix_prompt}]
        )
        fixed   = fix_response.content[0].text
        f_start = fixed.find("{")
        f_end   = fixed.rfind("}") + 1
        return json.loads(fixed[f_start:f_end])


# ── Yahoo Finance data fetcher ───────────────────────────────────────────────
def get_yahoo_finance_data(ticker: str) -> dict:
    """
    Pull real-time financial data directly from Yahoo Finance.
    Returns empty dict if ticker not found or company is private.
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info  = stock.info

        if not info.get("marketCap"):
            return {}

        price      = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        change_pct = ((price - prev_close) / prev_close * 100) if price and prev_close else None

        market_cap = info.get("marketCap")
        if market_cap:
            if market_cap >= 1_000_000_000_000:
                mc_str = f"${market_cap/1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                mc_str = f"${market_cap/1_000_000_000:.2f}B"
            else:
                mc_str = f"${market_cap/1_000_000:.2f}M"
        else:
            mc_str = None

        pe        = info.get("trailingPE") or info.get("forwardPE")
        week_low  = info.get("fiftyTwoWeekLow")
        week_high = info.get("fiftyTwoWeekHigh")
        target    = info.get("targetMeanPrice")
        rating    = info.get("recommendationKey", "").replace("_", " ").title()

        return {
            "ticker":         info.get("symbol", ticker.upper()),
            "exchange":       info.get("exchange", ""),
            "current_price":  f"${price:.2f}" if price else None,
            "price_change":   f"{change_pct:+.2f}%" if change_pct is not None else None,
            "price_as_of":    "Yahoo Finance · Real-time",
            "market_cap":     mc_str,
            "pe_ratio":       f"{pe:.2f}" if pe else None,
            "pe_note":        "Negative earnings — company reporting losses" if pe and pe < 0 else None,
            "52_week_range":  f"${week_low:.2f} – ${week_high:.2f}" if week_low and week_high else None,
            "price_target":   f"${target:.2f}" if target else None,
            "analyst_rating": rating if rating else None,
            "is_public":      True,
        }
    except Exception:
        return {}


# ── Ticker resolver ──────────────────────────────────────────────────────────
def resolve_ticker(company: str) -> str:
    """
    Try to resolve a ticker symbol from a company name using yfinance search.
    """
    try:
        import yfinance as yf

        # Try direct lookup first
        ticker = yf.Ticker(company.upper())
        info   = ticker.info
        if info.get("marketCap"):
            return company.upper()

        # Try search
        results = yf.Search(company, max_results=1)
        quotes  = results.quotes
        if quotes:
            return quotes[0].get("symbol", "")
        return ""
    except Exception:
        return ""


# ── AGENT 1: News Search Agent ───────────────────────────────────────────────
def agent_news(company: str, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("agent_news", "active")

    raw_results = search_company_news(
        f"{company} news funding product launch 2026", max_results=8
    )

    prompt = f"""You are a financial intelligence analyst. Today's date is {TODAY_STR}. We are in 2026 — treat anything in 2025 or earlier as the past, never as upcoming.

Extract the most important findings about {company} and return ONLY a JSON object in this exact format:
{{
  "company": "{company}",
  "headlines": [
    {{"title": "...", "summary": "one sentence summary", "url": "...", "date": "e.g. March 2026 or Unknown", "relevance": "high/medium/low"}}
  ],
  "key_developments": ["development 1", "development 2", "development 3", "development 4", "development 5"],
  "data_freshness": "recent/mixed/stale"
}}

Search results:
{json.dumps(raw_results, indent=2)}

Return ONLY the JSON object. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    result = parse_json(response.content[0].text)

    if progress_callback:
        progress_callback("agent_news", "complete")

    return result


# ── AGENT 2: Competitor Mapper ───────────────────────────────────────────────
def agent_competitors(company: str, news_state: dict, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("agent_competitors", "active")

    raw_results = search_competitors(company, max_results=5)

    prompt = f"""You are a competitive strategy analyst. Today's date is {TODAY_STR}. We are in 2026.

Analyze {company} and its competitive landscape.

You already know this about {company} from prior research:
{json.dumps(news_state.get("key_developments", []), indent=2)}

Now using the search results below, return ONLY a JSON object in this exact format:
{{
  "competitors": [
    {{
      "name": "...",
      "positioning": "one sentence",
      "pricing_signal": "e.g. $99/mo, enterprise, freemium",
      "recent_move": "most notable recent action"
    }}
  ],
  "market_position": "how {company} compares overall in one sentence",
  "competitive_threat_level": "high/medium/low"
}}

Search results:
{json.dumps(raw_results, indent=2)}

Return ONLY the JSON object. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    result = parse_json(response.content[0].text)

    if progress_callback:
        progress_callback("agent_competitors", "complete")

    return result


# ── AGENT 3: Sentiment Scorer ────────────────────────────────────────────────
def agent_sentiment(company: str, news_state: dict, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("agent_sentiment", "active")

    raw_results = search_sentiment_signals(company, max_results=8)

    prompt = f"""You are a brand sentiment analyst. Today's date is {TODAY_STR}. We are in 2026 — treat anything in 2025 or earlier as the past.

Score the public sentiment around {company}.

Context from recent news:
{json.dumps(news_state.get("headlines", [])[:4], indent=2)}

Using the search results below, return ONLY a JSON object in this exact format:
{{
  "overall_score": <integer from -100 to 100>,
  "label": "Very Positive / Positive / Neutral / Negative / Very Negative",
  "sentiment_drivers": [
    {{"driver": "specific thing driving this sentiment", "direction": "positive/negative", "strength": "strong/moderate/weak", "detail": "one sentence explanation"}}
  ],
  "trend": "improving/stable/declining",
  "trend_explanation": "one sentence explaining why the trend is moving this direction",
  "key_quote": "most representative quote or phrase from the results"
}}

Include 4-6 sentiment drivers. Be specific — name actual products, events, or decisions causing the sentiment.

Search results:
{json.dumps(raw_results, indent=2)}

Return ONLY the JSON object. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    result = parse_json(response.content[0].text)

    if progress_callback:
        progress_callback("agent_sentiment", "complete")

    return result


# ── AGENT 4: SWOT Synthesizer ────────────────────────────────────────────────
def agent_swot(company: str, news_state: dict, competitor_state: dict, sentiment_state: dict, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("agent_swot", "active")

    raw_results = search_swot_context(company, max_results=5)

    prompt = f"""You are a strategic analyst writing a SWOT briefing for {company}. Today's date is {TODAY_STR}. We are in 2026.

CRITICAL: Never reference 2025 as a future or current date — it is in the past. All forward-looking statements must reference 2026 and beyond only.

You have access to the following research already conducted:

NEWS & DEVELOPMENTS:
{json.dumps(news_state.get("key_developments", []), indent=2)}

COMPETITIVE LANDSCAPE:
{json.dumps(competitor_state.get("competitors", []), indent=2)}
Market position: {competitor_state.get("market_position", "")}

SENTIMENT:
Overall score: {sentiment_state.get("overall_score", 0)} ({sentiment_state.get("label", "")})
Trend: {sentiment_state.get("trend", "")}
Trend explanation: {sentiment_state.get("trend_explanation", "")}

Now using the additional context below, return ONLY a JSON object in this exact format:
{{
  "strengths":     [{{"point": "...", "source": "brief citation", "impact": "high/medium/low"}}],
  "weaknesses":    [{{"point": "...", "source": "brief citation", "impact": "high/medium/low"}}],
  "opportunities": [{{"point": "...", "source": "brief citation", "impact": "high/medium/low"}}],
  "threats":       [{{"point": "...", "source": "brief citation", "impact": "high/medium/low"}}],
  "executive_summary": "4-5 sentence plain English briefing covering current position as of {TODAY_STR}, key competitive dynamics, sentiment, and one forward-looking observation for 2026 and beyond"
}}

Each quadrant must have 3-4 points. Every point must cite its source. Be specific — name actual products, competitors, events, and numbers where available.

Additional context:
{json.dumps(raw_results, indent=2)}

Return ONLY the JSON object. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    result = parse_json(response.content[0].text)

    if progress_callback:
        progress_callback("agent_swot", "complete")

    return result


# ── AGENT 5: Investment Analyst ──────────────────────────────────────────────
def agent_investment(company: str, news_state: dict, competitor_state: dict, sentiment_state: dict, swot_state: dict, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("agent_investment", "active")

    now      = datetime.now(timezone.utc)
    weekday  = now.weekday()
    time_utc = now.strftime("%H:%M UTC")

    if weekday == 5:
        market_status = "CLOSED — Weekend (Saturday)"
        market_note   = "Markets closed. Prices shown are from Friday's close."
    elif weekday == 6:
        market_status = "CLOSED — Weekend (Sunday)"
        market_note   = "Markets closed. Prices shown are from Friday's close."
    else:
        hour_utc = now.hour + now.minute / 60
        if 13.5 <= hour_utc <= 20.0:
            market_status = f"OPEN — {time_utc}"
            market_note   = "Markets currently open. Prices are real-time."
        elif hour_utc < 13.5:
            market_status = f"PRE-MARKET — {time_utc}"
            market_note   = "Pre-market session. Prices may differ from previous close."
        else:
            market_status = f"AFTER-HOURS — {time_utc}"
            market_note   = "After-hours session. Prices may differ from regular close."

    # ── Step 1: Get real Yahoo Finance data ───────────────────────────────
    ticker_guess = resolve_ticker(company)
    yf_data      = {}
    if ticker_guess:
        yf_data = get_yahoo_finance_data(ticker_guess)

    is_public = bool(yf_data)

    # ── Step 2: Get analyst web context for strategy quality ──────────────
    analyst_results = search_analyst_ratings(company, ticker=ticker_guess, max_results=5)

    # ── Step 3: Build financial section for prompt ────────────────────────
    if is_public:
        financial_section = f"""
LIVE YAHOO FINANCE DATA — USE THESE EXACT FIGURES, DO NOT CHANGE THEM:
Ticker: {yf_data.get('ticker')}
Exchange: {yf_data.get('exchange')}
Current Price: {yf_data.get('current_price')}
Price Change Today: {yf_data.get('price_change')}
Market Cap: {yf_data.get('market_cap')}
P/E Ratio: {yf_data.get('pe_ratio')}
52-Week Range: {yf_data.get('52_week_range')}
Analyst Price Target: {yf_data.get('price_target')}
Analyst Rating: {yf_data.get('analyst_rating')}
"""
    else:
        financial_section = f"""
COMPANY STATUS: {company} appears to be privately held — ticker could not be resolved.
Set all financial metrics (price, market cap, P/E, etc.) to null.
Focus analysis entirely on business fundamentals.
"""

    current_price_str = yf_data.get('current_price', 'N/A') if is_public else 'N/A'

    prompt = f"""You are a buy-side equity analyst. Today's date is {TODAY_STR}. We are in 2026. Market status: {market_status}.

{financial_section}

All prior research on {company}:

KEY DEVELOPMENTS:
{json.dumps(news_state.get("key_developments", []), indent=2)}

COMPETITIVE POSITION:
Market position: {competitor_state.get("market_position", "")}
Threat level: {competitor_state.get("competitive_threat_level", "")}

SENTIMENT: {sentiment_state.get("overall_score", 0)} ({sentiment_state.get("label", "")}) — {sentiment_state.get("trend", "")}

SWOT:
Strengths: {json.dumps([s.get("point","") for s in swot_state.get("strengths", [])], indent=2)}
Weaknesses: {json.dumps([w.get("point","") for w in swot_state.get("weaknesses", [])], indent=2)}
Opportunities: {json.dumps([o.get("point","") for o in swot_state.get("opportunities", [])], indent=2)}
Threats: {json.dumps([t.get("point","") for t in swot_state.get("threats", [])], indent=2)}

ANALYST WEB CONTEXT (for strategy quality only — do NOT use for price figures):
{json.dumps(analyst_results, indent=2)}

CRITICAL RULES:
1. All financial metrics in your JSON must match the Yahoo Finance data above EXACTLY
2. Never reference 2025 as current — we are in 2026
3. If company is private, set all financial fields to null
4. All strategy entry zones, targets, and stop losses must use the actual current price: {current_price_str}
5. Never invent or estimate any financial figure

Return ONLY a JSON object:
{{
  "is_publicly_traded": {str(is_public).lower()},
  "ticker": "{yf_data.get('ticker', '') if is_public else 'null'}",
  "exchange": "{yf_data.get('exchange', '') if is_public else 'null'}",
  "current_price": "{yf_data.get('current_price', 'null') if is_public else 'null'}",
  "price_change": "{yf_data.get('price_change', 'null') if is_public else 'null'}",
  "price_as_of": "Yahoo Finance · Real-time",
  "market_cap": "{yf_data.get('market_cap', 'null') if is_public else 'null'}",
  "analyst_rating": "{yf_data.get('analyst_rating', 'null') if is_public else 'null'}",
  "pe_ratio": "{yf_data.get('pe_ratio', 'null') if is_public else 'null'}",
  "pe_note": "{yf_data.get('pe_note', '') if is_public else 'null'}",
  "52_week_range": "{yf_data.get('52_week_range', 'null') if is_public else 'null'}",
  "price_target": "{yf_data.get('price_target', 'null') if is_public else 'null'}",
  "investment_thesis": "3-4 sentence bull case using actual price {current_price_str} and real metrics — specific products, numbers, 2026 catalysts",
  "bear_case": "2-3 sentence bear case grounded in specific 2026 risks",
  "key_catalysts": ["specific 2026 catalyst 1", "specific 2026 catalyst 2", "specific 2026 catalyst 3"],
  "key_risks": ["specific 2026 risk 1", "specific 2026 risk 2", "specific 2026 risk 3"],
  "strategies": [
    {{
      "name": "strategy name e.g. Momentum Long, Covered Call Income, Bull Call Spread",
      "type": "Bullish / Bearish / Neutral / Income / Hedging",
      "timeframe": "short-term (days-weeks) / medium-term (months) / long-term (1yr+)",
      "rationale": "2-3 sentences tied to current price {current_price_str} and 2026 conditions",
      "entry_signal": "specific measurable trigger based on current price {current_price_str}",
      "entry_price_zone": "specific dollar range based on current price {current_price_str}",
      "position_sizing": "e.g. 3-5% of portfolio, scale in over 2-3 tranches",
      "target": "specific price target with % upside from {current_price_str}",
      "stop_loss": "specific stop loss dollar amount below {current_price_str}",
      "exit_conditions": ["condition 1", "condition 2", "condition 3"],
      "risk_level": "Low / Medium / High / Speculative",
      "catalysts_needed": "specific events needed for this strategy to work"
    }}
  ],
  "overall_signal": "Bullish / Neutral / Bearish",
  "disclaimer": "This is AI-generated analysis for informational purposes only. Not financial advice. Always consult a licensed financial advisor before making investment decisions."
}}

Include 3 strategies: one bullish/growth, one income or hedging, one speculative.
If company is private set all financial fields to null and focus on fundamentals.

Return ONLY the JSON object. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=3500,
        messages=[{"role": "user", "content": prompt}]
    )

    result = parse_json(response.content[0].text)

    # ── Hard override — always use Yahoo Finance data, never Claude's version ──
    if is_public and yf_data:
        result["current_price"]      = yf_data.get("current_price")  or result.get("current_price")
        result["price_change"]       = yf_data.get("price_change")   or result.get("price_change")
        result["market_cap"]         = yf_data.get("market_cap")     or result.get("market_cap")
        result["pe_ratio"]           = yf_data.get("pe_ratio")       or result.get("pe_ratio")
        result["52_week_range"]      = yf_data.get("52_week_range")  or result.get("52_week_range")
        result["price_target"]       = yf_data.get("price_target")   or result.get("price_target")
        result["analyst_rating"]     = yf_data.get("analyst_rating") or result.get("analyst_rating")
        result["price_as_of"]        = "Yahoo Finance · Real-time"
        result["ticker"]             = yf_data.get("ticker")         or result.get("ticker")
        result["exchange"]           = yf_data.get("exchange")       or result.get("exchange")
        result["is_publicly_traded"] = True
    elif not is_public:
        result["current_price"]      = None
        result["price_change"]       = None
        result["market_cap"]         = None
        result["pe_ratio"]           = None
        result["52_week_range"]      = None
        result["price_target"]       = None
        result["analyst_rating"]     = None
        result["is_publicly_traded"] = False

    result["market_status"] = market_status
    result["market_note"]   = market_note

    if progress_callback:
        progress_callback("agent_investment", "complete")

    return result


# ── PIPELINE ORCHESTRATOR ────────────────────────────────────────────────────
def run_pipeline(company: str, progress_callback=None) -> dict:
    state = {}

    state["news"]        = agent_news(company, progress_callback)
    state["competitors"] = agent_competitors(company, state["news"], progress_callback)
    state["sentiment"]   = agent_sentiment(company, state["news"], progress_callback)
    state["swot"]        = agent_swot(
                               company,
                               state["news"],
                               state["competitors"],
                               state["sentiment"],
                               progress_callback
                           )
    state["investment"]  = agent_investment(
                               company,
                               state["news"],
                               state["competitors"],
                               state["sentiment"],
                               state["swot"],
                               progress_callback
                           )
    state["company"] = company
    return state