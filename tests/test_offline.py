"""Оффлайн-тест парсера на сохранённой странице ФИПИ.

Не требует сети — годится для CI из-под GitHub Actions runners, которые
до ege.fipi.ru не достучаться (гео-блок).
"""
from __future__ import annotations

import sys
from pathlib import Path

from fipi_mcp.mathml import mathml_to_latex
from fipi_mcp.parser import parse_tasks
from fipi_mcp.subjects import SUBJECTS_EGE, resolve

FIXTURE = Path(__file__).parent / "fixtures" / "questions_math_prof.html"


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
