from __future__ import annotations

TAXONOMY = {
    "语文": ["现代文阅读", "文言文阅读", "古代诗歌", "语言文字运用", "写作"],
    "数学": ["集合与逻辑", "函数", "导数", "数列", "三角函数", "立体几何", "解析几何", "概率统计"],
    "英语": ["阅读理解", "完形填空", "语法填空", "七选五", "应用文写作", "读后续写"],
    "物理": ["力学", "电磁学", "热学", "光学", "实验"],
    "化学": ["无机化学", "有机化学", "化学反应原理", "化学实验"],
    "生物": ["细胞与代谢", "遗传与进化", "稳态与调节", "生态", "实验"],
    "政治": ["经济生活", "政治生活", "文化生活", "哲学", "法律"],
    "历史": ["中国古代史", "中国近代史", "中国现代史", "世界史"],
    "地理": ["自然地理", "人文地理", "区域地理", "地理实践"],
}


def seed(conn, subjects, regions, eras=("new", "old")) -> int:
    n = 0
    for subject in subjects:
        for region in regions:
            for era in eras:
                for name in TAXONOMY.get(subject, []):
                    tid = f"type:{subject}:{region}:{era}:{name}"
                    conn.execute(
                        "INSERT OR IGNORE INTO question_types(id,subject,region,exam_era,name,source) VALUES(?,?,?,?,?,?)",
                        (tid, subject, region, era, name, "builtin"),
                    )
                    n += 1
    return n
