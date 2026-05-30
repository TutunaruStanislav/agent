"""CLI entry point.

Usage:
    python main.py "create user Alex with email alex@example.com"

Starts the mock API server in a background daemon thread, runs the agent,
prints the result, then exits.
"""
import sys
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


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "your request"')
        sys.exit(1)

    query = sys.argv[1]

    t = threading.Thread(target=_start_api, daemon=True)
    t.start()
    time.sleep(1.5)  # wait for uvicorn to be ready

    from agent import run_query
    response = run_query(query)

    print("\n" + "=" * 60)
    print("AGENT RESPONSE")
    print("=" * 60)
    print(response)


if __name__ == "__main__":
    main()
