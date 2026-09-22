"""Оффлайн-тест парсера на сохранённой странице ФИПИ.

Не требует сети — годится для CI из-под GitHub Actions runners, которые
до ege.fipi.ru не достучаться (гео-блок).
"""
from __future__ import annotations

import sys
from pathlib import Path

from fipi_mcp.mathml import mathml_to_latex
from fipi_mcp.parser import parse_kes_topics, parse_tasks
from fipi_mcp.subjects import SUBJECTS_EGE, resolve

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE = FIXTURES / "questions_math_prof.html"
PROJECT_FIXTURE = FIXTURES / "project_math_prof.html"


def _check(cond: bool, msg: str) -> None:
    print(f"  [{'OK' if cond else 'FAIL'}] {msg}")
    if not cond:
        sys.exit(1)


def main() -> None:
    print("Subjects registry:")
    _check(len(SUBJECTS_EGE) == 16, "16 EGE subjects registered")
    _check(resolve("physics")[0] == "Физика", "resolve('physics') → Физика")
    _check(
        resolve("AC437B34557F88EA4115D2F374B0A07B")[0].startswith("Мат"),
        "resolve() accepts proj-GUID",
    )

    print("\nParser against saved fixture:")
    html = FIXTURE.read_text(encoding="utf-8")
    tasks = parse_tasks(html)
    _check(len(tasks) >= 5, f"parsed >= 5 tasks (got {len(tasks)})")

    task_40b442 = next((t for t in tasks if t["qid"] == "40B442"), None)
    _check(task_40b442 is not None, "found task 40B442 in fixture")
    assert task_40b442 is not None
    _check(
        task_40b442["guid"] == "006420F9E9A798DD4FF57BB34671C6AA",
        "40B442 guid matches",
    )
    _check("вектор" in task_40b442["condition_text"].lower(), "condition contains 'вектор'")
    _check(r"\vec{a}" in task_40b442["condition_latex"], "MathML → LaTeX vector rendered")

    print("\nKES topics from project page:")
    topics = parse_kes_topics(PROJECT_FIXTURE.read_text(encoding="utf-8"))
    _check(len(topics) == 7, f"7 top-level sections (got {len(topics)})")
    codes = {s["code"] for s in topics}
    _check(codes == {"1", "2", "3", "4", "5", "6", "7"}, "section codes 1..7")
    section_2 = next(s for s in topics if s["code"] == "2")
    subcodes = {c["code"] for c in section_2["children"]}
    _check("2.4" in subcodes, "subtopic 2.4 present under section 2")
    sub_2_4 = next(c for c in section_2["children"] if c["code"] == "2.4")
    _check(
        "Показательные" in sub_2_4["name"],
        "subtopic 2.4 has expected name",
    )

    print("\nMathML → LaTeX unit checks:")
    _check(mathml_to_latex("<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>") == r"\frac{1}{2}", "mfrac")
    _check(mathml_to_latex("<math><msqrt><mn>9</mn></msqrt></math>") == r"\sqrt{9}", "msqrt")
    _check(
        mathml_to_latex("<math><msup><mi>x</mi><mn>2</mn></msup></math>") == "{x}^{2}",
        "msup",
    )

    print("\nAll offline checks passed.")


if __name__ == "__main__":
    main()
