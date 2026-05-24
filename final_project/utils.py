import re
from pathlib import Path

FILE_REF_PATTERN = re.compile(r'@::(.*?)::')
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

WARN_NOT_FOUND = 'Предупреждение: файл не найден: {path}'
WARN_TOO_LARGE = 'Предупреждение: файл {path} превышает лимит 5 МБ, пропускается.'
WARN_READ_ERROR = 'Предупреждение: не удалось прочитать {path}: {error}'


def expand_file_references(message: str) -> tuple[str, list[str]]:
    warnings: list[str] = []

    def replace(match: re.Match[str]) -> str:
        path = Path(match.group(1))
        if not path.exists():
            warnings.append(WARN_NOT_FOUND.format(path=path))
            return match.group(0)
        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            warnings.append(WARN_TOO_LARGE.format(path=path))
            return match.group(0)
        try:
            return path.read_text(encoding='utf-8')
        except OSError as e:
            warnings.append(WARN_READ_ERROR.format(path=path, error=e))
            return match.group(0)

    return FILE_REF_PATTERN.sub(replace, message), warnings


def split_by_paragraphs(text: str, count: int) -> list[str]:
    lines = [line for line in text.split('\n') if line.strip()]
    chunks = []
    for i in range(0, len(lines), count):
        chunk = '\n'.join(lines[i : i + count])
        if chunk:
            chunks.append(chunk)
    return chunks


def split_by_length(text: str, length: int) -> list[str]:
    return [text[i : i + length] for i in range(0, len(text), length)]
