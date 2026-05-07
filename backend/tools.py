# tools.py
import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

try:
    import streamlit as st
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except Exception:
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=TAVILY_API_KEY)


# ── Tool 1: General news + intelligence search ──────────────────────────────
def search_company_news(query: str, max_results: int = 8) -> list[dict]:
    """
    Search for recent news, funding rounds, product launches,
    leadership changes about a company or industry.
    """
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "content": r.get("content", "")[:600],
            "score":   round(r.get("score", 0), 3),
        })
    return output


# ── Tool 2: Competitor discovery search ─────────────────────────────────────
def search_competitors(company: str, max_results: int = 5) -> list[dict]:
    """
    Find top competitors, their positioning, pricing signals,
    and recent strategic moves.
    """
    query = f"{company} competitors alternatives pricing positioning 2024 2025"
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":          r.get("title", ""),
            "url":            r.get("url", ""),
            "content":        r.get("content", "")[:800],
            "score":          round(r.get("score", 0), 3),
            "published_date": r.get("published_date", ""),
        })
    return output


# ── Tool 3: Sentiment signals search ────────────────────────────────────────
def search_sentiment_signals(company: str, max_results: int = 6) -> list[dict]:
    """
    Pull recent reviews, social signals, and press tone
    to feed the sentiment scoring agent.
    """
    query = f"{company} reviews complaints praise sentiment customer feedback 2025"
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "content": r.get("content", "")[:600],
            "score":   round(r.get("score", 0), 3),
        })
    return output


# ── Tool 4: SWOT context search ──────────────────────────────────────────────
def search_swot_context(company: str, max_results: int = 5) -> list[dict]:
    """
    Fetch broader strategic context: market trends, regulatory risks,
    partnerships, and growth opportunities.
    """
    query = f"{company} market trends risks opportunities partnerships strategy 2025"
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "content": r.get("content", "")[:600],
            "score":   round(r.get("score", 0), 3),
        })
    return output

# ── Tool 5a: Stock price + change ───────────────────────────────────────────
def search_stock_price(company: str, ticker: str = "", max_results: int = 5) -> list[dict]:
    query = f"{ticker or company} stock price today market cap 2026"
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":          r.get("title", ""),
            "url":            r.get("url", ""),
            "content":        r.get("content", "")[:800],
            "score":          round(r.get("score", 0), 3),
            "published_date": r.get("published_date", ""),
        })
    return output


# ── Tool 5b: Fundamentals + analyst data ────────────────────────────────────
def search_stock_fundamentals(company: str, ticker: str = "", max_results: int = 5) -> list[dict]:
    query = f"{ticker or company} PE ratio 52 week range market cap analyst price target 2026"
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":          r.get("title", ""),
            "url":            r.get("url", ""),
            "content":        r.get("content", "")[:800],
            "score":          round(r.get("score", 0), 3),
            "published_date": r.get("published_date", ""),
        })
    return output


# ── Tool 5c: Analyst ratings search ─────────────────────────────────────────
def search_analyst_ratings(company: str, ticker: str = "", max_results: int = 4) -> list[dict]:
    query = f"{ticker or company} analyst rating buy sell hold consensus 2026"
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    output = []
    for r in results.get("results", []):
        output.append({
            "title":          r.get("title", ""),
            "url":            r.get("url", ""),
            "content":        r.get("content", "")[:800],
            "score":          round(r.get("score", 0), 3),
            "published_date": r.get("published_date", ""),
        })
    return output


# ── Tool 5 (kept for backward compat) ───────────────────────────────────────
def search_stock_data(company: str, max_results: int = 8) -> list[dict]:
    return search_stock_price(company, max_results=max_results)