import os
import re
import logging
from typing import List, Dict, Any, Optional

import requests

logger = logging.getLogger("mt5app")


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


def _normalize_item(
    title: str,
    url: str,
    source: str = '',
    published: str = '',
    summary: str = '',
    body: str | None = None,
) -> Dict[str, Any]:
    return {
        'title': title or '',
        'url': url or '',
        'source': source or '',
        'publishedAt': published or '',
        'summary': summary or '',
        # Include full-text body when available (e.g., FMP 'text')
        'body': (body or ''),
    }


def _is_fx_pair(symbol: str) -> bool:
    """Return True only for 6–7 char FX-like pairs (e.g., XAUUSD, EURUSD).

    Single codes like 'XAU' or 'USD' should NOT be treated as pairs.
    """
    sym = (symbol or '').upper()
    return bool(re.fullmatch(r'[A-Z]{3}[A-Z]{3,4}', sym))


def _fx_synonyms(ccy: str) -> list[str]:
    c = (ccy or '').upper()
    mapping = {
        'USD': ['usd', 'u.s. dollar', 'us dollar', 'dollar', 'greenback'],
        'EUR': ['eur', 'euro'],
        'GBP': ['gbp', 'pound', 'sterling', 'british pound'],
        'JPY': ['jpy', 'yen', 'japanese yen'],
        'CHF': ['chf', 'franc', 'swiss franc'],
        'AUD': ['aud', 'australian dollar', 'aussie'],
        'NZD': ['nzd', 'new zealand dollar', 'kiwi'],
        'CAD': ['cad', 'canadian dollar', 'loonie'],
        'XAU': ['xau', 'gold', 'bullion'],
        'XAG': ['xag', 'silver'],
        'XPT': ['xpt', 'platinum'],
        'XPD': ['xpd', 'palladium'],
    }
    return mapping.get(c, [c.lower()])


def _fx_is_relevant(title: str, body: str, base: str, quote: str) -> bool:
    text = f"{title}\n{body}".lower()
    b = (base or '').upper()
    q = (quote or '').upper()
    if not b or not q:
        return False
    # explicit pair patterns
    pairs = [f"{b}{q}", f"{b}/{q}", f"{q}{b}", f"{q}/{b}"]
    if any(p.lower() in text for p in pairs):
        return True
    # both currency names present
    base_terms = _fx_synonyms(b)
    quote_terms = _fx_synonyms(q)
    if any(t in text for t in base_terms) and any(t in text for t in quote_terms):
        return True
    # generic fx context + at least one side
    has_fx_ctx = any(w in text for w in ['forex', 'fx ', 'currency', 'currencies', 'foreign exchange'])
    if has_fx_ctx and (any(t in text for t in base_terms + [b.lower()]) or any(t in text for t in quote_terms + [q.lower()])):
        return True
    return False


def fetch_fmp_news(symbol: str, limit: int = 20, timeout: float = 5.0) -> List[Dict[str, Any]]:
    key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')
    if not key:
        logger.info("[news] FMP key missing; skip fetch_fmp_news(%s)", symbol)
        return []
    sym = (symbol or '').upper()
    # Use the broad news feed for FX pairs and for standalone 3-letter codes (USD, XAU, etc.)
    if _is_fx_pair(sym) or len(sym) == 3:
        url = f'https://financialmodelingprep.com/api/v3/stock_news?limit=50&apikey={key}'
    else:
        url = f'https://financialmodelingprep.com/api/v3/stock_news?tickers={sym}&limit=50&apikey={key}'
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or []
    except Exception as e:
        logger.info("[news] FMP request failed for %s: %s", symbol, e)
        return []
    terms = _terms_for_symbol(symbol)
    items: List[Dict[str, Any]] = []
    for it in data:
        title = it.get('title') or ''
        text = it.get('text') or ''
        if _match_any(title, terms) or _match_any(text, terms):
            full_text = text or ''
            items.append(
                _normalize_item(
                    title=title,
                    url=it.get('url') or '',
                    source=it.get('site') or '',
                    published=it.get('publishedDate') or '',
                    summary=(full_text[:280] + ('…' if len(full_text) > 280 else '')),
                    body=full_text,
                )
            )
            if len(items) >= limit:
                break
    logger.info("[news] fmp_news symbol=%s fetched=%d filtered=%d", symbol, len(data), len(items))
    return items


