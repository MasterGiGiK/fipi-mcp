# fipi-mcp

[![smoke](https://github.com/MasterGiGiK/fipi-mcp/actions/workflows/smoke.yml/badge.svg)](https://github.com/MasterGiGiK/fipi-mcp/actions/workflows/smoke.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/protocol-MCP-8A2BE2)](https://modelcontextprotocol.io/)

MCP-сервер для открытого банка заданий ФИПИ (ЕГЭ и ОГЭ) —
`https://ege.fipi.ru/bank/` и `https://oge.fipi.ru/bank/`.

Даёт LLM/агенту структурированный доступ к заданиям **16 предметов ЕГЭ** и
**14 предметов ОГЭ**: список с фильтрами по темам кодификатора, условие с
MathML → LaTeX, метаданные (КЭС, тип ответа) и проверку ответа.

## Что можно попросить у модели

- «Дай 5 задач по профильной математике по теме `2.4` (показательные и логарифмические уравнения).»
- «Покажи темы кодификатора по физике из fipi-bank.»
- «Найди в fipi-bank задачи со словом `треугольник` по профильной математике.»
- «Дай 3 задачи ОГЭ по физике по разделу `1` (Механика).»
- «Найди задание `40B442` по профильной математике и объясни решение.»
- «Проверь мой ответ `29` на задание с guid `006420F9E9A798DD4FF57BB34671C6AA` по профильной математике.»

## Инструменты (MCP tools)

| Tool | Что делает |
|------|------------|
| `list_subjects(exam='ege')` | Все предметы. `'ege'` — 16 предметов ЕГЭ, `'oge'` — 14 предметов ОГЭ. |
| `list_kes_topics(subject, exam='ege')` | Дерево кодификатора: разделы 1..N + подтемы. Код темы (`2.4`) идёт в `themes` ниже. |
| `list_tasks(subject, exam='ege', page=0, pagesize=10, themes=[], answer_types=[], task_id=?)` | Задачи с фильтрами. `themes=['2.4']` — тема КЭС; `answer_types=['short'\|'full'\|'select_one']` — тип ответа. |
| `search_tasks(subject, query, exam='ege', themes=[], max_pages=10)` | Клиентский полнотекстовый поиск в тексте условия. Серверного у ФИПИ нет. Дорого — сужай через `themes`. |
| `get_task(subject, qid, exam='ege')` | Ищет конкретное задание по короткому qid (`40B442`), перебирая страницы. |
| `check_answer(subject, guid, answer, exam='ege')` | POST на `solve.php`. Клиент сам прогревает сессию. Возвращает `correct` / `wrong` / `not_found`. |

`subject` принимает три формата: ключ (`physics`), русское название (`Физика`)
или полный `proj_guid`. `exam` — `'ege'` (по умолчанию) или `'oge'`.

## С какими клиентами / нейронками работает

MCP — открытый протокол, к нашему серверу подключается любой MCP-совместимый
клиент. Модель под капотом клиент выбирает сам (Claude, GPT-4/5, Gemini,
локальная Llama через Ollama и т. д. — MCP-инструменты подаются им как обычные
function calls).

Работает из коробки: **Claude Desktop, Claude Code, Cursor, Windsurf, Zed,
Continue.dev, Cline / Roo Code, LibreChat, OpenWebUI, Goose**. Для ChatGPT
и Gemini напрямую нельзя — нужен bridge (напр. `mcp-openai-bridge`).

> ⚠️ Сервер должен запускаться на машине, которая физически видит
> `ege.fipi.ru` / `oge.fipi.ru`. Из США/Европы сайт часто недоступен.

## Установка

Нужен **Python 3.10+**. Три шага — склонировать, создать venv, поставить.

```bash
git clone https://github.com/MasterGiGiK/fipi-mcp.git
cd fipi-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

Запомни абсолютный путь до venv-питона — он нужен для конфигов ниже:

```bash
echo "$(pwd)/.venv/bin/python"
```

(На Windows это `.venv\Scripts\python.exe`.)

## Подключение

Ниже подставь свой путь вместо `<PYTHON>` — то, что вывела команда выше.

### Claude Desktop

**Settings → Developer → Edit Config** (это откроет `claude_desktop_config.json`).
Добавь блок `mcpServers` на верхний уровень:

```json
{
  "mcpServers": {
    "fipi-bank": {
      "command": "<PYTHON>",
      "args": ["-m", "fipi_mcp"]
    }
  }
}
```

Сохрани, полностью закрой Claude (`Cmd+Q`, не крестик) и открой заново.
У поля ввода появится иконка инструментов — там будет `fipi-bank`.

### Claude Code

```bash
claude mcp add fipi-bank --scope user -- <PYTHON> -m fipi_mcp
```

Проверка: `claude mcp list` или `/mcp` внутри чата.

### Cursor

**Settings → MCP → Add new MCP server**. Формат такой же, как у Claude Desktop:

```json
{
  "mcpServers": {
    "fipi-bank": {
      "command": "<PYTHON>",
      "args": ["-m", "fipi_mcp"]
    }
  }
}
```

Файл лежит в `~/.cursor/mcp.json` (глобально) или `.cursor/mcp.json` в корне
проекта (локально).

### Windsurf / Zed / Continue.dev / другие

Формат конфигурации у всех одинаковый (`command` + `args`), меняется только
путь к файлу настроек. Загляни в документацию своего клиента по разделу
«MCP» — вставь тот же блок `mcpServers`.

## Проверка, что всё работает

Без MCP, локально:

```bash
.venv/bin/python -m examples.smoke_test
```

Должен напечатать 2 задачи по профильной математике и `[OK]` по всем
пунктам, включая проверку ответа `29` через `check_answer`. Если работает —
и MCP-подключение заведётся.

Внутри клиента после подключения задай простой промпт: «Через fipi-bank
покажи 3 задания по профильной математике». Модель дёрнет `list_tasks` и
вернёт задачи с формулами в LaTeX.

## Как это устроено

- `fipi_mcp/client.py` — httpx-клиент с `verify=False` (у ege.fipi.ru свой
  CA), декодированием cp1251, сессионными куками и прогревом PHPSESSID
  перед `solve.php`.
- `fipi_mcp/parser.py` — BeautifulSoup + lxml. Ищет `div.qblock` (условие),
  `div#i<qid>` (метаданные), `ul.dropdown-menu` (дерево КЭС).
- `fipi_mcp/mathml.py` — мини-компилятор MathML → LaTeX для читаемости формул.
- `fipi_mcp/subjects.py` — реестр предметов ЕГЭ и ОГЭ с их `proj_guid`.
- `fipi_mcp/server.py` — MCP-обвязка тулов на официальном Python SDK.

## Ограничения

- Задания копирайт ФИПИ. Массовая выкачка не приветствуется — используй для
  подготовки к экзамену или разработки.
- Нет пагинации-cursor: серверу передаётся `page` и `pagesize`. `get_task`
  делает линейный перебор — дорого при глубоком поиске.
- MathML → LaTeX покрывает основные примитивы, а не 100% спецификации.
- `search_tasks` ищет только в тексте условия, не внутри формул MathML.
- `check_answer` работает только для заданий с автоматической проверкой
  (краткий/числовой ответ). Развёрнутые ответы ФИПИ не проверяет.

## Лицензия

MIT — см. [LICENSE](LICENSE).
