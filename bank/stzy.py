from __future__ import annotations

import time
from typing import Any
from urllib.parse import urljoin

import requests

from .settings import token_for


class StzyClient:
    """Bearer-token client. Endpoint paths are configured locally, never committed."""

    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.source = cfg.get("source", {})
        self.base = self.source.get("base_url", "https://stzy.com").rstrip("/")
        self.token = token_for(cfg)
        self.timeout = int(self.source.get("timeout_sec", 30))
        self.delay = float(self.source.get("request_delay_sec", 1.0))
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GaokaoQuestionBank/0.1 (private study archive)",
            "Authorization": self.source.get("token_prefix", "Bearer ") + self.token,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        })

    def get(self, url: str, **kwargs) -> requests.Response:
        if not url.startswith("http"):
            url = urljoin(self.base + "/", url.lstrip("/"))
        time.sleep(self.delay)
        resp = self.session.get(url, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
        return resp

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.get(path, params=params).json()

    def get_text(self, path: str, params: dict[str, Any] | None = None) -> str:
        return self.get(path, params=params).text

    def search(self, params: dict[str, Any]) -> Any:
        path = str(self.source.get("search_path", "")).strip()
        if not path:
            raise RuntimeError(
                "config.local.json 尚未配置 source.search_path。"
                "请先用浏览器登录 stzy，确认搜索接口路径后填入；不要提交 token。"
            )
        return self.get_json(path, params=params)

    def detail(self, path: str) -> Any:
        return self.get_json(path)
