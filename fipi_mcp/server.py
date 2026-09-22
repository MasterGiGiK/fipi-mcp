from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from .client import FipiClient
from .parser import parse_kes_topics, parse_tasks
from .subjects import SUBJECTS_EGE, resolve

mcp = MCPServer("fipi-bank")

_ANSWER_TYPES = {
    "short": "ILI_STD_SHORT",
    "full": "ILI_STD_FULL",
    "select_one": "ILI_STD_SELECTONE",
}


@mcp.tool()
def list_subjects() -> list[dict[str, str]]:
    """Список предметов ЕГЭ, доступных в открытом банке ФИПИ."""
    return [
        {"key": key, "name": name, "proj_guid": guid}
        for key, (name, guid) in SUBJECTS_EGE.items()
    ]


@mcp.tool()
def list_tasks(
    subject: str,
    page: int = 0,
    pagesize: int = 10,
    themes: list[str] | None = None,
    answer_types: list[str] | None = None,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Список заданий по предмету с опциональными фильтрами.

    subject — ключ ('physics'), русское название или proj-GUID.
    page — номер страницы с нуля.
    pagesize — размер страницы (обычно 10 или 20).
    themes — коды КЭС из list_kes_topics: ['2.4'] или ['1', '2.4'] (раздел или подтема).
    answer_types — типы ответа: 'short' | 'full' | 'select_one' (или сырые коды ILI_STD_*).
    task_id — фильтр по короткому 6-hex qid ('40B442').
    """
    name, guid = resolve(subject)
    filters: dict[str, Any] = {}
    if themes:
        filters["theme"] = list(themes)
    if answer_types:
        filters["qkind"] = [_ANSWER_TYPES.get(t.lower(), t) for t in answer_types]
    if task_id:
        filters["qid"] = task_id

    with FipiClient() as client:
        if filters:
            filters["search"] = "1"
            html = client.filter_questions(guid, filters, page=page, pagesize=pagesize)
        else:
            html = client.questions(guid, page=page, pagesize=pagesize)

    return {
        "subject": name,
        "proj_guid": guid,
        "page": page,
        "pagesize": pagesize,
        "filters": {k: v for k, v in filters.items() if k != "search"} or None,
        "tasks": parse_tasks(html),
    }


@mcp.tool()
def list_kes_topics(subject: str) -> dict[str, Any]:
    """Дерево кодификатора элементов содержания (КЭС) для предмета.

    Возвращает разделы верхнего уровня и подтемы с их кодами. Полученный
    `code` (например '2.4') передавай в list_tasks(themes=[...]) для фильтра.
    """
    name, guid = resolve(subject)
    with FipiClient() as client:
        html = client.project_page(guid)
    return {"subject": name, "proj_guid": guid, "topics": parse_kes_topics(html)}


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
