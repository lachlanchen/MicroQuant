#!/usr/bin/env python3
"""Mixed AI request client that falls back between OpenAI and DeepSeek."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

try:  # Prefer relative import when used as a package
    from .openai_request import OpenAIRequestJSONBase  # type: ignore
except ImportError:  # Fallback for legacy sys.path setups
    from echomind.openai_request import OpenAIRequestJSONBase  # type: ignore

try:
    from .deepseek_requests import DeepSeekRequestJSONBase  # type: ignore
except Exception:  # pragma: no cover - DeepSeek optional
    try:
        from echomind.deepseek_requests import DeepSeekRequestJSONBase  # type: ignore
    except Exception:
        DeepSeekRequestJSONBase = None  # type: ignore

LOGGER = logging.getLogger(__name__)


class MixedAIRequestJSONBase:
    """Proxy client that tries providers in order with graceful fallback."""

    def __init__(
        self,
        providers: Optional[List[str]] = None,
        use_cache: bool = True,
        max_retries: int = 3,
        cache_dir: str = 'cache'
    ) -> None:
        order = providers or ['openai', 'deepseek']
        self._clients: Dict[str, object] = {}
        self._order: List[str] = []
        self.use_cache = use_cache
        self.max_retries = max_retries
        self.cache_dir = cache_dir

        for name in order:
            key = (name or '').strip().lower()
            if key == 'openai':
                try:
                    client = OpenAIRequestJSONBase(use_cache=use_cache, max_retries=max_retries, cache_dir=cache_dir)
                    self._clients['openai'] = client
                    self._order.append('openai')
                except Exception as exc:  # pragma: no cover - initialization failure
                    LOGGER.warning("MixedAI: failed to initialise OpenAI client: %s", exc)
            elif key == 'deepseek':
                if DeepSeekRequestJSONBase is None:
                    LOGGER.warning("MixedAI: DeepSeek client not available (module import failed)")
                    continue
                try:
                    client = DeepSeekRequestJSONBase(use_cache=use_cache, max_retries=max_retries, cache_dir=cache_dir)
                    self._clients['deepseek'] = client
                    self._order.append('deepseek')
                except Exception as exc:  # pragma: no cover - initialization failure
                    LOGGER.warning("MixedAI: failed to initialise DeepSeek client: %s", exc)

        if not self._order:
            raise RuntimeError('MixedAIRequestJSONBase: no providers available')

    @property
    def providers(self) -> List[str]:
        return self._order.copy()

    def _call_with_fallback(self, method_name: str, *args, **kwargs):
        last_exc: Optional[Exception] = None
        # Allow caller to hint a specific provider (e.g., 'openai' or 'deepseek')
        preferred = (kwargs.pop('provider', None) or kwargs.pop('preferred_provider', None) or '').strip().lower()
        if preferred and preferred in self._order:
            trial_order = [preferred] + [p for p in self._order if p != preferred]
        else:
            trial_order = list(self._order)
        for provider in trial_order:
            client = self._clients.get(provider)
            if not client:
                continue
            call_kwargs = dict(kwargs)
            # Pass through model to both providers; each client handles its defaults
            try:
                method = getattr(client, method_name)
                return method(*args, **call_kwargs)
            except Exception as exc:  # pragma: no cover - network failure
                last_exc = exc
                LOGGER.warning("MixedAI: provider %s failed for %s: %s", provider, method_name, exc)
        if last_exc:
            raise last_exc
        raise RuntimeError(f'MixedAI: no providers succeeded for {method_name}')

    def send_request_with_json_schema(self, *args, **kwargs):
        return self._call_with_fallback('send_request_with_json_schema', *args, **kwargs)

    def send_simple_request(self, *args, **kwargs):
        return self._call_with_fallback('send_simple_request', *args, **kwargs)

    def __getattr__(self, item):
        # Fallback to primary provider for any other attributes/methods
        primary = self._order[0]
        client = self._clients.get(primary)
        if client is None:
            raise AttributeError(item)
        return getattr(client, item)
