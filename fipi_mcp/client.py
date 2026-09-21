import time
from typing import Any

import httpx

BASE_URL = "https://ege.fipi.ru/bank"


class FipiClient:
    """Тонкая обёртка над PHP-эндпоинтами открытого банка ФИПИ.

    Особенности:
    - страницы отдаются в cp1251;
    - SSL сертификат ege.fipi.ru не валидируется обычными клиентами (Astra Linux CA);
    - PHPSESSID хранится в session между запросами.
    """

    def __init__(self, timeout: float = 20.0) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            verify=False,
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) FipiMCP/0.1"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            },
        )
        self._warmed: set[str] = set()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FipiClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    @staticmethod
    def _decode(resp: httpx.Response) -> str:
        return resp.content.decode("windows-1251", errors="replace")

    def _get(self, path: str, params: dict[str, Any] | None = None) -> str:
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return self._decode(resp)

    def _post(self, path: str, data: dict[str, Any]) -> str:
        resp = self._client.post(path, data=data)
        resp.raise_for_status()
        return self._decode(resp)

    def index(self) -> str:
        return self._get("/index.php")

    def project_page(self, proj: str) -> str:
        return self._get("/index.php", params={"proj": proj})

    def questions(
        self,
        proj: str,
        page: int = 0,
        pagesize: int = 10,
        init_filter_themes: bool = True,
    ) -> str:
        params: dict[str, Any] = {"proj": proj, "page": page, "pagesize": pagesize}
        if init_filter_themes:
            params["init_filter_themes"] = 1
        return self._get("/questions.php", params=params)

    def filter_questions(
        self,
        proj: str,
        filters: dict[str, Any],
        page: int = 0,
        pagesize: int = 10,
    ) -> str:
        data = {
            "proj": proj,
            "page": page,
            "pagesize": pagesize,
            "crtm": str(int(time.time())),
            **filters,
        }
        return self._post("/questions.php", data)

    def warmup(self, proj: str) -> None:
        """Прогреть PHPSESSID: без этого solve.php отвечает "Пользователь не определён"."""
        if proj in self._warmed:
            return
        self.index()
        self.project_page(proj)
        self.questions(proj, page=0, pagesize=5)
        self._warmed.add(proj)

    def solve(self, proj: str, guid: str, answer: str) -> str:
        self.warmup(proj)
        return self._post(
            "/solve.php",
            {
                "proj": proj,
                "guid": guid,
                "answer": answer,
                "chkcode": "",
                "ajax": "1",
            },
        ).strip()
