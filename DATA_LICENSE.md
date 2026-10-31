# Data License and Redistribution Boundary

This repository uses two licenses:

- **Code** (`bank/`, scripts, schema, tests): MIT, see `LICENSE`.
- **Open dataset** (`data/open/`): Apache License 2.0, see `LICENSE-APACHE-2.0`.

## Open dataset

`data/open/gaokao-bench-2016-2022.json` is derived from
[OpenLMLab/GAOKAO-Bench](https://github.com/OpenLMLab/GAOKAO-Bench), which is
distributed under Apache-2.0. The normalized dataset keeps the upstream
questions, answers, and explanations and adds source/license metadata.

- Source: https://github.com/OpenLMLab/GAOKAO-Bench
- License: Apache-2.0
- Attribution: see `NOTICE` and `THIRD_PARTY_NOTICES.md`
- No endorsement by OpenLMLab is implied.

## Excluded material

The following are **not** part of this repository or its releases:

- GAOKAO-Bench-Updates 2023–2024: upstream has no declared license.
- Xiaohongshu notes and OCR results from 2025: third-party copyright.
- GaokaoCoach synthetic demo questions: not real exam questions.
- Scanned papers, images, PDFs, audio, SQLite databases, and user progress.

Local copies used for private study are not granted any redistribution rights
by this repository.

## Contributions

By contributing code, you agree to license it under MIT. By contributing data,
you must include the source URL, license, and attribution; do not submit
copyrighted scans, third-party notes, API tokens, or personal data.
