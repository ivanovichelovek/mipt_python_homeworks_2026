from dataclasses import dataclass, field

ROLE_USER = 'user'
ROLE_ASSISTANT = 'assistant'
ROLE_SYSTEM = 'system'

MessageDict = dict[str, str]


@dataclass
class MessageHistory:
    _messages: list[MessageDict] = field(default_factory=list, init=False)

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

    @property
    def messages(self) -> list[MessageDict]:
        return list(self._messages)

    def message_count(self) -> int:
        return len(self._messages)

    def _total_chars(self) -> int:
        return sum(len(m['content']) for m in self._messages)
