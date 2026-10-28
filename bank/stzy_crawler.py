from __future__ import annotations

import json, time
from pathlib import Path
from typing import Any

from .db import connect, import_questions
from .stzy_api import StzyApi, parse_question


def crawl(conn, raw_dir: Path, subject: str, year: int, province: str, max_pages: int = 1, keyword: str = "", delay: float = 1.2) -> dict:
    api = StzyApi(delay=delay)
    raw_dir.mkdir(parents=True, exist_ok=True)
    total_new = 0
    pages = 0
    total = 0
    for page in range(1, max_pages + 1):
        data = api.search(subject, year, province, page, keyword)
        total = int(data.get("total") or 0)
        rows = data.get("list") or []
        if not rows: break
        pages += 1
        (raw_dir / f"{subject}-{year}-{province}-{page}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        qs = [parse_question(it, subject, year, province) for it in rows]
        qs = [q for q in qs if q]
        total_new += import_questions(conn, qs)
        print(f"{subject} {year} {province} page {page}/{min(max_pages, (total + 9)//10)}: +{len(qs)}", flush=True)
    return {"pages": pages, "new": total_new, "total": total}
