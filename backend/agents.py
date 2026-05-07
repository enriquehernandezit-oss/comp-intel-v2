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


# ── Shared date string (computed once at import time) ───────────────────────
TODAY_STR = datetime.now(timezone.utc).strftime("%B %d, %Y")


# ── JSON parser (handles markdown-wrapped responses) ────────────────────────
def parse_json(text: str, client_ref=None, prompt_ref=None) -> dict:
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        # Ask Claude to fix the broken JSON
        fix_prompt = f"""The following JSON is malformed. Fix it and return ONLY valid JSON, nothing else:

{text[start:end]}"""
        fix_response = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": fix_prompt}]
        )
        fixed = fix_response.content[0].text
        f_start = fixed.find("{")
        f_end   = fixed.rfind("}") + 1
        return json.loads(fixed[f_start:f_end])


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

    # Three targeted searches instead of one generic one
    price_results       = search_stock_price(company, max_results=5)
    fundamental_results = search_stock_fundamentals(company, max_results=5)
    analyst_results     = search_analyst_ratings(company, max_results=4)

    prompt = f"""You are a buy-side equity analyst. Today's date is {TODAY_STR}. We are in 2026. Market status: {market_status}.

EXTRACTION RULES — READ CAREFULLY:
1. Extract financial figures from the search results even if they appear inside sentences, paragraphs, or tables — not just structured data.
2. For any publicly traded company, market cap, 52-week range, and analyst rating WILL exist somewhere in the results — find them.
3. If P/E is negative, still report it as a string e.g. "-151.29" — do NOT set it to null. Only set pe_ratio to null if no P/E figure appears anywhere in the results.
4. pe_note is for context only — use it to explain negative P/E or special situations, but always populate pe_ratio if any number exists.
5. For price_as_of: extract the most recent date mentioned alongside any price figure.
6. Never reference 2025 as current or future — we are in 2026.
7. analyst_rating must be one of: Buy / Overweight / Hold / Underweight / Sell / Mixed — extract the consensus from results.

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

--- PRICE & MARKET DATA (search these carefully for all figures) ---
{json.dumps(price_results, indent=2)}

--- FUNDAMENTALS DATA (PE ratio, market cap, 52-week range) ---
{json.dumps(fundamental_results, indent=2)}

--- ANALYST RATINGS DATA ---
{json.dumps(analyst_results, indent=2)}

Return ONLY a JSON object:
{{
  "is_publicly_traded": true or false,
  "ticker": "e.g. INTC or null",
  "exchange": "e.g. NASDAQ, NYSE or null",
  "current_price": "e.g. $21.37 — extract from price data",
  "price_change": "e.g. +2.3% or -1.1% — extract from price data",
  "price_as_of": "most recent date found alongside a price figure",
  "market_cap": "e.g. $91.2B — extract from any section",
  "analyst_rating": "consensus rating from analyst data",
  "pe_ratio": "report as string even if negative e.g. -151.29 — only null if completely absent",
  "pe_note": "context for pe_ratio e.g. Negative P/E reflects current losses — company in turnaround phase, or null if P/E is normal",
  "52_week_range": "e.g. $17.53 - $37.16 — extract from fundamentals data",
  "price_target": "analyst consensus price target",
  "investment_thesis": "3-4 sentence bull case — specific products, numbers, 2026 catalysts",
  "bear_case": "2-3 sentence bear case — specific 2026 risks",
  "key_catalysts": ["2026 catalyst 1", "2026 catalyst 2", "2026 catalyst 3"],
  "key_risks": ["2026 risk 1", "2026 risk 2", "2026 risk 3"],
  "strategies": [
    {{
      "name": "strategy name e.g. Momentum Long, Covered Call Income, Dollar-Cost Average, Wait for Catalyst, Short-Term Put Hedge",
      "type": "Bullish / Bearish / Neutral / Income / Hedging",
      "timeframe": "short-term (days-weeks) / medium-term (months) / long-term (1yr+)",
      "rationale": "2-3 sentences explaining why this strategy makes sense given current price action, sentiment, competitive position, and 2026 catalysts specifically",
      "entry_signal": "specific and measurable trigger — e.g. price closes above $23.50 on volume above 30-day average, RSI crosses above 45 from oversold, next earnings beat consensus by >5%",
      "entry_price_zone": "specific price range to enter e.g. $20.00 - $22.50, or 'at market' if momentum play",
      "position_sizing": "e.g. 2-5% of portfolio for speculative, 5-8% for conviction play, scale in over 3 tranches",
      "target": "specific price target or % gain e.g. $28.00 (+32%) within 6 months, or yield target for income strategies",
      "stop_loss": "specific stop loss level e.g. hard stop at $18.50 (-12%), or trailing stop 8% below peak",
      "exit_conditions": "list 2-3 specific conditions that would trigger exit e.g. earnings miss >10%, CEO departure, price breaks below 200-day MA",
      "risk_level": "Low / Medium / High / Speculative",
      "catalysts_needed": "what specific events need to happen for this strategy to work e.g. Q2 2026 earnings beat, 18A node production ramp confirmed, Fed rate cut"
    }}
  ],
  ],
  "overall_signal": "Bullish / Neutral / Bearish",
  "disclaimer": "This is AI-generated analysis for informational purposes only. Not financial advice. Always consult a licensed financial advisor before making investment decisions."
}}

Include 3 strategies that are meaningfully different from each other — one bullish/growth play, one income or hedging play, and one speculative or options-based play. Each strategy must be detailed enough for a retail investor to execute without additional research. Use actual price levels from the search results wherever possible.
Return ONLY the JSON object. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=3500,
        messages=[{"role": "user", "content": prompt}]
    )

    result = parse_json(response.content[0].text)
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