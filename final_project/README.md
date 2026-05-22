# GigaVibeMiptCode

Консольный чат-бот с поддержкой любого OpenAI-совместимого API. Вроде всё работает)

## Как устроен проект

```
final_project/
├── bot.py       — конфиг, история сообщений, клиент к LLM
├── utils.py     — работа с файлами (подстановка @::путь::, разбивка на чанки)
├── main.py      — главный цикл и команды
├── __init__.py
├── __main__.py
├── ruff.toml
├── config.yaml.example
└── tests/
    ├── conftest.py
    ├── test_bot.py
    ├── test_utils.py
    └── test_commands.py
```

## Что реализовано

### Конфиг

Можно задать через переменные окружения или `config.yaml` (env имеет приоритет):

| Параметр | Env | YAML | По умолчанию |
|---|---|---|---|
| API-ключ | `API_KEY` | `api_key` | — |
| Хост | `API_HOST` | `api_host` | — |
| Модель | `MODEL` | `model` | gemma3:270m |
| Температура | `TEMPERATURE` | `temperature` | 0.7 |
| Лимит сообщений | `LIMIT_MESSAGE` | `limit_message` | — |
| Лимит символов | `LIMIT_CHARS` | `limit_chars` | — |
| Системный промпт | — | `system_prompt` | — |

`system_prompt` только через `config.yaml`, не через env — там могут быть секреты. `config.yaml` в `.gitignore`

### Управление контекстом

Когда история превышает лимит — старые сообщения вытесняются. Если одно сообщение длиннее `limit_chars` — обрезается слева

### Команды

| Команда | Что делает |
|---|---|
| `\q` | Выйти |
| `/reset` | Очистить историю и экран |
| `@::путь/к/файлу::` | Вставить содержимое файла в сообщение (лимит 5 МБ) |
| `/file_chunk [paragraph=N] [len=N] [-y]` | Обработать файл по чанкам |

### /file_chunk подробнее

Спрашивает путь к файлу и задание, потом отправляет каждый чанк отдельно

- `paragraph=N` — сколько абзацев в чанке (по умолчанию 1)
- `len=N` — разбивать по символам, а не абзацам
- `-y` — не спрашивать подтверждение между чанками

`Ctrl+C` во время ответа — отменяет текущий чанк и останавливает обработку

### Потоковый вывод и отмена

Ответ печатается токен за токеном. `Ctrl+C` во время ожидания — печатает `Запрос отменён.` и возвращает в диалог, незавершённый ответ в историю не попадает

## Запуск

Нужен Python 3.13+ и [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

Создать `final_project/config.yaml`:

```yaml
api_key: your_api_key
api_host: http://localhost:11434/v1
model: gemma3:4b
temperature: 0.7
limit_message: 20
system_prompt: Отвечай кратко и по делу.
```

Или через env:

```bash
API_KEY=your_key API_HOST=http://localhost:11434/v1 uv run python -m final_project
```

Запуск:

```bash
uv run python -m final_project
```

Если хочется использовать локально — подойдёт [Ollama](https://ollama.com):

```bash
ollama serve
ollama pull gemma3:4b
```

## Примеры

Обычный диалог:

```
>>> Привет
Привет! Чем могу помочь?
>>> \q
```

Вставка файла:

```
>>> Объясни этот код: @::main.py::
Этот файл содержит главный цикл...
```

Чанкование файла:

```
>>> /file_chunk paragraph=2 -y
>>> Укажите путь к файлу
>>> /tmp/document.txt
>>> Принято. Что делать с каждым фрагментом?
>>> Кратко перескажи
>>> Принято. Обработка:
В первых двух абзацах говорится о...
...
>>> Обработка файла завершена.
```

Ошибка конфига:

```
$ uv run python -m final_project
Ошибка конфигурации: Конфигурация не найдена. Задайте переменные окружения или создайте config.yaml.
```

## Тесты

```bash
uv run pytest final_project/tests/ -v
uv run pytest final_project/tests/ --cov=final_project --cov-report=html
```

Покрытие ~77%. Не покрыты функции с `input()` и реальными вызовами API

## Линтинг и типизация

```bash
uv run ruff check final_project/
uv run mypy final_project/
```

Конфиг линтера в `final_project/ruff.toml`, mypy в строгом режиме
