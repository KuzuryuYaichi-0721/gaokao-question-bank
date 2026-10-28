from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


def load_har(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("log", {}).get("entries", [])
    out = []
    for e in entries:
        req = e.get("request", {})
        url = req.get("url", "")
        if "stzy.com" not in urlparse(url).netloc:
            continue
        headers = {h.get("name", ""): h.get("value", "") for h in req.get("headers", [])}
        headers.pop("Authorization", None)
        headers.pop("Cookie", None)
        resp = e.get("response", {})
        content = resp.get("content", {})
        text = content.get("text", "")
        out.append({
            "method": req.get("method"), "url": url,
            "path": urlparse(url).path,
            "query": urlparse(url).query,
            "request_headers": headers,
            "request_body": req.get("postData", {}).get("text", ""),
            "status": resp.get("status"),
            "mime": content.get("mimeType", ""),
            "response_text": text,
        })
    return out


def write_responses(path: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for i, e in enumerate(load_har(path), 1):
        if not e["response_text"]:
            continue
        ext = ".json" if "json" in e["mime"] else ".html"
        (out_dir / f"stzy-{i:03d}{ext}").write_text(e["response_text"], encoding="utf-8")
        n += 1
    return n
