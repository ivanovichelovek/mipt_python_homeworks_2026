from collections.abc import Callable
from typing import Any

import pytest

from final_project.bot import AppConfig


@pytest.fixture
def make_config() -> Callable[..., AppConfig]:
    def factory(**kwargs: Any) -> AppConfig:
        defaults: dict[str, Any] = {
            'api_key': 'key',
            'api_host': 'http://host/v1',
            'model': 'gemma3',
            'limit_message': None,
            'limit_chars': None,
            'temperature': 0.5,
            'system_prompt': None,
        }
        defaults.update(kwargs)
        return AppConfig(**defaults)

    return factory
