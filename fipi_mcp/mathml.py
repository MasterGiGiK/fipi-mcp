"""Мини-конвертер MathML → LaTeX для условий задач ФИПИ.

Задача — не полный компилятор, а читаемое приближение, которое LLM/пользователь
поймут. Покрывает основные примитивы, встречающиеся на ege.fipi.ru: mfrac,
msup/msub, msqrt/mroot, mover (стрелка над буквой — вектор), mfenced и т. д.
"""

from __future__ import annotations

from bs4 import BeautifulSoup, NavigableString, Tag

_SYMBOLS: dict[str, str] = {
    "·": r"\cdot",
    "×": r"\times",
    "÷": r"\div",
    "→": r"\to",
    "←": r"\leftarrow",
    "↔": r"\leftrightarrow",
    "≤": r"\le",
    "≥": r"\ge",
    "≠": r"\ne",
    "≈": r"\approx",
    "−": "-",
    "±": r"\pm",
    "∓": r"\mp",
    "∑": r"\sum",
    "∏": r"\prod",
    "∫": r"\int",
    "∞": r"\infty",
    "∀": r"\forall",
    "∃": r"\exists",
    "∈": r"\in",
    "∉": r"\notin",
    "∩": r"\cap",
    "∪": r"\cup",
    "∅": r"\emptyset",
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "ε": r"\varepsilon",
    "θ": r"\theta",
    "λ": r"\lambda",
    "μ": r"\mu",
    "π": r"\pi",
    "ρ": r"\rho",
    "σ": r"\sigma",
    "φ": r"\varphi",
    "ψ": r"\psi",
    "ω": r"\omega",
    "Δ": r"\Delta",
    "Σ": r"\Sigma",
    "Ω": r"\Omega",
    " ": " ",
    " ": " ",
    " ": " ",
    "⁡": "",
    "⁢": "",
    "⁣": "",
}


def _tex_text(text: str) -> str:
    return "".join(_SYMBOLS.get(ch, ch) for ch in text)


def _local(name: str | None) -> str:
    if not name:
        return ""
    return name.rsplit(":", 1)[-1].lower()


def _kids(node: Tag) -> list[Tag]:
    result: list[Tag] = []
    for child in node.children:
        if isinstance(child, Tag):
            result.append(child)
        elif isinstance(child, NavigableString) and str(child).strip():
            result.append(child)  # type: ignore[arg-type]
    return result


def _content(node: Tag | NavigableString | None) -> str:
    if node is None:
        return ""
    if isinstance(node, NavigableString):
        return _tex_text(str(node))
    return _convert(node)


def _convert(node: Tag) -> str:
    tag = _local(node.name)
    kids = _kids(node)

    if tag in {"math", "mrow", "mstyle", "semantics", "mpadded"}:
        return "".join(_content(c) for c in kids)

    if tag in {"mn", "mi", "mtext", "mo"}:
        return _tex_text(node.get_text())

    if tag == "mspace":
        return " "

    if tag == "annotation":
        return ""

    if tag == "mfrac" and len(kids) >= 2:
        return f"\\frac{{{_content(kids[0])}}}{{{_content(kids[1])}}}"

    if tag == "msqrt":
        inner = "".join(_content(c) for c in kids)
        return f"\\sqrt{{{inner}}}"

    if tag == "mroot" and len(kids) >= 2:
        return f"\\sqrt[{_content(kids[1])}]{{{_content(kids[0])}}}"

    if tag == "msup" and len(kids) >= 2:
        return f"{{{_content(kids[0])}}}^{{{_content(kids[1])}}}"

    if tag == "msub" and len(kids) >= 2:
        return f"{{{_content(kids[0])}}}_{{{_content(kids[1])}}}"

    if tag == "msubsup" and len(kids) >= 3:
        return (
            f"{{{_content(kids[0])}}}"
            f"_{{{_content(kids[1])}}}"
            f"^{{{_content(kids[2])}}}"
        )

    if tag == "mover" and len(kids) >= 2:
        base = _content(kids[0])
        acc = _content(kids[1]).strip()
        if acc in (r"\to", "→"):
            return f"\\vec{{{base}}}"
        if acc == "-":
            return f"\\overline{{{base}}}"
        if acc in ("^", r"\hat"):
            return f"\\hat{{{base}}}"
        return f"\\overset{{{acc}}}{{{base}}}"

    if tag == "munder" and len(kids) >= 2:
        return f"\\underset{{{_content(kids[1])}}}{{{_content(kids[0])}}}"

    if tag == "munderover" and len(kids) >= 3:
        return (
            f"\\underset{{{_content(kids[1])}}}"
            f"{{\\overset{{{_content(kids[2])}}}{{{_content(kids[0])}}}}}"
        )

    if tag == "mfenced":
        open_ = node.get("open", "(")
        close_ = node.get("close", ")")
        sep = node.get("separators", ",")
        parts = [_content(c) for c in kids]
        if len(parts) <= 1:
            joined = "".join(parts)
        else:
            joined = sep.join(parts) if sep else "".join(parts)
        return f"{open_}{joined}{close_}"

    return "".join(_content(c) for c in kids)


def mathml_to_latex(node: Tag | str) -> str:
    if isinstance(node, str):
        node = BeautifulSoup(node, "lxml-xml")
    if isinstance(node, Tag):
        return " ".join(_convert(node).split())
    return ""
