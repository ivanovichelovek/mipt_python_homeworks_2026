from pathlib import Path

import pytest

from final_project.utils import (
    expand_file_references,
    split_by_length,
    split_by_paragraphs,
)


def test_expand_no_references() -> None:
    result, warnings = expand_file_references('plain message')
    assert result == 'plain message'
    assert warnings == []


def test_expand_replaces_file_content(tmp_path: Path) -> None:
    f = tmp_path / 'hello.txt'
    f.write_text('file content')
    msg = f'read this: @::{f}::'
    result, warnings = expand_file_references(msg)
    assert 'file content' in result
    assert warnings == []


def test_expand_multiple_references(tmp_path: Path) -> None:
    f1 = tmp_path / 'a.txt'
    f2 = tmp_path / 'b.txt'
    f1.write_text('AAA')
    f2.write_text('BBB')
    result, warnings = expand_file_references(f'@::{f1}:: and @::{f2}::')
    assert 'AAA' in result
    assert 'BBB' in result
    assert warnings == []


def test_expand_file_not_found() -> None:
    result, warnings = expand_file_references('@::/nonexistent/file.txt::')
    assert '@::' in result
    assert len(warnings) == 1
    assert 'не найден' in warnings[0].lower()


def test_expand_file_too_large(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / 'big.txt'
    f.write_text('data')

    monkeypatch.setattr('final_project.utils.MAX_FILE_SIZE_BYTES', 1)
    result, warnings = expand_file_references(f'@::{f}::')
    assert '@::' in result
    assert len(warnings) == 1
    assert '5 МБ' in warnings[0]


def test_expand_path_with_spaces_in_between(tmp_path: Path) -> None:
    f = tmp_path / 'code.py'
    f.write_text('print(1/0)')
    result, warnings = expand_file_references(f'before @::{f}:: after')
    assert 'print(1/0)' in result
    assert 'before' in result
    assert 'after' in result


def test_split_by_paragraphs_single() -> None:
    text = 'line1\nline2\nline3'
    chunks = split_by_paragraphs(text, 1)
    assert chunks == ['line1', 'line2', 'line3']


def test_split_by_paragraphs_multiple() -> None:
    text = 'p1\np2\np3\np4\np5'
    chunks = split_by_paragraphs(text, 2)
    assert len(chunks) == 3
    assert chunks[0] == 'p1\np2'
    assert chunks[1] == 'p3\np4'
    assert chunks[2] == 'p5'


def test_split_by_paragraphs_skips_blank_lines() -> None:
    text = 'a\n\n\nb\n\nc'
    chunks = split_by_paragraphs(text, 1)
    assert chunks == ['a', 'b', 'c']


def test_split_by_length_basic() -> None:
    text = 'abcdefgh'
    chunks = split_by_length(text, 3)
    assert chunks == ['abc', 'def', 'gh']


def test_split_by_length_exact() -> None:
    text = 'abcdef'
    chunks = split_by_length(text, 3)
    assert chunks == ['abc', 'def']


def test_split_by_length_empty() -> None:
    assert split_by_length('', 10) == []


def test_split_by_paragraphs_empty() -> None:
    assert split_by_paragraphs('', 1) == []
