# STZY 接入

## 当前状态

- Bearer 客户端、HAR 检查器、SQLite 检索已实现。
- `source.search_path` / `detail_path` 尚未配置；没有这两个路径不能抓取。
- 需要一份登录后的 HAR 或脱敏请求样本。

## 安全

- token 只在本机环境变量 `STZY_TOKEN` 或未提交的 `config.local.json`。
- HAR 只放 `inbox/`，`.gitignore` 已忽略。
- 不绕过登录、验证码、付费墙。
