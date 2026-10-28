from __future__ import annotations

from .db import connect
from .stzy_api import StzyApi, html_text


def enrich_answers(conn, limit: int = 20, delay: float = 1.2) -> int:
    api = StzyApi(delay=delay)
    rows = conn.execute("SELECT id FROM questions WHERE status='draft' AND id LIKE 'stzy-%' ORDER BY id LIMIT ?", (limit,)).fetchall()
    n = 0
    for (qid,) in rows:
        try:
            data = api.answer(qid.replace('stzy-', '', 1))
            answer = html_text(str((data or {}).get('answer') or ''))
            explains = html_text(str((data or {}).get('explains') or ''))
            if not answer and not explains:
                continue
            conn.execute("UPDATE questions SET answer=?, explanation=?, status='published' WHERE id=?", (answer, explains, qid))
            n += 1
            print('answer', qid, answer[:40], flush=True)
        except Exception as e:
            print('ERR', qid, str(e)[:120], flush=True)
    conn.commit()
    return n
