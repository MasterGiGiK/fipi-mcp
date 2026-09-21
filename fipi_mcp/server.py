from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from .client import FipiClient
from .parser import parse_tasks
from .subjects import SUBJECTS_EGE, resolve

mcp = MCPServer("fipi-bank")


@mcp.tool()
def list_subjects() -> list[dict[str, str]]:
    """Список предметов ЕГЭ, доступных в открытом банке ФИПИ."""
    return [
        {"key": key, "name": name, "proj_guid": guid}
        for key, (name, guid) in SUBJECTS_EGE.items()
    ]


@mcp.tool()
def list_tasks(subject: str, page: int = 0, pagesize: int = 10) -> dict[str, Any]:
    """Список заданий по предмету.

    subject — ключ ('physics'), русское название или proj-GUID.
    page — номер страницы с нуля.
    pagesize — размер страницы (обычно 10 или 20).
    """
    name, guid = resolve(subject)
    with FipiClient() as client:
        html = client.questions(guid, page=page, pagesize=pagesize)
    return {
        "subject": name,
        "proj_guid": guid,
        "page": page,
        "pagesize": pagesize,
        "tasks": parse_tasks(html),
    }


@mcp.tool()
def get_task(subject: str, qid: str, max_pages: int = 50) -> dict[str, Any]:
    """Найти задание по короткому 6-hex qid, перебирая страницы предмета.

    Дороже, чем list_tasks — используй, если знаешь qid, но нет `guid`.
    max_pages — верхняя граница перебора.
    """
    name, guid = resolve(subject)
    target = qid.strip().upper()
    with FipiClient() as client:
        for page in range(max_pages):
            html = client.questions(guid, page=page, pagesize=20)
            tasks = parse_tasks(html)
            if not tasks:
                break
            for task in tasks:
                if task["qid"].upper() == target:
                    return {"subject": name, "proj_guid": guid, **task}
    raise ValueError(f"Задание {qid} не найдено в предмете {name} за {max_pages} страниц")


@mcp.tool()
def check_answer(subject: str, guid: str, answer: str) -> dict[str, Any]:
    """Проверить ответ через solve.php ФИПИ. `guid` — полный 32-hex ID задания
    (не короткий qid). Клиент сам прогревает сессию перед POST-ом.

    Коды ФИПИ (расшифрованы экспериментально): 3=correct, 2=wrong, 0=not_found.
    """
    name, proj_guid = resolve(subject)
    with FipiClient() as client:
        raw = client.solve(proj_guid, guid, answer)
    mapping = {"3": "correct", "2": "wrong", "0": "not_found", "1": "correct"}
    if raw in mapping:
        status = mapping[raw]
    elif "Пользователь" in raw or "не определ" in raw.lower():
        status = "session_expired"
    else:
        status = "unknown"
    return {
        "subject": name,
        "guid": guid,
        "answer": answer,
        "raw_response": raw,
        "status": status,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
