# LangChain API Agent

Минимальный AI-агент на LangChain — натурально-языковая обёртка над User Management API.

## Стек

| Компонент | Описание |
|-----------|----------|
| LangChain | 1.x |
| LLM | Ollama — `qwen3.5:9b` (локально) |
| API | FastAPI + uvicorn |
| Хранилище | SQLite (`users.db`, создаётся автоматически) |
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

SQLite-база `users.db` создаётся при первом запуске и сохраняется между сессиями.

---

## Инструменты агента

### API tools (`tools/api_tool.py`)

Выполняют реальные HTTP-запросы к FastAPI-серверу. Данные сохраняются в SQLite.

| Tool | HTTP-метод | Описание |
|------|------------|----------|
| `create_user(name, email)` | `POST /users` | Создать пользователя |
| `get_user(user_id)` | `GET /users/{id}` | Получить пользователя по ID |
| `update_user_status(user_id, status)` | `PATCH /users/{id}/status` | Обновить статус |
| `list_users()` | `GET /users` | Список всех пользователей |

Допустимые значения статуса: `active`, `inactive`, `banned`.

### LLM proxy tool (`tools/llm_tool.py`)

| Tool | Описание |
|------|----------|
| `ask_llm(prompt, system="")` | Проксирует любой запрос через агента к LLM и возвращает кастомный ответ. Не обращается к API и БД. |

Агент вызывает `ask_llm` для вопросов, объяснений и задач, не требующих обращения к API — переводы, резюме, генерация текста и т.д.  
Температура: `0.7` (переопределяется через `LLM_TOOL_TEMPERATURE` в `.env`).

---

## Хранилище данных

Используется **SQLite** (`users.db`). Схема таблицы:

```sql
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    status     TEXT    NOT NULL DEFAULT 'active'
                   CHECK(status IN ('active', 'inactive', 'banned')),
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

База инициализируется в `api/database.py` через lifespan-хук FastAPI при старте сервера.  
Путь к файлу переопределяется через `DB_PATH` в `.env`.

---

## Контракт ответа

Агент всегда отвечает в следующем формате (см. `prompts/system.md`):

```
Status: success | error
Action: <описание выполненного действия>
Data: <результат или "none">
Errors: <описание ошибки или "none">
```

---

## Структура проекта

```
agent/
├── api/
│   ├── database.py     # SQLite: подключение и init_db()
│   └── server.py       # FastAPI: эндпоинты, lifespan
├── tools/
│   ├── api_tool.py     # LangChain tools → реальные HTTP-вызовы к API
│   └── llm_tool.py     # LangChain tool → прокси-запрос через агента к LLM
├── prompts/
│   └── system.md       # Системный промпт и документация по инструментам
├── agent.py            # Сборка агента (create_agent + ChatOllama)
├── main.py             # CLI (один запрос)
├── run_tests.py        # 5 тестовых запросов
├── requirements.txt
├── .env.example
└── report.md
```

---

## Настройка

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Адрес Ollama |
| `OLLAMA_MODEL` | `qwen3.5:9b` | Модель для агента и ask_llm |
| `LLM_TOOL_TEMPERATURE` | `0.7` | Температура для ask_llm |
| `API_BASE_URL` | `http://127.0.0.1:8000` | Адрес FastAPI-сервера |
| `DB_PATH` | `users.db` | Путь к SQLite-базе |

---

## Подтверждение вызовов tool

Файл `tools/api_tool.py` — реальные HTTP-вызовы и дебаг-вывод:

- `create_user` — вызов **L21**, дебаг **L22–23**
- `get_user` — вызов **L34**, дебаг **L35–37**
- `update_user_status` — вызов **L47**, дебаг **L48–50**
- `list_users` — вызов **L61**, дебаг **L62–64**

Файл `tools/llm_tool.py` — прокси через `ChatOllama.invoke()`, дебаг **L37–38**.
