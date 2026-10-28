# Gaokao Question Bank

独立、私有、闭源的高考题库数据管线与检索工具，供 GaokaoCoach 调用。

## 边界

- 私有仓库，仅个人学习使用，不再分发。
- `STZY_TOKEN` 只放本机环境变量，不写入仓库。
- 原文件默认放本地/私有 Release，不塞进 Git。
- 不生成题目、不伪造答案；检索结果必须带来源。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.json config.local.json
# 编辑 config.local.json：填 stzy 的搜索/详情接口路径；token 放环境变量
$env:STZY_TOKEN = "..."
python -m bank.cli init
```

## 命令

```powershell
python -m bank.cli import-json .\data\sample.json
python -m bank.cli search --subject 数学 --region 河南 --type 导数 --limit 20
python -m bank.cli ai-search "河南新高考数学导数题 第1题"`npython -m bank.cli har-import inbox\stzy.har --subject 数学 --region 河南 --year 2024 --exam-era new
python -m bank.cli stats
python -m bank.cli export-app --out ..\GaokaoCoach\data\questions.json
```

## 数据模型

- `papers`：套卷、地区、年份、新高考前/后、考试类型、来源
- `questions`：题号、题型、题干、选项、答案、解析、来源
- `question_types`：按学科/地区/新高考时代拆分的题型目录
- `questions_fts`：全文检索
- `crawl_jobs`：抓取任务与失败原因

## stzy 接入

`bank/stzy.py` 是 Bearer token 客户端。`config.local.json` 的 `source.search_path` / `detail_path` 需要按登录后的实际接口填写；没有接口文档时先不要盲目抓取。`bank/cli.py` 不包含绕过登录、验证码或付费墙的代码。

## 题型

- 源站元数据优先
- 本地关键词规则补充
- 不确定项交给 DeepSeek 分类，并记录 `method/confidence`
- 不同地区独立目录：`subject + region + exam_era`

## 检索

支持学科、地区、新高考前/后、年份、题型、题号、关键词/全文，返回来源 URL 和导入状态。
