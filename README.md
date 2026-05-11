# CompIntel — AI Competitive Intelligence Platform


https://github.com/user-attachments/assets/1ec1faa8-ef00-4170-8bf4-d1d86660b419

> Full-stack AI research platform that generates sourced competitive intelligence briefings in under 30 seconds.

---



## What It Does

Type any company or industry. Five specialized Claude AI agents run in sequence — searching the web, mapping competitors, scoring sentiment, synthesizing strategy, and running investment signals — and return a fully sourced intelligence briefing in under 30 seconds. No hallucination. Every finding cites its source.

---

## Five-Agent Pipeline

| Agent | Role | Tools |
|-------|------|-------|
| 01 — News | Scans for recent news, funding rounds, product launches, leadership changes | Claude + Tavily |
| 02 — Competitors | Maps up to 5 competitors with positioning, pricing signals, and recent moves | Claude + Tavily |
| 03 — Sentiment | Scores public perception -100 to +100 with 4-6 named drivers | Claude + Tavily |
| 04 — SWOT | Synthesizes a fully sourced SWOT where every point cites its origin | Claude |
| 05 — Investment | Pulls live financial data from Yahoo Finance, generates bull/bear thesis, and 3 actionable strategies | Claude + Yahoo Finance + Tavily |

Each agent receives the previous agents' findings as context — no agent starts from scratch.

---

## Stack

**Backend** — Python, FastAPI, Anthropic Claude API, Tavily Search API, Yahoo Finance (yfinance), Streaming SSE

**Frontend** — React 18 via Babel CDN, Bloomberg Terminal-inspired dark UI, DM Sans + DM Mono typography, floating AI chatbot

---

## Features

- 5-agent sequential pipeline with tool use and state passing
- Live web search — every finding grounded in real cited sources
- Real-time stock data — price, market cap, P/E, 52-week range, analyst rating pulled directly from Yahoo Finance
- Private company detection — automatically shows N/A for financial metrics if company is not publicly traded
- Investment signals — bull/bear thesis, 3 strategies with entry zone, target, stop loss, position sizing, catalysts, and exit conditions
- Market status detection — open, pre-market, after-hours, weekend
- Floating AI analyst chatbot — Claude answers questions grounded in the specific report with clickable section citations
- Streaming responses — chatbot streams word-by-word
- Works for public companies, private companies, industries, and tickers
- Re-run any company from the sticky nav search bar without leaving the report

---
