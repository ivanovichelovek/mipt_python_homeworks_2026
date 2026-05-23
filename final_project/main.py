from .client import LLMClient
from .commands import PROMPT, process_input
from .config import load_config
from .history import MessageHistory


def main() -> None:
    try:
        config = load_config()
    except (ValueError, RuntimeError) as e:
        print(f'Ошибка конфигурации: {e}')
        return

    client = LLMClient(config)
    history = MessageHistory()

    while True:
        try:
            user_input = input(PROMPT).strip()
        except EOFError:
            break

        if not user_input:
            continue

        if not process_input(user_input, history, client, config):
            break
