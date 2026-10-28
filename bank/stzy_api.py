from __future__ import annotations

import base64, json, os, re, time
from typing import Any

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BASE = "https://qms.stzy.com/matrix"
PATH = {
    "search": "/zw-search/api/v1/homeEs/question/keyPointQuery",
    "tags": "/zw-zzw/api/v1/zzw/tag/queryQuestionTag",
    "dropdown": "/zw-zzw/api/v1/zzw/tag/queryDropDownTag",
    "answer": "/zw-zzw/api/v1/zzw/pickQuestion/getAnswer",
    "detail": "/zw-zzw/api/v1/zzw/home/pickQuestion/questionDetail",
}
WIRE_KEY = b"abADefg234cdegsd"
SUBJECTS = {"语文": "1", "数学": "2", "英语": "3", "政治": "4", "历史": "5", "地理": "6", "物理": "7", "化学": "8", "生物": "9"}
REGIONS = {"全国": "-1", "北京": "110000", "天津": "120000", "河北": "130000", "山西": "140000", "内蒙古": "150000", "辽宁": "210000", "吉林": "220000", "黑龙江": "230000", "上海": "310000", "江苏": "320000", "浙江": "330000", "安徽": "340000", "福建": "350000", "江西": "360000", "山东": "370000", "河南": "410000", "湖北": "420000", "湖南": "430000", "广东": "440000", "广西": "450000", "海南": "460000", "重庆": "500000", "四川": "510000", "贵州": "520000", "云南": "530000", "西藏": "540000", "陕西": "610000", "甘肃": "620000", "青海": "630000", "宁夏": "640000", "新疆": "650000"}


def decode(data: Any) -> Any:
    if isinstance(data, dict): return data
    if not isinstance(data, str): raise ValueError("unexpected payload")
    # Some endpoints already return a JSON string; most return base64 AES-CBC.
    try:
        return json.loads(data)
    except Exception:
        pass
    raw = base64.b64decode(data)
    dec = Cipher(algorithms.AES(WIRE_KEY), modes.CBC(WIRE_KEY)).decryptor()
    plain = dec.update(raw) + dec.finalize()
    # PKCS#7 padding, then any NUL padding.
    if plain:
        pad = plain[-1]
        if 1 <= pad <= 16 and plain.endswith(bytes([pad]) * pad):
            plain = plain[:-pad]
    text = plain.decode("utf-8", errors="ignore").rstrip("\x00").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Tolerate a valid object followed by stray bytes.
        return json.JSONDecoder().raw_decode(text)[0]


class StzyApi:
    def __init__(self, token: str = "", delay: float = 1.2):
        self.token = token or os.environ.get("STZY_ACCESS_TOKEN", "")
        self.delay = delay
        self.s = requests.Session()
        self.s.headers.update({"Content-Type": "application/json", "Accept": "application/json", "X-Plat-Type": "pt_stw", "User-Agent": "GaokaoQuestionBank/0.1"})
        self.s.trust_env = False

    def post(self, path: str, body: dict, auth: bool = False) -> Any:
        headers = {}
        if auth or self.token:
            headers["token"] = self.token
        for attempt in range(4):
            r = self.s.post(BASE + path, headers=headers, json=body, timeout=40)
            if r.status_code == 429:
                time.sleep(15 * (attempt + 1)); continue
            r.raise_for_status()
            j = r.json()
            if str(j.get("code")) != "200":
                raise RuntimeError(f"stzy {j.get('code')}: {j.get('message')}")
            time.sleep(self.delay)
            return decode(j.get("data"))
        raise RuntimeError("stzy rate limited")

    def search(self, subject: str, year: int, province: str, page: int = 1, keyword: str = "") -> dict:
        body = {"onlyCheckUrlAndMethod": True, "pageNum": page, "pageSize": 10, "params": {
            "studyPhaseCode": "300", "subjectCode": SUBJECTS[subject], "searchType": 2, "sort": 2,
            "treeIds": [], "keyWord": keyword, "provinceCode": REGIONS.get(province, "-1"), "yearCode": str(year)
        }}
        return self.post(PATH["search"], body)

    def answer(self, question_id: str) -> Any:
        return self.post(PATH["answer"], {"questionId": question_id}, auth=True)


def html_text(value: str) -> str:
    v = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", value or "", flags=re.I)
    v = re.sub(r"<[^>]+>", "", v)
    v = v.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"[ \t]+", " ", v).strip()


def parse_question(item: dict, subject: str, year: int, province: str) -> dict | None:
    qid = str(item.get("questionId") or "")
    raw = str(item.get("questionArticle") or "")
    text = html_text(raw)
    if not qid or not text: return None
    srcs = item.get("questionSourceList") or []
    title = (srcs[0].get("title") if srcs else "") or str(item.get("questionSource") or "")
    num = re.match(r"^\s*(\d{1,3})\s*[．.、]", text)
    qno = int(num.group(1)) if num else 0
    stem = re.sub(r"^\s*\d{1,3}\s*[．.、]\s*", "", text)
    opts = []
    for m in re.finditer(r"([A-D])\s*[．.、]\s*(.+?)(?=\s*[A-D]\s*[．.、]|$)", stem, re.S):
        opts.append({"key": m.group(1), "text": m.group(2).strip()})
    if opts:
        first = re.search(r"\s*[A-D]\s*[．.、]", stem)
        if first: stem = stem[:first.start()].strip()
    return {
        "id": "stzy-" + qid, "paper_key": "stzy-" + re.sub(r"[^0-9A-Za-z一-龥]+", "-", title)[:120] or f"stzy-{subject}-{year}-{province}",
        "paper_title": title, "subject": subject, "region": province, "exam_era": "old" if year <= 2020 else "new",
        "year": year, "month": 6, "exam_type": "试题网", "section": "", "q_no": qno,
        "q_type": str(item.get("showQuestionTypeName") or ""), "stem": stem, "options": opts,
        "answer": "", "explanation": "", "score": 0, "knowledge": [],
        "source_site": "stzy", "source_url": f"https://zj.stzy.com/create-paper/question-detail?id={qid}&studyPhaseCode=300&subjectCode={SUBJECTS[subject]}",
        "status": "draft"
    }
