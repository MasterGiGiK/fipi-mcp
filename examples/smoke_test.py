"""Ручной тест без запуска MCP: тянем страницу, парсим, печатаем 2 задачи.

Запуск (из корня проекта):
    python -m examples.smoke_test
"""
from __future__ import annotations

import json

from fipi_mcp.client import FipiClient
from fipi_mcp.parser import parse_tasks
from fipi_mcp.subjects import resolve


def main() -> None:
    name, guid = resolve("math_prof")
    with FipiClient() as client:
        html = client.questions(guid, page=0, pagesize=5)
    tasks = parse_tasks(html)
    print(f"Subject: {name}")
    print(f"Fetched {len(tasks)} tasks")
    for task in tasks[:2]:
        print("=" * 60)
        print(json.dumps(
            {k: v for k, v in task.items() if k != "condition_html"},
            ensure_ascii=False,
            indent=2,
        ))


if __name__ == "__main__":
    main()
