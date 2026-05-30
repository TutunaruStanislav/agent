# Отчёт по домашнему заданию

## 1. LLM и настройка

**Провайдер:** Ollama (локальный)  
**Модель:** `qwen3.5:9b` (переопределяется через `OLLAMA_MODEL` в `.env`)  
**Пакет:** `langchain-ollama>=0.2.0`

Настройка:
```bash
# Установить Ollama: https://ollama.com
ollama pull qwen3.5:9b
ollama serve          # запустить сервер (если не запущен)
cp .env.example .env  # опционально, defaults работают
```

---

## 2. API и поддерживаемые операции

**Домен:** User Management (управление пользователями)  
**Реализация:** локальный mock на FastAPI (`api/server.py`), in-memory хранилище, запускается автоматически при старте агента.

| # | Операция | HTTP | Tool |
|---|----------|------|------|
| 1 | Создать пользователя | `POST /users` | `create_user` |
| 2 | Получить пользователя | `GET /users/{id}` | `get_user` |
| 3 | Обновить статус | `PATCH /users/{id}/status` | `update_user_status` |
| 4 | Список всех пользователей | `GET /users` | `list_users` |

---

## 3. Как запустить

```bash
pip install -r requirements.txt
# Ollama должен быть запущен: ollama serve

# Один запрос:
python main.py "создай пользователя с именем Maria, email maria@test.com"

# Все тесты:
python run_tests.py
```

---

## 4. Тестовые запросы и результаты

### Запрос 1 — Создать пользователя Alice (→ `create_user`)

**Ввод:**
```
Создай пользователя с именем Alice и email alice@example.com
```

**Вывод консоли (дебаг tool):**
```
[TOOL] POST /users  name='Alice' email='alice@example.com'
[TOOL] response 201: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'status': 'active'}
```

**Ответ агента:**
```
Status: success
Action: Created a new user named Alice with email alice@example.com
Data: {"success": true, "user": {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active"}}
Errors: none
```

---

### Запрос 2 — Создать пользователя Bob (→ `create_user`)

**Ввод:**
```
Добавь нового пользователя Bob, его email bob@example.com
```

**Вывод консоли:**
```
[TOOL] POST /users  name='Bob' email='bob@example.com'
[TOOL] response 201: {'id': 2, 'name': 'Bob', 'email': 'bob@example.com', 'status': 'active'}
```

**Ответ агента:**
```
Status: success
Action: Created a new user named Bob with email bob@example.com
Data: {"success": true, "user": {"id": 2, "name": "Bob", "email": "bob@example.com", "status": "active"}}
Errors: none
```

---

### Запрос 3 — Список пользователей (→ `list_users`)

**Ввод:**
```
Покажи список всех пользователей
```

**Вывод консоли:**
```
[TOOL] GET /users
[TOOL] response 200: {'users': [{'id': 1, ...}, {'id': 2, ...}], 'total': 2}
```

**Ответ агента:**
```
Status: success
Action: Retrieved the list of all users
Data: {"users": [{"id": 1, "name": "Alice", ...}, {"id": 2, "name": "Bob", ...}], "total": 2}
Errors: none
```

---

### Запрос 4 — Заблокировать пользователя (→ `update_user_status`)

**Ввод:**
```
Заблокируй пользователя с ID 1
```

**Вывод консоли:**
```
[TOOL] PATCH /users/1/status  status='banned'
[TOOL] response 200: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'status': 'banned'}
```

**Ответ агента:**
```
Status: success
Action: Пользователь с ID 1 заблокирован (статус изменён на banned)
Data: {"success": true, "user": {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "banned"}}
Errors: none
```

---

### Запрос 5 — Количество пользователей (→ `list_users`)

**Ввод:**
```
Сколько пользователей сейчас в системе?
```

**Вывод консоли:**
```
[TOOL] GET /users
[TOOL] response 200: {'users': [{'id': 1, 'name': 'Alice', ...}, {'id': 2, 'name': 'Bob', ...}], 'total': 2}
```

**Ответ агента:**
```
Status: success
Action: Получен список всех пользователей с общей статистикой
Data: {"users": [...], "total": 2}
Errors: none
```

---

## 5. Используемые промпты

### Системный промпт (`agent.py:_SYSTEM_PROMPT`, полное описание в `prompts/system.md`)

```
You are a User Management API Operator.
Your sole job is to interact with the User Management API on behalf of the user.

Available operations:
1. create_user(name, email)
2. get_user(user_id)
3. update_user_status(user_id, status)
4. list_users()

Constraints:
- You MUST use a tool for every data-changing or data-fetching request.
- You CANNOT perform operations not listed above.
- If required parameters are missing, ask the user before calling the tool.
- Never invent or guess user IDs.

Always reply in exactly this format:
Status: success | error
Action: <one-sentence description>
Data: <tool result or "none">
Errors: <error details, or "none">
```

### Пользовательский шаблон

```
{input}
```

---

## 6. Критерии выполнения

| Критерий | Выполнено | Ссылка |
|----------|-----------|--------|
| Агент запускается по инструкции | ✅ | README.md |
| Минимум один API-tool с реальным вызовом | ✅ | `tools/api_tool.py:L21,34,47,61` |
| Дебаг-вывод tool | ✅ | `tools/api_tool.py:L22–23,35–37,48–50,62–64` |
| Агент корректно интерпретирует запросы | ✅ | 5 примеров выше |
| Контракт ответа | ✅ | `prompts/system.md`, `agent.py:L22–35` |
| 5 проверочных запросов (3+ с tool) | ✅ | Раздел 4 (все 5 вызывают tool) |
| Промпты оформлены | ✅ | `prompts/system.md`, `report.md` раздел 5 |
| Секреты не закоммичены | ✅ | `.gitignore`, `.env.example` |
