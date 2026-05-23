import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

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
    'API-ключ не настроен. Укажите API_KEY в переменных окружения или api_key в config.yaml.'
)
ERR_NO_API_HOST = (
    'Хост API не настроен. Укажите API_HOST в переменных окружения или api_host в config.yaml.'
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
        temperature=float(str(raw_temperature))
        if raw_temperature is not None
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
