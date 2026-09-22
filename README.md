# fipi-mcp

[![smoke](https://github.com/MasterGiGiK/fipi-mcp/actions/workflows/smoke.yml/badge.svg)](https://github.com/MasterGiGiK/fipi-mcp/actions/workflows/smoke.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/protocol-MCP-8A2BE2)](https://modelcontextprotocol.io/)

MCP-сервер для открытого банка заданий ФИПИ (ЕГЭ) — `https://ege.fipi.ru/bank/`.

Даёт LLM/агенту структурированный доступ к заданиям 16 предметов ЕГЭ: список,
условие с MathML → LaTeX, метаданные (КЭС, тип ответа) и проверку ответа.

## Инструменты (MCP tools)

| Tool | Что делает |
|------|------------|
| `list_subjects` | Возвращает 16 предметов с ключами и `proj_guid`. |
| `list_tasks(subject, page=0, pagesize=10, themes=[], answer_types=[], task_id=?)` | Задачи страницы с фильтрами. `themes=['2.4']` — тема КЭС; `answer_types=['short'\|'full'\|'select_one']` — тип ответа. |
| `list_kes_topics(subject)` | Дерево кодификатора: разделы 1..N + подтемы. `code` подходит для `themes` фильтра выше. |
| `get_task(subject, qid)` | Ищет конкретное задание по короткому qid, перебирая страницы. |
| `check_answer(subject, guid, answer)` | POST на `solve.php`. Клиент сам прогревает сессию. Возвращает `correct` / `wrong` / `not_found`. |

`subject` принимает три формата: ключ (`physics`), русское название (`Физика`)
или полный `proj_guid`.

## Установка

Нужен Python 3.10+. С `uv` (рекомендую):

```bash
cd "/Users/niccolovasioni/Desktop/Папка и мамка вайбкодинга/фипи"
uv venv
uv pip install -e .
```

Или классический pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Проверка без MCP

```bash
python -m examples.smoke_test
```

Должен напечатать 2 задачи по математике профильной. Если видишь текст условия
и LaTeX-фрагменты — всё работает.

## Подключение к Claude Desktop

Открой `~/Library/Application Support/Claude/claude_desktop_config.json` и
добавь сервер (замени путь на свой абсолютный):

```json
{
  "mcpServers": {
    "fipi-bank": {
      "command": "/Users/niccolovasioni/Desktop/Папка и мамка вайбкодинга/фипи/.venv/bin/python",
      "args": ["-m", "fipi_mcp"]
    }
  }
}
```

Перезапусти Claude Desktop → в меню инструментов появится `fipi-bank`.

## Подключение к Claude Code

```bash
claude mcp add fipi-bank \
  --command "/Users/niccolovasioni/Desktop/Папка и мамка вайбкодинга/фипи/.venv/bin/python" \
  --args "-m" "fipi_mcp"
```

## Примеры промптов

- «Покажи список тем кодификатора по физике из fipi-bank.»
- «Дай 5 задач по профильной математике по теме `2.4` (показательные и логарифмические уравнения).»
- «Найди в банке ФИПИ задание `40B442` по профильной математике и объясни решение.»
- «Проверь ответ `29` на задание с guid `006420F9E9A798DD4FF57BB34671C6AA` по профильной математике.»

## Как это устроено

- `fipi_mcp/client.py` — httpx-клиент с `verify=False` (у ege.fipi.ru свой CA),
  декодированием cp1251 и сессионными куками.
- `fipi_mcp/parser.py` — BeautifulSoup + lxml. Ищет `div.qblock` (условие) и
  `div#i<qid>` (метаданные).
- `fipi_mcp/mathml.py` — мини-компилятор MathML → LaTeX для читаемости формул.
- `fipi_mcp/server.py` — FastMCP-обвязка тулов.

## Ограничения

- Задания копирайт ФИПИ. Массовая выкачка не приветствуется — используй для
  подготовки к экзамену или разработки.
- Нет пагинации-cursor: серверу передаётся `page` и `pagesize`. `get_task`
  делает линейный перебор — дорого при глубоком поиске.
- MathML → LaTeX покрывает основные примитивы, а не 100% спецификации.
- `check_answer` работает только для заданий с автоматической проверкой
  (краткий/числовой ответ). Для развёрнутых ответов ФИПИ не проверяет.
