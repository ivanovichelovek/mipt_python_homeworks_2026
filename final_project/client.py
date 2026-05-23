from collections.abc import Iterator
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .config import AppConfig
from .history import MessageDict


class LLMClient:
    def __init__(self, config: AppConfig) -> None:
        self._openai = OpenAI(api_key=config.api_key, base_url=config.api_host)
        self._model = config.model
        self._temperature = config.temperature

    def send_stream(self, messages: list[MessageDict]) -> Iterator[str]:
        stream = self._openai.chat.completions.create(
            model=self._model,
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=self._temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
