SUBJECTS_EGE: dict[str, tuple[str, str]] = {
    "english":     ("Английский язык",                "4B53A6CB75B0B5E1427E596EB4931A2A"),
    "biology":     ("Биология",                       "CA9D848A31849ED149D382C32A7A2BE4"),
    "geography":   ("География",                      "20E79180061DB32845C11FC7BD87C7C8"),
    "informatics": ("Информатика и ИКТ",              "B9ACA5BBB2E19E434CD6BEC25284C67F"),
    "spanish":     ("Испанский язык",                 "8C65A335D93D9DA047C42613F61416F3"),
    "history":     ("История",                        "068A227D253BA6C04D0C832387FD0D89"),
    "chinese":     ("Китайский язык",                 "F6298F3470D898D043E18BC680F60434"),
    "literature":  ("Литература",                     "4F431E63B9C9B25246F00AD7B5253996"),
    "math_base":   ("Математика. Базовый уровень",    "E040A72A1A3DABA14C90C97E0B6EE7DC"),
    "math_prof":   ("Математика. Профильный уровень", "AC437B34557F88EA4115D2F374B0A07B"),
    "german":      ("Немецкий язык",                  "B5963A8D84CF9020461EAE42F37F541F"),
    "social":      ("Обществознание",                 "756DF168F63F9A6341711C61AA5EC578"),
    "russian":     ("Русский язык",                   "AF0ED3F2557F8FFC4C06F80B6803FD26"),
    "physics":     ("Физика",                         "BA1F39653304A5B041B656915DC36B38"),
    "french":      ("Французский язык",               "5BAC840990A3AF0A4EE80D1B5A1F9527"),
    "chemistry":   ("Химия",                          "EA45D8517ABEB35140D0D83E76F14A41"),
}

SUBJECTS_OGE: dict[str, tuple[str, str]] = {
    "english":     ("Английский язык",   "8BBD5C99F37898B6402964AB11955663"),
    "biology":     ("Биология",          "0E1FA4229923A5CE4FC368155127ED90"),
    "geography":   ("География",         "0FA4DA9E3AE2BA1547B75F0B08EF6445"),
    "informatics": ("Информатика",       "74676951F093A0754D74F2D6E7955F06"),
    "spanish":     ("Испанский язык",    "7FF0B02E53DFBCDE4F56B0148BE9A236"),
    "history":     ("История",           "3CBBE97571208D9140697A6C2ABE91A0"),
    "literature":  ("Литература",        "6B2CD4C77304B2A3478E5A5B61F6899A"),
    "math":        ("Математика",        "DE0E276E497AB3784C3FC4CC20248DC0"),
    "german":      ("Немецкий язык",     "A2AC67AE354EBC5242C49482CBC13451"),
    "social":      ("Обществознание",    "AE63AB28A2D28E194A286FA5A8EB9A78"),
    "russian":     ("Русский язык",      "2F5EE3B12FE2A0EA40B06BF61A015416"),
    "physics":     ("Физика",            "B24AFED7DE6AB5BC461219556CCA4F9B"),
    "french":      ("Французский язык",  "2A4C52ED5AC1ADA644B8BBF169FEC0FC"),
    "chemistry":   ("Химия",             "33B3A93C5A6599124B04FB95616C835B"),
}

_REGISTRY: dict[str, dict[str, tuple[str, str]]] = {
    "ege": SUBJECTS_EGE,
    "oge": SUBJECTS_OGE,
}


def registry(exam: str) -> dict[str, tuple[str, str]]:
    key = exam.lower().strip()
    if key not in _REGISTRY:
        raise ValueError(f"Unknown exam {exam!r}: use 'ege' or 'oge'")
    return _REGISTRY[key]


def resolve(subject: str, exam: str = "ege") -> tuple[str, str]:
    """Принимает ключ ('physics'), русское название или proj-GUID → (name, guid).

    `exam` — 'ege' (по умолчанию) или 'oge'.
    """
    reg = registry(exam)
    q = subject.strip()
    if q.lower() in reg:
        return reg[q.lower()]
    for name, guid in reg.values():
        if guid.upper() == q.upper():
            return name, guid
    for name, guid in reg.values():
        if name.lower() == q.lower():
            return name, guid
    raise ValueError(
        f"Unknown {exam.upper()} subject {subject!r}. "
        f"Use list_subjects(exam='{exam}') to see valid keys/names."
    )
