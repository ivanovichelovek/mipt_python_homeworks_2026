from pathlib import Path

from final_project.client import LLMClient
from final_project.config import AppConfig
from final_project.history import ROLE_SYSTEM, ROLE_USER, MessageDict, MessageHistory
from final_project.utils import expand_file_references, split_by_length, split_by_paragraphs

PROMPT = '>>> '
QUIT_CMD = r'\q'
RESET_CMD = '/reset'
FILE_CHUNK_CMD = '/file_chunk'


def _build_messages(history: MessageHistory, config: AppConfig) -> list[MessageDict]:
    messages: list[MessageDict] = []
    if config.system_prompt:
        messages.append({'role': ROLE_SYSTEM, 'content': config.system_prompt})
    messages.extend(history.messages)
    return messages


def _collect_response(client: LLMClient, messages: list[MessageDict]) -> str | None:
    full_response = ''
    try:
        for token in client.send_stream(messages):
            print(token, end='', flush=True)
            full_response += token
    except KeyboardInterrupt:
        print('\nЗапрос отменён.')
        return None
    except Exception as e:
        print(f'Ошибка LLM: {e}')
        return None
    print()
    return full_response


def _send_and_collect(client: LLMClient, history: MessageHistory, config: AppConfig) -> None:
    messages = _build_messages(history, config)
    full_response = _collect_response(client, messages)
    if full_response is None:
        history.pop_last()
        return
    history.add_assistant(full_response)


def handle_reset(history: MessageHistory) -> None:
    history.clear()
    print('\033[2J\033[H', end='')
    print('История чата очищена.')


def _parse_chunk_args(cmd: str) -> tuple[int, int | None, bool]:
    parts = cmd.split()
    paragraph_count = 1
    char_len: int | None = None
    auto = '-y' in parts

    for part in parts[1:]:
        if part.startswith('paragraph='):
            paragraph_count = int(part.split('=', 1)[1])
        elif part.startswith('len='):
            char_len = int(part.split('=', 1)[1])

    return paragraph_count, char_len, auto


def _build_chunk_messages(chunk: str, user_prompt: str, config: AppConfig) -> list[MessageDict]:
    messages: list[MessageDict] = []
    if config.system_prompt:
        messages.append({'role': ROLE_SYSTEM, 'content': config.system_prompt})
    messages.append({'role': ROLE_USER, 'content': f'{user_prompt}\n\n{chunk}'})
    return messages


def _read_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding='utf-8')
    except OSError as e:
        print(f'Не удалось прочитать файл: {e}')
        return None


def _stream_chunk(client: LLMClient, messages: list[MessageDict]) -> bool:
    try:
        for token in client.send_stream(messages):
            print(token, end='', flush=True)
    except KeyboardInterrupt:
        print('\nОбработка фрагмента отменена.')
        return False
    print()
    return True


def _process_chunks(
    chunks: list[str], user_prompt: str, client: LLMClient, config: AppConfig, auto: bool
) -> None:
    for i, chunk in enumerate(chunks):
        messages = _build_chunk_messages(chunk, user_prompt, config)
        if not _stream_chunk(client, messages):
            return
        is_last = i == len(chunks) - 1
        if not is_last and not auto:
            input(f'{PROMPT}')


def handle_file_chunk(cmd: str, client: LLMClient, config: AppConfig) -> None:
    file_path_str = input(f'{PROMPT}Укажите путь к файлу\n{PROMPT}').strip()
    path = Path(file_path_str)

    if not path.exists():
        print(f'Файл не найден: {path}')
        return

    text = _read_file(path)
    if text is None:
        return

    user_prompt = input(f'{PROMPT}Принято. Что делать с каждым фрагментом?\n{PROMPT}').strip()
    paragraph_count, char_len, auto = _parse_chunk_args(cmd)

    if char_len is None:
        chunks = split_by_paragraphs(text, paragraph_count)
    else:
        chunks = split_by_length(text, char_len)

    if not chunks:
        print('Обработка файла завершена.')
        return

    print(f'{PROMPT}Принято. Обработка:')
    _process_chunks(chunks, user_prompt, client, config, auto)
    print(f'{PROMPT}Обработка файла завершена.')


def process_input(
    user_input: str, history: MessageHistory, client: LLMClient, config: AppConfig
) -> bool:
    if user_input == QUIT_CMD:
        return False

    if user_input == RESET_CMD:
        handle_reset(history)
        return True

    if user_input.startswith(FILE_CHUNK_CMD):
        handle_file_chunk(user_input, client, config)
        return True

    expanded, warnings = expand_file_references(user_input)
    for w in warnings:
        print(w)

    history.prepare_and_add(expanded, config.limit_message, config.limit_chars)
    _send_and_collect(client, history, config)
    return True
