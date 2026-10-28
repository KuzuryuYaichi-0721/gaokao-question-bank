from __future__ import annotations

import json, os
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        path = Path(__file__).resolve().parent.parent / "config.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def token_for(cfg: dict[str, Any]) -> str:
    env_name = cfg.get("source", {}).get("token_env", "STZY_TOKEN")
    token = os.environ.get(env_name, "").strip() or str(cfg.get("source", {}).get("token", "")).strip()
    if not token:
        raise RuntimeError(f"缺少 {env_name} 或 source.token。请在本机环境变量或 config.local.json 中配置，不要把 token 提交到 Git。")
    return token
