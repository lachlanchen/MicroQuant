#!/usr/bin/env python3
"""Smoke-test the MixedAIRequestJSONBase by requesting tiny JSON output."""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can import helper modules stored under llm_model/
ROOT = Path(__file__).resolve().parents[1]
LLM_DIR = ROOT / "llm_model"
if LLM_DIR.exists():
    sys.path.append(str(LLM_DIR))
env_path = ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# Provide a lightweight pygame stub if the real library is unavailable for this smoke test.
if "pygame" not in sys.modules:
    stub = types.SimpleNamespace()
    music = types.SimpleNamespace(
        load=lambda *_args, **_kwargs: None,
        play=lambda *_args, **_kwargs: None,
        get_busy=lambda: False,
        stop=lambda: None,
    )
    stub.mixer = types.SimpleNamespace(init=lambda *_args, **_kwargs: None, music=music)
    stub.time = types.SimpleNamespace(wait=lambda *_args, **_kwargs: None)
    sys.modules["pygame"] = stub

try:
    from echomind.mixed_ai_request import MixedAIRequestJSONBase  # type: ignore
except ImportError as exc:  # pragma: no cover
    print(f"Failed to import MixedAIRequestJSONBase: {exc}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    schema = {
        "type": "object",
        "properties": {
            "reply": {"type": "string"}
        },
        "required": ["reply"],
        "additionalProperties": False,
    }

    prompt = (
        "Reply with JSON that contains a single field named 'reply' with any text. "
        "Do not include any additional text."
    )

    try:
        client = MixedAIRequestJSONBase(use_cache=False, max_retries=2, cache_dir=str(ROOT / "cache"))
    except Exception as exc:
        print(f"Failed to initialise MixedAIRequestJSONBase: {exc}", file=sys.stderr)
        return 1

    try:
        result = client.send_request_with_json_schema(
            prompt,
            schema,
            system_content="You are a JSON-only bot.",
            schema_name="hello_response",
        )
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
