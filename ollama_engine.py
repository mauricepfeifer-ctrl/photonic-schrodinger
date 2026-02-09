from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Union

import aiohttp


@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None


class OllamaEngine:
    """
    Unified local LLM interface for Ollama.
    - Supports /api/chat (preferred) and /api/generate (fallback).
    - Configurable via env:
      OLLAMA_HOST (default http://127.0.0.1:11434)
      OLLAMA_MODEL (default llama3.1:8b)
      OLLAMA_TEMPERATURE (default 0.2)
    """

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        timeout_s: float = 600.0,
    ) -> None:
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL") or "llama3.1:8b"
        self.temperature = temperature if temperature is not None else float(os.getenv("OLLAMA_TEMPERATURE") or "0.2")
        self.timeout_s = timeout_s

    async def health(self) -> bool:
        url = f"{self.host}/api/tags"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_s)) as s:
                async with s.get(url) as r:
                    return r.status == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        url = f"{self.host}/api/tags"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_s)) as s:
            async with s.get(url) as r:
                r.raise_for_status()
                data = await r.json()
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]

    async def pull_model(self, model: Optional[str] = None) -> None:
        url = f"{self.host}/api/pull"
        payload = {"name": model or self.model}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_s)) as s:
            async with s.post(url, json=payload) as r:
                r.raise_for_status()
                # Ollama streams json lines; we just consume
                async for _ in r.content:
                    pass

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> Union[LLMResponse, Iterable[str]]:
        """
        messages format:
          [{"role":"system|user|assistant","content":"..."}]
        """
        m = model or self.model
        temp = self.temperature if temperature is None else temperature

        url = f"{self.host}/api/chat"
        payload: Dict[str, Any] = {
            "model": m,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": temp, **(options or {})},
        }

        t0 = time.time()

        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        session = aiohttp.ClientSession(timeout=timeout)
        try:
            async with session.post(url, json=payload) as r:
                r.raise_for_status()

                if stream:
                    async def gen() -> Iterable[str]:
                        async for line in r.content:
                            if not line:
                                continue
                            try:
                                obj = json.loads(line.decode("utf-8"))
                            except Exception:
                                continue
                            msg = obj.get("message", {})
                            chunk = msg.get("content")
                            if chunk:
                                yield chunk
                    return gen()

                data = await r.json()
                content = (data.get("message") or {}).get("content") or ""
                usage = data.get("usage") or {}
                dt = int((time.time() - t0) * 1000)

                return LLMResponse(
                    content=content,
                    model=m,
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                    latency_ms=dt,
                    raw=data,
                )
        finally:
            await session.close()

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> Union[LLMResponse, Iterable[str]]:
        """
        Fallback endpoint similar to /api/generate
        """
        m = model or self.model
        temp = self.temperature if temperature is None else temperature

        url = f"{self.host}/api/generate"
        payload: Dict[str, Any] = {
            "model": m,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": temp, **(options or {})},
        }

        t0 = time.time()
        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        session = aiohttp.ClientSession(timeout=timeout)
        try:
            async with session.post(url, json=payload) as r:
                r.raise_for_status()

                if stream:
                    async def gen() -> Iterable[str]:
                        async for line in r.content:
                            if not line:
                                continue
                            try:
                                obj = json.loads(line.decode("utf-8"))
                            except Exception:
                                continue
                            chunk = obj.get("response")
                            if chunk:
                                yield chunk
                    return gen()

                # non-stream responses sometimes still come as json lines; collect
                text = ""
                raw_last: Optional[Dict[str, Any]] = None
                async for line in r.content:
                    if not line:
                        continue
                    try:
                        obj = json.loads(line.decode("utf-8"))
                    except Exception:
                        continue
                    raw_last = obj
                    text += obj.get("response") or ""
                    if obj.get("done"):
                        break

                dt = int((time.time() - t0) * 1000)
                usage = (raw_last or {}).get("usage") or {}
                return LLMResponse(
                    content=text,
                    model=m,
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                    latency_ms=dt,
                    raw=raw_last,
                )
        finally:
            await session.close()


async def _standalone_test() -> None:
    engine = OllamaEngine()
    ok = await engine.health()
    print("health:", ok, "host:", engine.host)
    models = await engine.list_models()
    print("models:", models[:10], ("..." if len(models) > 10 else ""))
    resp = await engine.chat(
        [
            {"role": "system", "content": "You are a precise assistant."},
            {"role": "user", "content": "Give me 3 bullet ideas to sell an AI automation sprint to small businesses."},
        ]
    )
    assert isinstance(resp, LLMResponse)
    print("model:", resp.model, "latency_ms:", resp.latency_ms)
    print(resp.content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_standalone_test())
