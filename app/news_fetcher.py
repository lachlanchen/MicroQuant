import os
import re
import time
from typing import List, Dict, Any

import requests


def _terms_for_symbol(symbol: str) -> List[str]:
    symbol = (symbol or '').upper()
    # currency code → common name mapping
    cname = {
        'USD': 'usd US dollar dollar',
        'EUR': 'eur euro',
        'GBP': 'gbp pound sterling',
        'JPY': 'jpy yen',
        'CHF': 'chf franc',
        'AUD': 'aud australian dollar',
        'NZD': 'nzd new zealand dollar kiwi',
        'CAD': 'cad canadian dollar loonie',
        'XAU': 'xau gold',
        'XAG': 'xag silver',
    }
    terms = {symbol}
    # split base/quote if looks like forex/metals
    if len(symbol) in (6, 7):  # e.g. XAUUSD or EURUSD
        base = symbol[:3]
        quote = symbol[3:6]
        terms.update([base, quote])
        for t in cname.get(base, '').split():
            terms.add(t)
        for t in cname.get(quote, '').split():
            terms.add(t)
        # helpful generic words
        if base == 'XAU' or 'gold' in cname.get(base, ''):
            terms.update(['gold', 'bullion'])
        if base == 'XAG' or 'silver' in cname.get(base, ''):
            terms.update(['silver'])
    return [t for t in (w.strip() for w in terms) if t]


def _match_any(text: str, terms: List[str]) -> bool:
    if not text:
        return False
    low = text.lower()
    return any(term.lower() in low for term in terms)


def _normalize_item(title: str, url: str, source: str = '', published: str = '', summary: str = '') -> Dict[str, Any]:
    return {
        'title': title or '',
        'url': url or '',
        'source': source or '',
        'publishedAt': published or '',
        'summary': summary or '',
    }


def fetch_fmp_news(symbol: str, limit: int = 20, timeout: float = 5.0) -> List[Dict[str, Any]]:
    key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')
    if not key:
        return []
    url = f'https://financialmodelingprep.com/api/v3/stock_news?limit=50&apikey={key}'
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or []
    except Exception:
        return []
    terms = _terms_for_symbol(symbol)
    items: List[Dict[str, Any]] = []
    for it in data:
        title = it.get('title') or ''
        text = it.get('text') or ''
        if _match_any(title, terms) or _match_any(text, terms):
            items.append(
                _normalize_item(
                    title=title,
                    url=it.get('url') or '',
                    source=it.get('site') or '',
                    published=it.get('publishedDate') or '',
                    summary=text[:280] + ('…' if len(text) > 280 else ''),
                )
            )
            if len(items) >= limit:
                break
    return items


def fetch_alpha_news(symbol: str, limit: int = 20, timeout: float = 5.0) -> List[Dict[str, Any]]:
    key = os.getenv('ALPHAVANTAGE_API_KEY') or os.getenv('ALPHAVANTAGE_KEY') or os.getenv('ALPHA_VANTAGE_KEY')
    if not key:
        return []
    # Use broad FOREX topic and filter client-side
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=FOREX&sort=LATEST&apikey={key}'
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception:
        return []
    feed = data.get('feed') or []
    terms = _terms_for_symbol(symbol)
    items: List[Dict[str, Any]] = []
    for it in feed:
        title = it.get('title') or ''
        summary = it.get('summary') or ''
        if _match_any(title, terms) or _match_any(summary, terms):
            items.append(
                _normalize_item(
                    title=title,
                    url=(it.get('url') or ''),
                    source=(it.get('source') or ''),
                    published=(it.get('time_published') or ''),
                    summary=summary[:280] + ('…' if len(summary) > 280 else ''),
                )
            )
            if len(items) >= limit:
                break
    return items


def fetch_news_for_symbol(symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for provider in (fetch_fmp_news, fetch_alpha_news):
        try:
            items = provider(symbol, limit=limit)
        except Exception:
            items = []
        for it in items:
            key = it.get('url') or it.get('title')
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(it)
            if len(out) >= limit:
                return out
    return out

