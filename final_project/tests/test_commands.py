from collections.abc import Callable

from final_project.bot import AppConfig
from final_project.main import (
    FILE_CHUNK_CMD,
    _build_chunk_messages,
    _parse_chunk_args,
)


def test_parse_chunk_args_defaults() -> None:
    paragraph_count, char_len, auto = _parse_chunk_args(FILE_CHUNK_CMD)
    assert paragraph_count == 1
    assert char_len is None
    assert auto is False


def test_parse_chunk_args_paragraph() -> None:
    paragraph_count, char_len, auto = _parse_chunk_args(f'{FILE_CHUNK_CMD} paragraph=3')
    assert paragraph_count == 3
    assert char_len is None


def test_parse_chunk_args_len() -> None:
    paragraph_count, char_len, auto = _parse_chunk_args(f'{FILE_CHUNK_CMD} len=500')
    assert char_len == 500


def test_parse_chunk_args_auto_flag() -> None:
    _, _, auto = _parse_chunk_args(f'{FILE_CHUNK_CMD} -y')
    assert auto is True


def test_parse_chunk_args_combined() -> None:
    paragraph_count, char_len, auto = _parse_chunk_args(
        f'{FILE_CHUNK_CMD} paragraph=2 len=300 -y'
    )
    assert paragraph_count == 2
    assert char_len == 300
    assert auto is True


def test_build_chunk_messages_no_system_prompt(make_config: Callable[..., AppConfig]) -> None:
    config = make_config()
    messages = _build_chunk_messages('chunk text', 'summarize', config)
    assert len(messages) == 1
    assert messages[0]['role'] == 'user'
    assert 'summarize' in messages[0]['content']
    assert 'chunk text' in messages[0]['content']


def test_build_chunk_messages_with_system_prompt(make_config: Callable[..., AppConfig]) -> None:
    config = make_config(system_prompt='Be concise.')
    messages = _build_chunk_messages('chunk text', 'summarize', config)
    assert len(messages) == 2
    assert messages[0]['role'] == 'system'
    assert messages[0]['content'] == 'Be concise.'


def test_build_chunk_messages_content_format(make_config: Callable[..., AppConfig]) -> None:
    config = make_config()
    messages = _build_chunk_messages('the text', 'do this', config)
    assert messages[0]['content'] == 'do this\n\nthe text'
