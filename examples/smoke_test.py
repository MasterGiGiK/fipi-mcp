"""Ручной/CI smoke: тянем страницу задач и проверку ответа.

Запуск:
    python -m examples.smoke_test

Возвращает exit=1 при провале любой проверки — годится для CI.
"""
from __future__ import annotations

import json
import sys

from fipi_mcp.client import FipiClient
from fipi_mcp.parser import parse_tasks
from fipi_mcp.subjects import resolve


def _check(cond: bool, msg: str) -> None:
    status = "OK" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        sys.exit(1)


def main() -> None:
    name, guid = resolve("math_prof")
    print(f"Subject: {name}")

    with FipiClient() as client:
        html = client.questions(guid, page=0, pagesize=5)
        tasks = parse_tasks(html)

        print(f"Fetched {len(tasks)} tasks from page 0")
        _check(len(tasks) >= 3, "at least 3 tasks parsed")

        first = tasks[0]
        _check(len(first["qid"]) == 6, "qid is 6 hex chars")
        _check(len(first["guid"]) == 32, "guid is 32 hex chars")
        _check(bool(first["condition_text"]), "condition_text is non-empty")
        _check(first["answer_type"] is not None, "answer_type parsed")

        # ФИПИ solve.php: 3=correct, 2=wrong. Проверяем известную задачу.
        target = next((t for t in tasks if t["qid"] == "40B442"), None)
        if target is not None:
            code_ok = client.solve(guid, target["guid"], "29")
            code_bad = client.solve(guid, target["guid"], "30")
            print(f"  solve('29') -> {code_ok!r}, solve('30') -> {code_bad!r}")
            _check(code_ok == "3", "correct answer for 40B442 returns code 3")
            _check(code_bad == "2", "wrong answer for 40B442 returns code 2")

    print("\nSample task:")
    print(json.dumps(
        {k: v for k, v in tasks[0].items() if k != "condition_html"},
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
