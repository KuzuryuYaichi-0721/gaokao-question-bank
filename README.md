# Gaokao Question Bank

Open-source question-bank data pipeline and retrieval tools for GaokaoCoach.

- Code: MIT License (`LICENSE`)
- Open dataset: Apache-2.0 (`LICENSE-APACHE-2.0`, `DATA_LICENSE.md`)
- No API token is committed. `STZY_TOKEN` is read from the local environment only.

## What is included

`data/open/gaokao-bench-2016-2022.json` contains **2,996** nine-subject Gaokao questions from **2016–2022**, normalized to the GaokaoCoach question schema.

The questions are derived from [OpenLMLab/GAOKAO-Bench](https://github.com/OpenLMLab/GAOKAO-Bench), which is licensed under Apache-2.0. See `NOTICE` and `THIRD_PARTY_NOTICES.md`.

## What is not included

- GAOKAO-Bench-Updates 2023–2024: the upstream repository has **no declared license**, so these rows are not redistributed here.
- Xiaohongshu 2025 items: third-party content with no redistribution license.
- GaokaoCoach synthetic demo seed: sample questions, not real exam questions.
- Scanned images, PDFs, audio, local SQLite databases, and user progress.

The local GaokaoCoach installation can still contain those items for private study; they are not part of this open-data release.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.json config.local.json
# Only needed for paid/private source access; never commit the token.
$env:STZY_TOKEN = "..."
python -m bank.cli init
python -m bank.cli import-json .\data\open\gaokao-bench-2016-2022.json
python -m bank.cli stats
```

## Commands

```powershell
python -m bank.cli import-json .\data\open\gaokao-bench-2016-2022.json
python -m bank.cli search --subject 数学 --region 河南 --type 导数 --limit 20
python -m bank.cli ai-search "河南新高考数学导数题 第1题"
python -m bank.cli crawl-stzy --subject 数学 --year 2025 --province 河南 --pages 1
python -m bank.cli index-search --subject 数学 --year 2024 --province 河南 --type 导数 --limit 10
python -m bank.cli hydrate stzy-481099108393984000
python -m bank.cli hydrate stzy-481099108393984000 --answer
python -m bank.cli answers-stzy --limit 10
python -m bank.cli import-bench --raw-dir raw/gaokao-bench
python -m bank.cli har-import inbox\stzy.har --subject 数学 --region 河南 --year 2024 --exam-era new
python -m bank.cli stats
python -m bank.cli export-app --out ..\GaokaoCoach\data\questions.json
```

## Data model

- `papers`: paper, region, year, exam era, exam type, source
- `questions`: number, type, stem, options, answer, explanation, source
- `question_index`: search-result summary; full question is fetched only on explicit hydrate
- `question_types`: per subject/region/era taxonomy
- `questions_fts`: full-text search
- `crawl_jobs`: crawl jobs and failure reasons

## Source boundary

`bank/stzy.py` is a Bearer-token client. The search/detail paths in `config.local.json` must be filled in from the user's own account. The project does not bypass login, captcha, or paywalls.

## Open-source status

The repository is public. Code contributions are accepted under MIT; data contributions must state their source and license. Do not open a pull request containing copyrighted scans, third-party notes, API tokens, or user data.
