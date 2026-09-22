from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag

from .mathml import mathml_to_latex


@dataclass
class Task:
    qid: str
    guid: str
    condition_html: str
    condition_text: str
    condition_latex: str
    answer_type: str | None = None
    kes: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _flatten(node: Tag) -> tuple[str, str]:
    text_parts: list[str] = []
    latex_parts: list[str] = []

    def walk(n: Tag | NavigableString) -> None:
        if isinstance(n, NavigableString):
            text_parts.append(str(n))
            latex_parts.append(str(n))
            return
        if not isinstance(n, Tag):
            return
        if n.name and n.name.rsplit(":", 1)[-1].lower() == "math":
            latex = mathml_to_latex(n)
            text_parts.append(f" [{latex}] ")
            latex_parts.append(f" ${latex}$ ")
            return
        for child in n.children:
            walk(child)

    walk(node)
    text = " ".join("".join(text_parts).split())
    latex = " ".join("".join(latex_parts).split())
    return text, latex


def parse_kes_topics(html: str) -> list[dict[str, Any]]:
    """Дерево КЭС со страницы предмета: разделы верхнего уровня + подтемы.

    Возвращает: [{"code": "1", "name": "...", "children": [{"code": "1.1", ...}]}].
    """
    soup = BeautifulSoup(html, "lxml")
    sections: dict[str, dict[str, Any]] = {}

    for section_label in soup.select("div.filter-title + div label"):
        checkbox = section_label.find("input", attrs={"name": "theme"})
        if not isinstance(checkbox, Tag):
            continue
        code = str(checkbox.get("value", "")).strip()
        if not code or "." in code:
            continue
        name = section_label.get_text(" ", strip=True)
        sections.setdefault(code, {"code": code, "name": name, "children": []})

    for item in soup.select("ul.dropdown-menu li.dropdown-item"):
        checkbox = item.find("input", attrs={"name": "theme"})
        if not isinstance(checkbox, Tag):
            continue
        code = str(checkbox.get("value", "")).strip()
        if not code or "." not in code:
            continue
        name = item.get_text(" ", strip=True)
        parent = code.split(".", 1)[0]
        section = sections.setdefault(parent, {"code": parent, "name": "", "children": []})
        section["children"].append({"code": code, "name": name})

    return sorted(
        sections.values(),
        key=lambda s: int(s["code"]) if s["code"].isdigit() else 0,
    )


def parse_tasks(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    tasks: list[dict[str, Any]] = []

    for qblock in soup.select("div.qblock"):
        block_id = qblock.get("id", "")
        if not isinstance(block_id, str) or not block_id.startswith("q"):
            continue
        qid = block_id[1:]

        guid_input = qblock.find("input", attrs={"name": "guid"})
        guid = ""
        if isinstance(guid_input, Tag):
            guid = str(guid_input.get("value", ""))

        cond_td = qblock.find("td", class_="cell_0")
        condition_html = cond_td.decode_contents() if isinstance(cond_td, Tag) else ""
        if isinstance(cond_td, Tag):
            condition_text, condition_latex = _flatten(cond_td)
            images = [
                str(img.get("src", "")) for img in cond_td.find_all("img") if isinstance(img, Tag)
            ]
        else:
            condition_text = ""
            condition_latex = ""
            images = []

        answer_type: str | None = None
        kes: list[str] = []
        info_block = soup.find("div", id=f"i{qid}")
        if isinstance(info_block, Tag):
            for row in info_block.select("table tr"):
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                name = cells[0].get_text(strip=True).rstrip(":").lower()
                value = cells[1].get_text(" ", strip=True)
                if "тип ответа" in name:
                    answer_type = value
                elif "кэс" in name:
                    kes.append(value)

        tasks.append(
            Task(
                qid=qid,
                guid=guid,
                condition_html=condition_html,
                condition_text=condition_text,
                condition_latex=condition_latex,
                answer_type=answer_type,
                kes=kes,
                images=images,
            ).to_dict()
        )

    return tasks
