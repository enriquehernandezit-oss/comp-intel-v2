# backend/main.py
import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="CompIntel API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────────────────────────
class BriefingRequest(BaseModel):
    company: str


class ChatRequest(BaseModel):
    company:  str
    briefing: dict
    messages: list


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ── POST /briefing ────────────────────────────────────────────────────────────
@app.post("/briefing")
async def get_briefing(req: BriefingRequest):
    if not req.company.strip():
        raise HTTPException(status_code=400, detail="Company name is required.")

    try:
        from agents import run_pipeline
        state = run_pipeline(req.company.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    company = req.company.strip()
    news    = state.get("news", {})
    comps   = state.get("competitors", {})
    sent    = state.get("sentiment", {})
    swot    = state.get("swot", {})
    inv     = state.get("investment", {})

    market_status = inv.get("market_status", "")
    if "OPEN" in market_status:
        ms_kind, ms_label = "open", "MARKET OPEN"
    elif "PRE" in market_status:
        ms_kind, ms_label = "pre", "PRE-MARKET"
    elif "AFTER" in market_status:
        ms_kind, ms_label = "after", "AFTER-HOURS"
    else:
        ms_kind, ms_label = "closed", "MARKET CLOSED"

    price_change = inv.get("price_change", "") or ""
    delta_tone   = "bull" if price_change.startswith("+") else "bear" if price_change.startswith("-") else "neutral"

    signal      = inv.get("overall_signal", "Neutral")
    signal_tone = "bull" if signal == "Bullish" else "bear" if signal == "Bearish" else "warn"

    news_items = []
    for h in news.get("headlines", []):
        relevance = h.get("relevance", "low")
        tone      = "accent" if relevance == "high" else "bull" if relevance == "medium" else "neutral"
        news_items.append({
            "date":    h.get("date", ""),
            "tag":     relevance.upper(),
            "tone":    tone,
            "title":   h.get("title", ""),
            "summary": h.get("summary", ""),
            "sources": [h.get("url", "")] if h.get("url") else [],
        })

    comp_items = []
    for c in comps.get("competitors", []):
        comp_items.append({
            "name":        c.get("name", ""),
            "symbol":      "",
            "region":      "US",
            "color":       "#1A2233",
            "threat":      comps.get("competitive_threat_level", "MEDIUM").upper(),
            "threatTone":  "bear",
            "positioning": c.get("positioning", ""),
            "share":       "N/A",
            "pricing":     c.get("pricing_signal", ""),
            "growth":      "N/A",
            "growthTone":  "neutral",
            "move":        c.get("recent_move", ""),
        })

    drivers = []
    for d in sent.get("sentiment_drivers", []):
        direction = d.get("direction", "neutral")
        score     = 7 if d.get("strength") == "strong" else 4 if d.get("strength") == "moderate" else 2
        val       = score if direction == "positive" else -score
        drivers.append({
            "name": d.get("driver", ""),
            "dir":  val,
            "note": d.get("detail", ""),
        })

    def swot_items(key):
        return [{"text": i.get("point", ""), "src": i.get("source", "")} for i in swot.get(key, [])]

    style_map  = ["cons", "mod", "agg"]
    strategies = []
    for i, s in enumerate(inv.get("strategies", [])):
        exit_raw = s.get("exit_conditions", [])
        if isinstance(exit_raw, str):
            import ast
            try:
                exit_raw = ast.literal_eval(exit_raw)
            except Exception:
                exit_raw = [exit_raw]
        catalysts_raw = s.get("catalysts_needed", "")
        if isinstance(catalysts_raw, str):
            catalysts_list = [c.strip() for c in catalysts_raw.split(";") if c.strip()]
        else:
            catalysts_list = catalysts_raw
        strategies.append({
            "style":    style_map[i % 3],
            "name":     s.get("name", ""),
            "signal":   s.get("entry_signal", ""),
            "entry":    s.get("entry_price_zone", ""),
            "target":   s.get("target", ""),
            "stop":     s.get("stop_loss", ""),
            "position": s.get("position_sizing", ""),
            "needs":    catalysts_list,
            "exits":    exit_raw,
        })

    import datetime
    briefing = {
        "ticker": {
            "symbol": inv.get("ticker") or company.upper()[:4],
            "name":   company,
        },
        "marketStatus": {
            "kind":  ms_kind,
            "label": ms_label,
        },
        "hero": {
            "name":      company,
            "symbol":    inv.get("ticker") or company.upper()[:4],
            "sector":    "N/A",
            "industry":  "N/A",
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%b %-d, %Y · %H:%M ET"),
            "runtime":   0,
            "price":     inv.get("current_price", "N/A"),
            "change":    inv.get("price_change", "N/A"),
            "deltaPct":  inv.get("price_change", ""),
            "deltaTone": delta_tone,
            "marketCap": inv.get("market_cap", "N/A"),
            "pe":        inv.get("pe_ratio", "N/A"),
            "range":     inv.get("52_week_range", "N/A"),
            "analyst":   inv.get("analyst_rating", "N/A"),
            "summary":   swot.get("executive_summary", ""),
        },
        "news":        news_items,
        "competitors": comp_items,
        "sentiment": {
            "score":   sent.get("overall_score", 0),
            "trend":   sent.get("trend", "stable").capitalize(),
            "drivers": drivers,
        },
        "swot": {
            "S": swot_items("strengths"),
            "W": swot_items("weaknesses"),
            "O": swot_items("opportunities"),
            "T": swot_items("threats"),
        },
        "investment": {
            "signal":      signal,
            "signalTone":  signal_tone,
            "bull":        inv.get("investment_thesis", ""),
            "bear":        inv.get("bear_case", ""),
            "catalysts":   inv.get("key_catalysts", []),
            "risks":       inv.get("key_risks", []),
            "strategies":  strategies,
            "pe_note":     inv.get("pe_note", ""),
            "price_as_of": inv.get("price_as_of", ""),
            "disclaimer":  inv.get("disclaimer", ""),
        },
    }

    return briefing


# ── POST /chat (streaming) ────────────────────────────────────────────────────
@app.post("/chat")
async def chat(req: ChatRequest):
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set.")

    b    = req.briefing
    hero = b.get("hero", {})
    sent = b.get("sentiment", {})
    inv  = b.get("investment", {})

    system_context = f"""You are CompIntel's in-report analyst assistant. The user is reading a live briefing about {hero.get('name','this company')} ({hero.get('symbol','')}).

Your job:
- Answer questions using ONLY the data in this briefing — never invent figures
- Reference specific numbers and findings
- Use plain English — no jargon unless the user asks for it
- Keep responses to 2-4 short paragraphs
- When citing a section use bracketed numbers: [01] News, [02] Competitors, [03] Sentiment, [04] SWOT, [05] Investment

Briefing snapshot:
Price: {hero.get('price','N/A')} | Market Cap: {hero.get('marketCap','N/A')} | P/E: {hero.get('pe','N/A')} | Analyst: {hero.get('analyst','N/A')}
Signal: {inv.get('signal','N/A')}
Executive summary: {hero.get('summary','')}
Sentiment score: {sent.get('score',0)} ({sent.get('trend','')})
Bull case: {inv.get('bull','')}
Bear case: {inv.get('bear','')}
Strategies: {' | '.join([s.get('name','') + ' — entry ' + s.get('entry','') + ' → target ' + s.get('target','') for s in inv.get('strategies',[])])}
Key risks: {', '.join(inv.get('risks',[]))}
Key catalysts: {', '.join(inv.get('catalysts',[]))}
"""

    messages = [
        {"role": "user",      "content": system_context},
        {"role": "assistant", "content": f"I've loaded the {hero.get('symbol','')} briefing. Ask me anything about the report."},
    ]
    for msg in req.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    client = anthropic.Anthropic(api_key=api_key)

    async def stream_response():
        try:
            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=messages,
            ) as stream:
                for text_chunk in stream.text_stream:
                    yield f"data: {json.dumps({'text': text_chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        }
    )