def fetch_alpha_news(symbol: str, limit: int = 20, timeout: float = 5.0) -> List[Dict[str, Any]]:
    key = os.getenv('ALPHAVANTAGE_API_KEY') or os.getenv('ALPHAVANTAGE_KEY') or os.getenv('ALPHA_VANTAGE_KEY')
    if not key:
        logger.info("[news] AlphaVantage key missing; skip fetch_alpha_news(%s)", symbol)
        return []
    # Use broad FOREX topic and filter client-side
    sym = (symbol or '').upper()
    # Use FOREX topic for pairs and standalone 3-letter codes
    if _is_fx_pair(sym) or len(sym) == 3:
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=FOREX&sort=LATEST&apikey={key}'
    else:
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={sym}&sort=LATEST&apikey={key}'
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception as e:
        logger.info("[news] AlphaVantage request failed for %s: %s", symbol, e)
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
                    body=summary or '',  # no separate body from AlphaVantage feed
                )
            )
            if len(items) >= limit:
                break
    logger.info("[news] alpha_news symbol=%s filtered=%d", symbol, len(items))
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
                break
    # Extra filtering only for true FX pairs (not for standalone 3-letter codes)
    sym = (symbol or '').upper()
    if _is_fx_pair(sym):
        base = sym[:3]
        quote = sym[3:6]
        filtered: List[Dict[str, Any]] = []
        for it in out:
            title = it.get('title') or ''
            body = it.get('body') or it.get('summary') or ''
            # exclude pure ETF/fund chatter unless FX context clearly present
            low = (f"{title}\n{body}").lower()
            is_etfish = any(w in low for w in [' etf', 'etfs', 'fund', 'proshares', 'leveraged'])
            fx_ctx = any(w in low for w in ['forex', 'currency', 'currencies', 'fx '])
            if is_etfish and not fx_ctx:
                continue
            if _fx_is_relevant(title, body, base, quote):
                filtered.append(it)
        out = filtered
    # cap result size
    if len(out) > limit:
        out = out[:limit]
    logger.info("[news] aggregated symbol=%s items=%d", symbol, len(out))
    return out


def fetch_fmp_forex_latest(
    *,
    since: Optional[str] = None,
    to: Optional[str] = None,
    page: int = 0,
    limit: int = 100,
    timeout: float = 6.0,
) -> List[Dict[str, Any]]:
    """Fetch the FMP forex-latest feed page with optional date filtering.

    Dates should be ISO-like 'YYYY-MM-DD' strings according to FMP docs.
    """
    key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')
    if not key:
        logger.info("[news] FMP key missing; skip forex-latest page=%d", page)
        return []
    base = 'https://financialmodelingprep.com/stable/news/forex-latest'
    params = [f"page={int(page)}", f"limit={int(limit)}", f"apikey={key}"]
    if since:
        params.append(f"from={since}")
    if to:
        params.append(f"to={to}")
    url = base + '?' + '&'.join(params)
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or []
    except Exception as e:
        logger.info("[news] FMP request failed for %s: %s", symbol, e)
        return []
    out: List[Dict[str, Any]] = []
    for it in data:
        # FMP returns 'symbol', 'publishedDate', 'publisher', 'title', 'image', 'site', 'text', 'url'
        out.append(
            _normalize_item(
                title=(it.get('title') or ''),
                url=(it.get('url') or ''),
                source=(it.get('publisher') or ''),
                published=(it.get('publishedDate') or ''),
                summary=(it.get('text') or '')[:280] + ('…' if len(it.get('text') or '') > 280 else ''),
                body=(it.get('text') or ''),
            ) | {
                'symbol': (it.get('symbol') or '').upper(),
                'image': it.get('image') or '',
                'site': it.get('site') or '',
            }
        )
    return out


