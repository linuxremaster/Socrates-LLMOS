# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Thin, uniform wrapper around each provider's SDK so conditions.py doesn't
care which model it's talking to.

You must set API keys as environment variables before running:
    ANTHROPIC_API_KEY
    OPENAI_API_KEY
    GOOGLE_API_KEY

Install SDKs:
    pip install anthropic openai google-generativeai --break-system-packages

Each call() returns a CallResult with token usage recorded whenever the
provider exposes it — per §6 "Do not assume provider token accounting is
perfectly comparable," we record what's actually reported and mark
anything unavailable as None rather than estimating it.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Literal

Provider = Literal["anthropic", "openai", "google"]


@dataclass
class CallResult:
    text: str
    input_tokens: int | None
    output_tokens: int | None
    wall_clock_seconds: float
    provider: str
    model: str
    raw_finish_reason: str | None = None


class LLMClient:
    def __init__(self, provider: Provider, model: str):
        self.provider = provider
        self.model = model
        self._client = self._build_client()

    def _build_client(self):
        if self.provider == "anthropic":
            import anthropic
            return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        elif self.provider == "openai":
            import openai
            return openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        elif self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            return genai.GenerativeModel(self.model)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def call(self, system: str, user: str, max_tokens: int) -> CallResult:
        start = time.time()

        if self.provider == "anthropic":
            resp = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(
                block.text for block in resp.content if hasattr(block, "text")
            )
            return CallResult(
                text=text,
                input_tokens=resp.usage.input_tokens,
                output_tokens=resp.usage.output_tokens,
                wall_clock_seconds=time.time() - start,
                provider=self.provider,
                model=self.model,
                raw_finish_reason=resp.stop_reason,
            )

        elif self.provider == "openai":
            resp = self._client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            usage = resp.usage
            return CallResult(
                text=resp.choices[0].message.content or "",
                input_tokens=usage.prompt_tokens if usage else None,
                output_tokens=usage.completion_tokens if usage else None,
                wall_clock_seconds=time.time() - start,
                provider=self.provider,
                model=self.model,
                raw_finish_reason=resp.choices[0].finish_reason,
            )

        elif self.provider == "google":
            resp = self._client.generate_content(
                f"{system}\n\n{user}",
                generation_config={"max_output_tokens": max_tokens},
            )
            # Gemini's token usage reporting varies by SDK version - record
            # what's available, mark unavailable as None rather than guess.
            input_tokens = getattr(
                getattr(resp, "usage_metadata", None), "prompt_token_count", None
            )
            output_tokens = getattr(
                getattr(resp, "usage_metadata", None), "candidates_token_count", None
            )
            return CallResult(
                text=resp.text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                wall_clock_seconds=time.time() - start,
                provider=self.provider,
                model=self.model,
                raw_finish_reason=None,
            )
