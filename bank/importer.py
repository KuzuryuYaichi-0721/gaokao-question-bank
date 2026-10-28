from __future__ import annotations

import json, re
from typing import Any

from .har import load_har


def _pick(d: dict, *keys, default=""):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def normalize_record(rec: dict, defaults: dict | None = None) -> dict | None:
    d = dict(rec)
    defaults = defaults or {}
    stem = _pick(d, "stem", "question", "content", "title", "题干")
    if not stem or len(str(stem).strip()) < 4:
        return None
    options = _pick(d, "options", "option_list", "choices", "选项", default=[])
    if isinstance(options, dict):
        options = [{"key": str(k).upper(), "text": str(v)} for k, v in options.items()]
    elif isinstance(options, list):
        opts = []
        for i, o in enumerate(options):
            if isinstance(o, dict):
                opts.append({"key": str(o.get("key") or o.get("label") or chr(65 + i)).upper(), "text": str(o.get("text") or o.get("value") or "")})
            else:
                opts.append({"key": chr(65 + i), "text": str(o)})
        options = opts
    else:
        options = []
    q = {
        "subject": _pick(d, "subject", "学科", default=defaults.get("subject", "")),
        "region": _pick(d, "region", "province", "地区", default=defaults.get("region", "")),
        "exam_era": _pick(d, "exam_era", "era", default=defaults.get("exam_era", "unknown")),
        "year": int(_pick(d, "year", "年份", default=defaults.get("year", 0)) or 0),
        "month": int(_pick(d, "month", default=0) or 0),
        "exam_type": _pick(d, "exam_type", "examType", default=defaults.get("exam_type", "")),
        "section": _pick(d, "section", default=""),
        "q_no": int(_pick(d, "q_no", "qno", "number", "题号", default=0) or 0),
        "q_type": _pick(d, "q_type", "type", "题型", default=""),
        "stem": str(stem).strip(),
        "options": options,
        "answer": str(_pick(d, "answer", "correct", "答案", default="")).strip(),
        "explanation": str(_pick(d, "explanation", "analysis", "解析", default="")).strip(),
        "score": float(_pick(d, "score", "points", "分值", default=0) or 0),
        "source_url": str(_pick(d, "source_url", "url", default=defaults.get("source_url", ""))),
    }
    q["paper_key"] = _pick(d, "paper_key", "paper", "试卷", default=f"stzy-{q['subject']}-{q['year']}-{q['region']}")
    q["paper_title"] = _pick(d, "paper_title", "paper_name", default=q["paper_key"])
    return q


def find_question_dicts(obj: Any) -> list[dict]:
    out = []
    if isinstance(obj, dict):
        stem = _pick(obj, "stem", "question", "content", "title", "题干")
        if stem and len(str(stem).strip()) >= 4 and any(k in obj for k in ("options", "answer", "choices", "选项", "答案")):
            out.append(obj)
        for v in obj.values():
            out.extend(find_question_dicts(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(find_question_dicts(v))
    return out


def import_har(path, conn, defaults: dict | None = None) -> int:
    from .db import import_questions
    rows = []
    for e in load_har(path):
        if "json" not in (e.get("mime") or "") and not e.get("response_text", "").lstrip().startswith(("{", "[")):
            continue
        try:
            data = json.loads(e["response_text"])
        except Exception:
            continue
        for rec in find_question_dicts(data):
            q = normalize_record(rec, {**(defaults or {}), "source_url": e.get("url", "")})
            if q:
                rows.append(q)
    return import_questions(conn, rows)