def fetch_fmp_snapshot(symbol: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Return a small fundamentals/quote snapshot for the selected symbol using FMP endpoints."""
    key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')
    if not key:
        logger.info("[news] FMP key missing; skip snapshot(%s)", symbol)
        return {}
    sym = (symbol or '').upper()
    try:
        if _is_fx_pair(sym):
            url = f'https://financialmodelingprep.com/api/v3/fx/{sym}?apikey={key}'
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            data = r.json() or []
            if not data:
                return {}
            item = data[0]
            return {
                'type': 'forex',
                'symbol': sym,
                'name': item.get('name') or sym,
                'price': item.get('price'),
                'change': item.get('change'),
                'changesPercentage': item.get('changesPercentage'),
                'dayHigh': item.get('dayHigh'),
                'dayLow': item.get('dayLow'),
                'yearHigh': item.get('yearHigh'),
                'yearLow': item.get('yearLow'),
            }
        else:
            quote_url = f'https://financialmodelingprep.com/api/v3/quote/{sym}?apikey={key}'
            prof_url = f'https://financialmodelingprep.com/api/v3/profile/{sym}?apikey={key}'
            quote_resp = requests.get(quote_url, timeout=timeout)
            quote_resp.raise_for_status()
            quote_data = (quote_resp.json() or [])
            profile: Optional[Dict[str, Any]] = None
            try:
                prof_resp = requests.get(prof_url, timeout=timeout)
                prof_resp.raise_for_status()
                prof_data = prof_resp.json() or []
                profile = prof_data[0] if prof_data else None
            except Exception:
                profile = None
            item = quote_data[0] if quote_data else {}
            snapshot = {
                'type': 'equity',
                'symbol': sym,
                'name': profile.get('companyName') if profile else item.get('name') or sym,
                'price': item.get('price'),
                'change': item.get('change'),
                'changesPercentage': item.get('changesPercentage'),
                'dayHigh': item.get('dayHigh'),
                'dayLow': item.get('dayLow'),
                'yearHigh': item.get('yearHigh'),
                'yearLow': item.get('yearLow'),
                'previousClose': item.get('previousClose'),
                'open': item.get('open'),
                'volume': item.get('volume'),
                'avgVolume': item.get('avgVolume'),
                'marketCap': item.get('marketCap'),
                'exchange': item.get('exchange'),
            }
            if profile:
                snapshot['industry'] = profile.get('industry')
                snapshot['sector'] = profile.get('sector')
                snapshot['description'] = profile.get('description')
                snapshot['currency'] = profile.get('currency')
                snapshot['ceo'] = profile.get('ceo')
                snapshot['website'] = profile.get('website')
            return snapshot
    except Exception as e:
        logger.info("[news] snapshot request failed for %s: %s", symbol, e)
        return {}
    return {}


def fetch_symbol_digest(symbol: str, limit: int = 20) -> Dict[str, Any]:
    """Return both news items and auxiliary snapshot information for a symbol."""
    symu = (symbol or '').upper()
    news: List[Dict[str, Any]] = []
    # Prefer FMP forex-latest feed for FX symbols (provides symbol-tagged articles)
    if _is_fx_pair(symu):
        try:
            # Pull a couple pages to gather enough recent items for the symbol
            for pg in (0, 1):
                batch = fetch_fmp_forex_latest(page=pg, limit=200)
                if not batch:
                    break
                for it in batch:
                    if (it.get('symbol') or '').upper() == symu:
                        news.append(it)
                        if len(news) >= limit:
                            break
                if len(news) >= limit:
                    break
        except Exception:
            news = []
        # Fallback to general providers if forex-latest yielded nothing
        if not news:
            news = fetch_news_for_symbol(symu, limit=limit)
    else:
        news = fetch_news_for_symbol(symu, limit=limit)
    snapshot = fetch_fmp_snapshot(symbol)
    return {
        'symbol': symu,
        'news': news,
        'snapshot': snapshot,
    }
