from __future__ import annotations

import hashlib, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def connect(db_path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: Path, schema_path: Path) -> None:
    conn = connect(db_path)
    try:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def _hash(q: dict[str, Any]) -> str:
    raw = json.dumps([q.get("stem", ""), q.get("options", [])], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def import_questions(conn: sqlite3.Connection, rows: list[dict[str, Any]], defaults: dict[str, Any] | None = None) -> int:
    defaults = defaults or {}
    now = datetime.now(timezone.utc).isoformat()
    n = 0
    for q in rows:
        q = dict(q)
        for k, v in defaults.items():
            q.setdefault(k, v)
        if not q.get("subject") or not q.get("stem"):
            continue
        paper_key = q.get("paper_key") or f"import-{q.get('subject')}-{q.get('year', 0)}-{q.get('region', '')}"
        conn.execute(
            """INSERT INTO papers(paper_key,title,subject,region,exam_era,year,month,exam_type,source_site,source_url,local_file,status,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(paper_key) DO UPDATE SET
                 title=excluded.title, subject=excluded.subject, region=excluded.region,
                 exam_era=excluded.exam_era, year=excluded.year, month=excluded.month,
                 exam_type=excluded.exam_type, source_url=excluded.source_url, status=excluded.status""",
            (
                paper_key, q.get("paper_title") or q.get("title") or paper_key, q["subject"],
                q.get("region", ""), q.get("exam_era", "unknown"), int(q.get("year") or 0),
                int(q.get("month") or 0), q.get("exam_type", ""), q.get("source_site", ""),
                q.get("source_url", ""), q.get("local_file", ""), q.get("status", "published"), now,
            ),
        )
        qid = q.get("id") or hashlib.sha1(f"{paper_key}|{q.get('q_no')}|{q.get('stem')}".encode()).hexdigest()[:24]
        opts = q.get("options", [])
        conn.execute(
            """INSERT INTO questions(id,paper_key,subject,region,exam_era,year,month,exam_type,section,q_no,q_type,stem,options_json,answer,explanation,score,knowledge_json,source_url,content_hash,status,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 stem=excluded.stem, options_json=excluded.options_json, answer=excluded.answer,
                 explanation=excluded.explanation, q_type=excluded.q_type, knowledge_json=excluded.knowledge_json,
                 source_url=excluded.source_url, status=excluded.status""",
            (
                qid, paper_key, q["subject"], q.get("region", ""), q.get("exam_era", "unknown"),
                int(q.get("year") or 0), int(q.get("month") or 0), q.get("exam_type", ""),
                q.get("section", ""), int(q.get("q_no") or 0), q.get("q_type") or q.get("type", ""),
                q["stem"], json.dumps(opts, ensure_ascii=False), q.get("answer", ""),
                q.get("explanation", ""), float(q.get("score") or q.get("point") or 0),
                json.dumps(q.get("knowledge", []), ensure_ascii=False), q.get("source_url", ""),
                q.get("hash") or _hash(q), q.get("status", "published"), now,
            ),
        )
        conn.execute("DELETE FROM questions_fts WHERE question_id=?", (qid,))
        text = " ".join([q["stem"], " ".join(str(o.get("text", "")) for o in opts), q.get("explanation", "")])
        conn.execute("INSERT INTO questions_fts(question_id,stem,options_text,explanation) VALUES(?,?,?,?)",
                     (qid, q["stem"], " ".join(str(o.get("text", "")) for o in opts), q.get("explanation", "")))
        conn.execute("DELETE FROM question_type_links WHERE question_id=?", (qid,))
        qtype = q.get("q_type") or q.get("type")
        if qtype:
            type_id = f"type:{q['subject']}:{q.get('region','全部')}:{q.get('exam_era','unknown')}:{qtype}"
            conn.execute("INSERT OR IGNORE INTO question_types(id,subject,region,exam_era,name,source) VALUES(?,?,?,?,?,?)",
                         (type_id, q["subject"], q.get("region", ""), q.get("exam_era", "unknown"), qtype, "local"))
            conn.execute("INSERT OR IGNORE INTO question_type_links(question_id,type_id,confidence,method) VALUES(?,?,?,?)",
                         (qid, type_id, 1.0, "source"))
        n += 1
    conn.commit()
    return n
