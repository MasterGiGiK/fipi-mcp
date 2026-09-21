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


def resolve(subject: str) -> tuple[str, str]:
    """Принимает ключ ('physics'), русское название или proj-GUID → (name, guid)."""
    q = subject.strip()
    if q.lower() in SUBJECTS_EGE:
        return SUBJECTS_EGE[q.lower()]
    for name, guid in SUBJECTS_EGE.values():
        if guid.upper() == q.upper():
            return name, guid
    for name, guid in SUBJECTS_EGE.values():
        if name.lower() == q.lower():
            return name, guid
    raise ValueError(
        f"Unknown subject {subject!r}. Use list_subjects() to see valid keys/names."
    )
