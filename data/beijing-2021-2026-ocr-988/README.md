# Beijing 2021–2026 batch OCR questions

This dataset contains 988 Beijing questions across 102 paper keys. It is exported from the `beijing-ocr-batch` records in the [banks Beijing dataset](https://github.com/KuzuryuYaichi-0721/gaokao-question-banks/blob/a60375740c06b4a0e9a7dbfd34ac50ef7e0a128e/datasets/beijing-2016-2026-2588.json). The export removes the local PDF path from each record and preserves the original ID and source URL.

The [upstream rights statement](https://github.com/KuzuryuYaichi-0721/gaokao-question-banks/blob/a60375740c06b4a0e9a7dbfd34ac50ef7e0a128e/RIGHTS.md) states that the Beijing compilation was purchased or authorized for redistribution. The upstream export labels these records CC BY 4.0. Attribution is KuzuryuYaichi-0721 / GaokaoCoach. See the [upstream license notes](https://github.com/KuzuryuYaichi-0721/gaokao-question-banks/blob/a60375740c06b4a0e9a7dbfd34ac50ef7e0a128e/DATA_LICENSES.md).

All records have empty answers and C confidence. Check OCR text against the source before using it for assessment.

This is a separate batch associated with the follow-up OCR work described in [PR #3](https://github.com/KuzuryuYaichi-0721/gaokao-question-bank/pull/3). Its paper keys have yet to be reconciled with the pending-paper manifest. Record-level overlap with PR #3 has yet to be measured.

```powershell
python -m bank.cli import-json ./data/beijing-2021-2026-ocr-988/questions.json
```
