# stzy 接入资料

把登录后搜索页的 HAR 放到本目录：`inbox/stzy.har`。

要求：

1. 在浏览器登录 stzy.com，打开一次搜索/试卷列表。
2. 开发者工具 → Network → 右键任意搜索请求 → Save all as HAR。
3. HAR 会包含 Cookie/Authorization；程序只读取，不会上传；不要提交 Git。
4. 同时在本机设置 `STZY_TOKEN`，不要把 token 发到聊天。

然后运行：

```powershell
python -m bank.cli har-inspect inbox\stzy.har
python -m bank.cli har-export inbox\stzy.har --out raw\har
```

把 `har-inspect` 输出的路径/参数（不要 token）发给我，我才能写真正的分页抓取器。
