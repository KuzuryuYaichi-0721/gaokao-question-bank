$ErrorActionPreference = 'Stop'
Write-Host ''
Write-Host '=== GaokaoQuestionBank STZY token 设置 ===' -ForegroundColor Cyan
Write-Host '粘贴时不会显示字符；不要把 token 发到聊天。' -ForegroundColor Yellow
Write-Host ''
$sec = Read-Host '请粘贴 STZY token（不显示）' -AsSecureString
$cred = [System.Management.Automation.PSCredential]::new('stzy', $sec)
$token = $cred.GetNetworkCredential().Password
$token = $token.Trim()
if ([string]::IsNullOrWhiteSpace($token) -or $token.Length -lt 16) {
    Write-Host 'token 为空或太短，未保存。' -ForegroundColor Red
    Read-Host '按回车关闭'
    exit 1
}
if ($token -match '[\r\n]') {
    Write-Host 'token 含有换行，未保存。' -ForegroundColor Red
    Read-Host '按回车关闭'
    exit 1
}
[Environment]::SetEnvironmentVariable('STZY_ACCESS_TOKEN', $token, 'User')
$env:STZY_ACCESS_TOKEN = $token
Write-Host ''
Write-Host ('已保存到当前用户环境变量 STZY_ACCESS_TOKEN；长度=' + $token.Length) -ForegroundColor Green
Write-Host '关闭本窗口后，重新打开 pwsh，再运行题库命令。' -ForegroundColor Green
Write-Host '如果之后 token 过期，重新运行本脚本即可覆盖。' -ForegroundColor DarkGray
Write-Host ''
Read-Host '按回车关闭'
