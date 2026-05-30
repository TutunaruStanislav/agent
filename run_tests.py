"""Run 5 test queries against the agent with a single shared API server instance.

Usage:
    python run_tests.py
"""
import threading
import time

import uvicorn


def _start_api():
    config = uvicorn.Config(
        "api.server:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    server.run()


TEST_QUERIES = [
    # 1 — create (→ create_user)
    "Создай пользователя с именем Alice и email alice@example.com",
    # 2 — create (→ create_user)
    "Добавь нового пользователя Bob, его email bob@example.com",
    # 3 — list (→ list_users)
    "Покажи список всех пользователей",
    # 4 — update status (→ update_user_status)
    "Заблокируй пользователя с ID 1",
    # 5 — get (→ list_users or get_user for count)
    "Сколько пользователей сейчас в системе?",
]


def run():
    t = threading.Thread(target=_start_api, daemon=True)
    t.start()
    time.sleep(1.5)

    from agent import run_query

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {query}")
        print("=" * 60)
        response = run_query(query)
        print("\n--- AGENT RESPONSE ---")
        print(response)


if __name__ == "__main__":
    run()
