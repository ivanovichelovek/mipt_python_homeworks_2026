import os
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import yaml
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

CONFIG_FILE = Path(__file__).parent / 'config.yaml'

ENV_API_KEY = 'API_KEY'
ENV_API_HOST = 'API_HOST'
ENV_LIMIT_MESSAGE = 'LIMIT_MESSAGE'
ENV_LIMIT_CHARS = 'LIMIT_CHARS'
ENV_TEMPERATURE = 'TEMPERATURE'
ENV_MODEL = 'MODEL'

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MODEL = 'gemma3:270m'

ERR_NO_API_KEY = (
    'API-ключ не настроен. '
    'Укажите API_KEY в переменных окружения или api_key в config.yaml.'
)
ERR_NO_API_HOST = (
    'Хост API не настроен. '
    'Укажите API_HOST в переменных окружения или api_host в config.yaml.'
)
ERR_NO_CONFIG = 'Конфигурация не найдена. Задайте переменные окружения или создайте config.yaml.'
ERR_TEMPERATURE = 'temperature должно быть числом с плавающей точкой от 0.0 до 1.0.'
ERR_LIMIT_MESSAGE = 'limit_message должно быть положительным целым числом.'
ERR_LIMIT_CHARS = 'limit_chars должно быть положительным целым числом.'


@dataclass
class AppConfig:
    api_key: str
    api_host: str
    model: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str | None


def _load_yaml(path: Path) -> dict[str, object]:
    with open(path) as f:
        result = yaml.safe_load(f)
    return result if isinstance(result, dict) else {}


def _validate(config: AppConfig) -> None:
    errors: list[str] = []
    if not (0.0 <= config.temperature <= 1.0):
        errors.append(ERR_TEMPERATURE)
    if config.limit_message is not None and config.limit_message <= 0:
        errors.append(ERR_LIMIT_MESSAGE)
    if config.limit_chars is not None and config.limit_chars <= 0:
        errors.append(ERR_LIMIT_CHARS)
    if errors:
        raise ValueError('\n'.join(errors))


def _build(env: Mapping[str, str], yaml_cfg: Mapping[str, object]) -> AppConfig:
    api_key = env.get(ENV_API_KEY) or yaml_cfg.get('api_key')
    api_host = env.get(ENV_API_HOST) or yaml_cfg.get('api_host')

    if not api_key:
        raise ValueError(ERR_NO_API_KEY)
    if not api_host:
        raise ValueError(ERR_NO_API_HOST)

    raw_limit_msg = env.get(ENV_LIMIT_MESSAGE) or yaml_cfg.get('limit_message')
    raw_limit_chars = env.get(ENV_LIMIT_CHARS) or yaml_cfg.get('limit_chars')
    raw_temperature = env.get(ENV_TEMPERATURE) or yaml_cfg.get('temperature')
    raw_model = env.get(ENV_MODEL) or yaml_cfg.get('model')

    config = AppConfig(
        api_key=str(api_key),
        api_host=str(api_host),
        model=str(raw_model) if raw_model is not None else DEFAULT_MODEL,
        limit_message=int(str(raw_limit_msg)) if raw_limit_msg is not None else None,
        limit_chars=int(str(raw_limit_chars)) if raw_limit_chars is not None else None,
        temperature=float(str(raw_temperature)) if raw_temperature is not None
        else DEFAULT_TEMPERATURE,
        system_prompt=str(yaml_cfg['system_prompt']) if 'system_prompt' in yaml_cfg else None,
    )
    _validate(config)
    return config


def load_config() -> AppConfig:
    env: dict[str, str] = dict(os.environ)
    yaml_cfg: dict[str, object] = {}

    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        yaml_cfg = _load_yaml(config_path)

    has_env = bool(env.get(ENV_API_KEY) or env.get(ENV_API_HOST))
    if not has_env and not yaml_cfg:
        raise RuntimeError(ERR_NO_CONFIG)

    return _build(env, yaml_cfg)


ROLE_USER = 'user'
ROLE_ASSISTANT = 'assistant'
ROLE_SYSTEM = 'system'

MessageDict = dict[str, str]


@dataclass
class MessageHistory:
    _messages: list[MessageDict] = field(default_factory=list, init=False)

    def _total_chars(self) -> int:
        return sum(len(m['content']) for m in self._messages)

    def prepare_and_add(
        self,
        content: str,
        limit_message: int | None,
        limit_chars: int | None,
    ) -> str:
        if limit_message is not None:
            while len(self._messages) >= limit_message:
                self._messages.pop(0)

        if limit_chars is not None:
            total = self._total_chars() + len(content)
            while self._messages and total > limit_chars:
                removed = self._messages.pop(0)
                total -= len(removed['content'])
            if total > limit_chars:
                excess = total - limit_chars
                content = content[excess:]

        self._messages.append({'role': ROLE_USER, 'content': content})
        return content

    def add_assistant(self, content: str) -> None:
        self._messages.append({'role': ROLE_ASSISTANT, 'content': content})

    def pop_last(self) -> None:
        if self._messages:
            self._messages.pop()

    def clear(self) -> None:
        self._messages.clear()

    def get_messages(self) -> list[MessageDict]:
        return list(self._messages)

    def message_count(self) -> int:
        return len(self._messages)


class LLMClient:
    def __init__(self, config: AppConfig) -> None:
        self._openai = OpenAI(api_key=config.api_key, base_url=config.api_host)
        self._model = config.model
        self._temperature = config.temperature

    def send(self, messages: list[MessageDict]) -> str:
        response = self._openai.chat.completions.create(
            model=self._model,
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=self._temperature,
        )
        return response.choices[0].message.content or ''

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
