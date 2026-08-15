# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Thin wrappers around each provider's official SDK. Credentials are read
from environment variables server-side only -- never sent to or stored
in the browser. Only used by SYNC_AUTO and SYNC_GATED modes; ASYNC_GATED
mode makes no provider calls at all (see relay_engine.py).

Uses each provider's official API client, per the architecture this
project's own design doc recommends -- no browser automation, no
scraping consumer web UIs. Respect each provider's current rate limits
and usage policies; this file doesn't attempt to enforce them, that's
on whoever configures and runs a session.
"""
from __future__ import annotations

import os
from typing import Optional

from .models import Provider


class ProviderError(Exception):
    pass


async def call_anthropic(model: str, history: list[dict], system: Optional[str] = None) -> str:
    try:
        import anthropic
    except ImportError:
        raise ProviderError("anthropic package not installed -- pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProviderError("ANTHROPIC_API_KEY not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    kwargs = {"model": model, "max_tokens": 4096, "messages": history}
    if system:
        kwargs["system"] = system
    response = await client.messages.create(**kwargs)
    return "".join(block.text for block in response.content if block.type == "text")


async def call_openai(model: str, history: list[dict], system: Optional[str] = None) -> str:
    try:
        import openai
    except ImportError:
        raise ProviderError("openai package not installed -- pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("OPENAI_API_KEY not set")

    client = openai.AsyncOpenAI(api_key=api_key)
    messages = history.copy()
    if system:
        messages = [{"role": "system", "content": system}] + messages
    response = await client.chat.completions.create(model=model, messages=messages, max_tokens=4096)
    return response.choices[0].message.content


async def call_google(model: str, history: list[dict], system: Optional[str] = None) -> str:
    try:
        from google import genai
    except ImportError:
        raise ProviderError("google-genai package not installed -- pip install google-genai")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ProviderError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)
    # Gemini uses a slightly different history shape; convert role names
    contents = []
    for m in history:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    config = {"system_instruction": system} if system else {}
    response = await client.aio.models.generate_content(model=model, contents=contents, config=config)
    return response.text


PROVIDER_FUNCS = {
    Provider.ANTHROPIC: call_anthropic,
    Provider.OPENAI: call_openai,
    Provider.GOOGLE: call_google,
}


async def call_provider(provider: Provider, model: str, history: list[dict], system: Optional[str] = None) -> str:
    func = PROVIDER_FUNCS[provider]
    return await func(model, history, system)
