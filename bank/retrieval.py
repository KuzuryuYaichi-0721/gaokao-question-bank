from __future__ import annotations

import json, sqlite3
from typing import Any

from .db import connect


def _where(filters: dict[str, Any]) -> tuple[str, list[Any]]:
    clauses = ["q.status='published'"]
    args: list[Any] = []
    for col in ("subject", "region", "exam_era", "exam_type", "section", "q_type"):
        val = filters.get(col)
        if val:
            clauses.append(f"q.{col}=?")
            args.append(val)
    if filters.get("year_from"):
        clauses.append("q.year>=?")
        args.append(int(filters["year_from"]))
    if filters.get("year_to"):
        clauses.append("q.year<=?")
        args.append(int(filters["year_to"]))
    if filters.get("q_no"):
        clauses.append("q.q_no=?")
        args.append(int(filters["q_no"]))
    return " AND ".join(clauses), args


def search(db_path: str, filters: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
    conn = connect(db_path)
    try:
        where, args = _where(filters)
        keyword = str(filters.get("keyword") or "").strip()
        if keyword:
            where += " AND q.id IN (SELECT question_id FROM questions_fts WHERE questions_fts MATCH ?)"
            args.append(keyword)
        sql = f"SELECT q.*, p.title AS paper_title FROM questions q LEFT JOIN papers p ON p.paper_key=q.paper_key WHERE {where} ORDER BY q.year DESC, q.region, q.paper_key, q.q_no LIMIT ?"
        args.append(max(1, min(500, int(limit))))
        rows = conn.execute(sql, args).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["options"] = json.loads(d.pop("options_json") or "[]")
            d["knowledge"] = json.loads(d.pop("knowledge_json") or "[]")
            d["type"] = d.get("q_type") or ""
            d["point"] = d.get("score") or 0
            out.append(d)
        return out
    finally:
        conn.close()


def stats(db_path: str) -> dict[str, Any]:
    conn = connect(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) FROM questions WHERE status='published'").fetchone()[0]
        by_subject = [dict(r) for r in conn.execute("SELECT subject,COUNT(*) n FROM questions WHERE status='published' GROUP BY subject ORDER BY subject")]
        by_type = [dict(r) for r in conn.execute("SELECT subject,region,q_type,COUNT(*) n FROM questions WHERE status='published' GROUP BY subject,region,q_type ORDER BY subject,region,n DESC")]
        return {"total": total, "by_subject": by_subject, "by_type": by_type}
    finally:
        conn.close()
