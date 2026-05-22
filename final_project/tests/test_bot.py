from collections.abc import Callable
from pathlib import Path

import pytest

from final_project.bot import (
    ERR_LIMIT_CHARS,
    ERR_LIMIT_MESSAGE,
    ERR_NO_API_HOST,
    ERR_NO_API_KEY,
    ERR_NO_CONFIG,
    ERR_TEMPERATURE,
    AppConfig,
    MessageHistory,
    _build,
    _validate,
    load_config,
)

BASE_ENV = {'API_KEY': 'test-key', 'API_HOST': 'http://localhost:11434/v1'}


def test_build_from_env_only() -> None:
    config = _build(BASE_ENV, {})
    assert config.api_key == 'test-key'
    assert config.api_host == 'http://localhost:11434/v1'


def test_build_from_yaml_only() -> None:
    yaml_cfg = {'api_key': 'yaml-key', 'api_host': 'http://yaml-host/v1'}
    config = _build({}, yaml_cfg)
    assert config.api_key == 'yaml-key'


def test_env_overrides_yaml() -> None:
    yaml_cfg = {'api_key': 'yaml-key', 'api_host': 'http://yaml-host/v1'}
    config = _build(BASE_ENV, yaml_cfg)
    assert config.api_key == 'test-key'


def test_missing_api_key_raises() -> None:
    with pytest.raises(ValueError, match=ERR_NO_API_KEY):
        _build({'API_HOST': 'http://host/v1'}, {})


def test_missing_api_host_raises() -> None:
    with pytest.raises(ValueError, match=ERR_NO_API_HOST):
        _build({'API_KEY': 'key'}, {})


def test_system_prompt_from_yaml_only() -> None:
    yaml_cfg = {
        'api_key': 'k',
        'api_host': 'http://h/v1',
        'system_prompt': 'Be concise.',
    }
    config = _build({}, yaml_cfg)
    assert config.system_prompt == 'Be concise.'


def test_system_prompt_not_from_env() -> None:
    env = {**BASE_ENV, 'system_prompt': 'ignored'}
    config = _build(env, {})
    assert config.system_prompt is None


def test_limit_message_parsed() -> None:
    config = _build({**BASE_ENV, 'LIMIT_MESSAGE': '10'}, {})
    assert config.limit_message == 10


def test_limit_chars_parsed() -> None:
    config = _build({**BASE_ENV, 'LIMIT_CHARS': '2000'}, {})
    assert config.limit_chars == 2000


def test_temperature_parsed() -> None:
    config = _build({**BASE_ENV, 'TEMPERATURE': '0.3'}, {})
    assert config.temperature == pytest.approx(0.3)


def test_validate_bad_temperature(make_config: Callable[..., AppConfig]) -> None:
    config = make_config(temperature=1.5)
    with pytest.raises(ValueError, match=ERR_TEMPERATURE):
        _validate(config)


def test_validate_zero_limit_message(make_config: Callable[..., AppConfig]) -> None:
    config = make_config(limit_message=0)
    with pytest.raises(ValueError, match=ERR_LIMIT_MESSAGE):
        _validate(config)


def test_validate_negative_limit_chars(make_config: Callable[..., AppConfig]) -> None:
    config = make_config(limit_chars=-1)
    with pytest.raises(ValueError, match=ERR_LIMIT_CHARS):
        _validate(config)


def test_load_config_no_config_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    for key in ('API_KEY', 'API_HOST', 'LIMIT_MESSAGE', 'LIMIT_CHARS', 'TEMPERATURE', 'MODEL'):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match=ERR_NO_CONFIG):
        load_config()


def test_prepare_and_add_basic() -> None:
    history = MessageHistory()
    result = history.prepare_and_add('hello', None, None)
    assert result == 'hello'
    assert history.message_count() == 1
    assert history.get_messages()[0]['content'] == 'hello'
    assert history.get_messages()[0]['role'] == 'user'


def test_add_assistant() -> None:
    history = MessageHistory()
    history.prepare_and_add('hi', None, None)
    history.add_assistant('hello back')
    messages = history.get_messages()
    assert len(messages) == 2
    assert messages[1]['role'] == 'assistant'
    assert messages[1]['content'] == 'hello back'


def test_limit_message_trims_oldest() -> None:
    history = MessageHistory()
    for i in range(4):
        history.prepare_and_add(f'msg{i}', None, None)
        history.add_assistant(f'resp{i}')
    history.prepare_and_add('new', 4, None)
    contents = [m['content'] for m in history.get_messages()]
    assert 'msg0' not in contents
    assert 'new' in contents
    assert history.message_count() == 4


def test_limit_chars_trims_oldest() -> None:
    history = MessageHistory()
    history.prepare_and_add('aaa', None, None)
    history.add_assistant('bbb')
    history.prepare_and_add('ccc', None, None)
    history.add_assistant('ddd')
    history.prepare_and_add('eee', None, 10)
    total = sum(len(m['content']) for m in history.get_messages())
    assert total <= 10


def test_limit_chars_truncates_message_if_exceeds_alone() -> None:
    history = MessageHistory()
    long_msg = 'x' * 20
    result = history.prepare_and_add(long_msg, None, 5)
    assert len(result) <= 5
    assert history.message_count() == 1


def test_both_limits_applied() -> None:
    history = MessageHistory()
    for i in range(6):
        history.prepare_and_add(f'm{i}', None, None)
    history.prepare_and_add('new', 4, 100)
    assert history.message_count() <= 4


def test_pop_last() -> None:
    history = MessageHistory()
    history.prepare_and_add('keep', None, None)
    history.prepare_and_add('remove', None, None)
    history.pop_last()
    assert history.message_count() == 1
    assert history.get_messages()[0]['content'] == 'keep'


def test_clear() -> None:
    history = MessageHistory()
    history.prepare_and_add('something', None, None)
    history.clear()
    assert history.message_count() == 0


def test_get_messages_returns_copy() -> None:
    history = MessageHistory()
    history.prepare_and_add('a', None, None)
    messages = history.get_messages()
    messages.clear()
    assert history.message_count() == 1
