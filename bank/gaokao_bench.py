from __future__ import annotations

import json, re
from pathlib import Path
from urllib.parse import quote

import requests

from .db import import_questions

BASE = "https://raw.githubusercontent.com/OpenLMLab/GAOKAO-Bench/main/Data"
UPD = "https://raw.githubusercontent.com/OpenLMLab/GAOKAO-Bench-Updates/main/Data"

OBJECTIVE = {
    "2010-2013_English_MCQs.json": "英语",
    "2010-2022_Biology_MCQs.json": "生物",
    "2010-2022_Chemistry_MCQs.json": "化学",
    "2010-2022_Chinese_Lang_and_Usage_MCQs.json": "语文",
    "2010-2022_Chinese_Modern_Lit.json": "语文",
    "2010-2022_English_Fill_in_Blanks.json": "英语",
    "2010-2022_English_Reading_Comp.json": "英语",
    "2010-2022_Geography_MCQs.json": "地理",
    "2010-2022_History_MCQs.json": "历史",
    "2010-2022_Math_II_MCQs.json": "数学",
    "2010-2022_Math_I_MCQs.json": "数学",
    "2010-2022_Physics_MCQs.json": "物理",
    "2010-2022_Political_Science_MCQs.json": "政治",
    "2012-2022_English_Cloze_Test.json": "英语",
}
SUBJECTIVE = {
    "2010-2022_Biology_Open-ended_Questions.json": "生物",
    "2010-2022_Chemistry_Open-ended_Questions.json": "化学",
    "2010-2022_Chinese_Language_Ancient_Poetry_Reading.json": "语文",
    "2010-2022_Chinese_Language_Classical_Chinese_Reading.json": "语文",
    "2010-2022_Chinese_Language_Famous_Passages_and_Sentences_Dictation.json": "语文",
    "2010-2022_Chinese_Language_Language_and_Writing_Skills_Open-ended_Questions.json": "语文",
    "2010-2022_Chinese_Language_Literary_Text_Reading.json": "语文",
    "2010-2022_Chinese_Language_Practical_Text_Reading.json": "语文",
    "2010-2022_Geography_Open-ended_Questions.json": "地理",
    "2010-2022_History_Open-ended_Questions.json": "历史",
    "2010-2022_Math_II_Fill-in-the-Blank.json": "数学",
    "2010-2022_Math_II_Open-ended_Questions.json": "数学",
    "2010-2022_Math_I_Fill-in-the-Blank.json": "数学",
    "2010-2022_Math_I_Open-ended_Questions.json": "数学",
    "2010-2022_Physics_Open-ended_Questions.json": "物理",
    "2010-2022_Political_Science_Open-ended_Questions.json": "政治",
    "2012-2022_English_Language_Error_Correction.json": "英语",
    "2014-2022_English_Language_Cloze_Passage.json": "英语",
}
UPDATES = {
    "2023_Biology_MCQs.json": "生物", "2023_Chemistry_MCQs.json": "化学",
    "2023_Chinese_Lang_and_Usage_MCQs.json": "语文", "2023_Chinese_Modern_Lit.json": "语文",
    "2023_English_Cloze_Test.json": "英语", "2023_English_Fill_in_Blanks.json": "英语",
    "2023_English_Reading_Comp.json": "英语", "2023_Geography_MCQs.json": "地理",
    "2023_History_MCQs.json": "历史", "2023_Math_MCQs.json": "数学",
    "2023_Physics_MCQs.json": "物理", "2023_Political_Science_MCQs.json": "政治",
    "2024_Biology_MCQs.json": "生物", "2024_Chemistry_MCQs.json": "化学",
    "2024_Chinese_Lang_and_Usage_MCQs.json": "语文", "2024_Chinese_Modern_Lit.json": "语文",
    "2024_English_Cloze_Test.json": "英语", "2024_English_Fill_in_Blanks.json": "英语",
    "2024_English_Reading_Comp.json": "英语", "2024_Geography_MCQs.json": "地理",
    "2024_History_MCQs.json": "历史", "2024_Math_MCQs.json": "数学",
    "2024_Physics_MCQs.json": "物理", "2024_Political_Science_MCQs.json": "政治",
}

