# LangChain API Agent

Минимальный AI-агент на LangChain — натурально-языковая обёртка над User Management API.

## Стек

| Компонент | Версия |
|-----------|--------|
| LangChain | 1.x |
| LLM | Ollama — `qwen3.5:9b` (локально) |
| Mock API | FastAPI + uvicorn (in-memory) |
| HTTP-клиент | httpx |

---

## Предварительные требования

Установите [Ollama](https://ollama.com) и загрузите модель:

```bash
ollama pull qwen3.5:9b
# убедитесь что сервер запущен: ollama serve
```

---

## Быстрый старт

```bash
# 1. Перейти в директорию
cd agent

# 2. Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения (опционально — defaults работают)
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/macOS

# 5. Один запрос через CLI
python main.py "создай пользователя с именем Alex и email alex@example.com"

# 6. Все 5 тестовых запросов
python run_tests.py
```

---

## Поддерживаемые операции

### API tools (`tools/api_tool.py`)

| Операция | Tool | HTTP-метод |
|----------|------|------------|
| Создать пользователя | `create_user(name, email)` | `POST /users` |
| Получить пользователя | `get_user(user_id)` | `GET /users/{id}` |
| Обновить статус | `update_user_status(user_id, status)` | `PATCH /users/{id}/status` |
| Список пользователей | `list_users()` | `GET /users` |

Допустимые значения статуса: `active`, `inactive`, `banned`.

### LLM proxy tool (`tools/llm_tool.py`)

| Tool | Назначение |
|------|-----------|
| `ask_llm(prompt, system="")` | Проксирует любой запрос через `ChatOllama` к LLM и возвращает кастомный ответ |

Использует тот же `OLLAMA_MODEL` / `OLLAMA_BASE_URL`, что и основной агент.  
Температура: `0.7` (переопределяется через `LLM_TOOL_TEMPERATURE` в `.env`).

---

## Контракт ответа

Агент всегда отвечает в следующем формате (см. `prompts/system.md`):

```
Status: success | error
Action: <описание выполненного действия>
Data: <результат API или "none">
Errors: <описание ошибки или "none">
```

---

## Структура проекта

```
agent/
├── api/
│   └── server.py       # FastAPI mock API
├── tools/
│   └── api_tool.py     # LangChain tools (реальные HTTP-вызовы)
├── prompts/
│   └── system.md       # Системный промпт + шаблоны
├── agent.py            # Сборка агента (ChatOllama)
├── main.py             # CLI (один запрос)
├── run_tests.py        # 5 тестовых запросов
├── requirements.txt
├── .env.example
└── report.md
```

---

## Смена модели Ollama

В `.env` укажите нужную модель:

```env
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Подтверждение вызовов tool

Файл: `tools/api_tool.py`

- `create_user` — реальный HTTP-вызов на **L21**, дебаг-вывод на **L22–23**
- `get_user` — вызов на **L34**, дебаг на **L35–37**
- `update_user_status` — вызов на **L47**, дебаг на **L48–50**
- `list_users` — вызов на **L61**, дебаг на **L62–64**
