from __future__ import annotations

import argparse, json, sys
from pathlib import Path

from .classify import parse_query
from .har import load_har, write_responses
from .db import init_db, connect, import_questions
from .retrieval import search, stats
from .settings import load_config

ROOT = Path(__file__).resolve().parent.parent


def _db(cfg):
    p = Path(cfg.get("database", "data/questions.db"))
    if not p.is_absolute(): p = ROOT / p
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gaokao-bank")
    ap.add_argument("--config", default="config.local.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    imp = sub.add_parser("import-json"); imp.add_argument("path")
    sr = sub.add_parser("search"); sr.add_argument("--subject"); sr.add_argument("--region"); sr.add_argument("--exam-era"); sr.add_argument("--year-from", type=int); sr.add_argument("--year-to", type=int); sr.add_argument("--type"); sr.add_argument("--q-no", type=int); sr.add_argument("--keyword"); sr.add_argument("--limit", type=int, default=50)
    ai = sub.add_parser("ai-search"); ai.add_argument("query"); ai.add_argument("--limit", type=int, default=50)
    sub.add_parser("stats")
    hi = sub.add_parser("har-inspect"); hi.add_argument("path"); hi.add_argument("--out", default="raw/har")
    he = sub.add_parser("har-export"); he.add_argument("path"); he.add_argument("--out", default="raw/har")
    ex = sub.add_parser("export-app"); ex.add_argument("--out", default="data/export/questions.json")
    args = ap.parse_args(argv)
    cfg_path = Path(args.config)
    if not cfg_path.is_absolute(): cfg_path = ROOT / cfg_path
    cfg = load_config(cfg_path)
    db = _db(cfg)
    if args.cmd == "init":
        init_db(db, ROOT / "schema.sql"); print(db); return 0
    if args.cmd == "import-json":
        data = json.loads(Path(args.path).read_text(encoding="utf-8"))
        conn = connect(db)
        try: print(import_questions(conn, data if isinstance(data, list) else [data]))
        finally: conn.close()
        return 0
    if args.cmd == "search":
        f = {"subject": args.subject, "region": args.region, "exam_era": args.exam_era, "year_from": args.year_from, "year_to": args.year_to, "q_type": args.type, "q_no": args.q_no, "keyword": args.keyword}
        print(json.dumps(search(str(db), f, args.limit), ensure_ascii=False, indent=2)); return 0
    if args.cmd == "ai-search":
        f = parse_query(args.query, cfg)
        print(json.dumps({"filters": f, "results": search(str(db), f, args.limit)}, ensure_ascii=False, indent=2)); return 0
    if args.cmd == "har-inspect":
        rows = load_har(Path(args.path))
        for r in rows:
            print(json.dumps({k: r[k] for k in ("method","url","path","query","status","mime")}, ensure_ascii=False))
        print(f"# {len(rows)} stzy entries")
        return 0
    if args.cmd == "har-export":
        n = write_responses(Path(args.path), Path(args.out))
        print(f"wrote {n} responses to {args.out}")
        return 0
    if args.cmd == "stats":
        print(json.dumps(stats(str(db)), ensure_ascii=False, indent=2)); return 0
    if args.cmd == "export-app":
        out = Path(args.out)
        if not out.is_absolute(): out = ROOT / out
        rows = search(str(db), {}, 100000)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(out); return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
