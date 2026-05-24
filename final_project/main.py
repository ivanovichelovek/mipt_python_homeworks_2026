from final_project.client import LLMClient
from final_project.commands import PROMPT, process_input
from final_project.config import AppConfig, load_config
from final_project.history import MessageHistory


def _read_input() -> str | None:
    try:
        return input(PROMPT).strip()
    except EOFError:
        return None


def _handle_input(
    user_input: str, history: MessageHistory, client: LLMClient, config: AppConfig
) -> bool:
    if not user_input:
        return True
    return process_input(user_input, history, client, config)


def _run_loop(client: LLMClient, history: MessageHistory, config: AppConfig) -> None:
    while True:
        user_input = _read_input()
        if user_input is None:
            break
        if not _handle_input(user_input, history, client, config):
            break


def main() -> None:
    try:
        config = load_config()
    except (ValueError, RuntimeError) as e:
        print(f'Ошибка конфигурации: {e}')
        return
    _run_loop(LLMClient(config), MessageHistory(), config)
