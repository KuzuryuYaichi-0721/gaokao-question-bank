from __future__ import annotations

import json, os
from typing import Any

import requests

LOCAL_TYPES = {
    "数学": [("导数", ["导数", "单调", "极值", "切线"]), ("圆锥曲线", ["椭圆", "双曲线", "抛物线"]), ("数列", ["数列", "等差", "等比"])],
    "物理": [("力学", ["受力", "牛顿", "运动"]), ("电磁学", ["电场", "磁场", "电路"])],
    "化学": [("实验", ["实验", "装置", "操作"]), ("有机", ["有机", "官能团", "同分异构"])],
    "语文": [("古代诗歌", ["诗歌", "意象", "赏析"]), ("文言文", ["文言", "实词", "翻译"])],
    "英语": [("阅读理解", ["reading", "passage", "author"]), ("完形填空", ["cloze", "blank"]), ("语法填空", ["grammar", "fill"])],
}


def parse_query(query: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """Use one DeepSeek key to turn natural language into local filters. Never generate questions."""
    key = os.environ.get(cfg.get("classify", {}).get("api_key_env", "DEEPSEEK_API_KEY"), "").strip()
    if not key:
        return local_parse(query)
    system = (
        "你是高考题库检索条件解析器。只输出 JSON，不要生成题目，不要补造答案。"
        "字段：subject,region,exam_era(new/old/unknown),year_from,year_to,q_type,q_no,keywords,confidence。"
        "无法确定的字段用空字符串或 null。"
    )
    body = {
        "model": cfg.get("classify", {}).get("deepseek_model", "deepseek-chat"),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": query}],
        "temperature": 0,
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
    }
    try:
        r = requests.post(
            cfg.get("classify", {}).get("deepseek_base_url", "https://api.deepseek.com").rstrip("/") + "/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json=body, timeout=40,
        )
        r.raise_for_status()
        data = json.loads(r.json()["choices"][0]["message"]["content"])
        return data
    except Exception:
        return local_parse(query)


def local_parse(query: str) -> dict[str, Any]:
    result = {"subject": "", "region": "", "exam_era": "", "year_from": None, "year_to": None, "q_type": "", "q_no": None, "keywords": query, "confidence": 0.2}
    for subject, types in LOCAL_TYPES.items():
        if subject in query:
            result["subject"] = subject
            for name, words in types:
                if any(w in query for w in words):
                    result["q_type"] = name
                    break
    if "新高考前" in query or "旧高考" in query:
        result["exam_era"] = "old"
    elif "新高考" in query:
        result["exam_era"] = "new"
    for province in ["北京", "河南", "山东", "广东", "河北", "湖南", "湖北", "四川", "浙江", "江苏", "上海", "天津", "重庆"]:
        if province in query:
            result["region"] = province
            break
    import re
    m = re.search(r"第\s*(\d{1,3})\s*题", query)
    if m:
        result["q_no"] = int(m.group(1))
    y = re.search(r"(20\d{2})", query)
    if y:
        result["year_from"] = int(y.group(1)); result["year_to"] = int(y.group(1))
    return result