REGION_MAP = [
    ("北京", "北京"), ("上海", "上海"), ("天津", "天津"), ("浙江", "浙江"),
    ("山东", "山东"), ("江苏", "江苏"), ("广东", "广东"), ("河南", "河南"),
    ("全国", "全国"), ("新课标", "全国"), ("新高考", "全国"),
]

TYPE_MAP = [
    ("Reading_Comp", "阅读理解"), ("Cloze", "完形填空"), ("Fill_in_Blanks", "语法填空"),
    ("MCQs", "单项选择题"), ("Modern_Lit", "现代文阅读"), ("Ancient_Poetry", "古代诗歌"),
    ("Classical_Chinese", "文言文阅读"), ("Error_Correction", "改错"),
    ("Open-ended", "主观题"), ("Fill-in-the-Blank", "填空题"), ("Dictation", "默写"),
]


def subject_of(name: str) -> str:
    for d in (OBJECTIVE, SUBJECTIVE, UPDATES):
        if name in d: return d[name]
    return ""


def type_of(name: str) -> str:
    for key, val in TYPE_MAP:
        if key.lower() in name.lower(): return val
    return "未分类"


def region_of(category: str) -> str:
    for key, val in REGION_MAP:
        if key in category: return val
    return "全国"


def parse_options(question: str):
    lines = question.splitlines()
    opts, stem_lines = [], []
    for line in lines:
        m = re.match(r"^\s*([A-D])[.、]\s*(.+?)\s*$", line)
        if m:
            opts.append({"key": m.group(1), "text": m.group(2)})
        else:
            stem_lines.append(line)
    return "\n".join(stem_lines).strip(), opts


def parse_file(path: Path, subject: str = "", source_url: str = "") -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("example", data if isinstance(data, list) else [])
    out = []
    for i, it in enumerate(items):
        year = int(str(it.get("year") or 0)[:4] or 0)
        if year < 2016 or year > 2025:
            continue
        q = str(it.get("question") or "").strip()
        if not q: continue
        stem, options = parse_options(q)
        num = re.match(r"^\s*(\d{1,3})[.、]\s*", stem)
        qno = int(num.group(1)) if num else int(it.get("index") or 0) + 1
        if num: stem = stem[num.end():].strip()
        ans = it.get("answer")
        if isinstance(ans, list): ans = "".join(map(str, ans))
        category = str(it.get("category") or "")
        subj = subject or subject_of(path.name)
        out.append({
            "paper_key": f"bench-{subj}-{year}-{re.sub(r'[^0-9A-Za-z一-龥]+', '-', category).strip('-') or 'national'}",
            "paper_title": f"{year} 高考 {subj} {category}".strip(),
            "subject": subj,
            "region": region_of(category),
            "exam_era": "old" if year <= 2020 else "new",
            "year": year,
            "month": 6,
            "exam_type": category or "高考真题",
            "section": "",
            "q_no": qno,
            "q_type": type_of(path.name),
            "stem": stem,
            "options": options,
            "answer": str(ans or "").strip(),
            "explanation": str(it.get("analysis") or "").strip(),
            "score": float(it.get("score") or 0),
            "source_site": "GAOKAO-Bench",
            "source_url": source_url,
            "status": "published",
        })
    return out


def ensure_files(raw_dir: Path) -> list[tuple[Path, str, str]]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name, subj in OBJECTIVE.items():
        jobs.append((name, subj, BASE + "/Objective_Questions/" + quote(name)))
    for name, subj in SUBJECTIVE.items():
        jobs.append((name, subj, BASE + "/Subjective_Questions/" + quote(name)))
    for name, subj in UPDATES.items():
        folder = "GAOKAO-Bench-" + name[:4]
        jobs.append((name, subj, UPD + "/" + folder + "/" + quote(name)))
    out = []
    for name, subj, url in jobs:
        p = raw_dir / name
        if not p.exists() or p.stat().st_size < 20:
            r = requests.get(url, timeout=60, headers={"User-Agent": "GaokaoQuestionBank/0.1"})
            r.raise_for_status()
            p.write_bytes(r.content)
        out.append((p, subj, url))
    return out


def import_bench(conn, raw_dir: Path, limit: int = 0) -> int:
    total = 0
    for p, subj, url in ensure_files(raw_dir):
        rows = parse_file(p, subj, url)
        if limit: rows = rows[:limit]
        total += import_questions(conn, rows)
    return total
