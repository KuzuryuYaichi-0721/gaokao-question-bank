param(
    [ValidateSet('search','ai-search','stats','export-app','import-json')]
    [string]$Action = 'search',
    [string]$Query = '',
    [string]$Subject = '',
    [string]$Region = '',
    [ValidateSet('', 'new', 'old')][string]$ExamEra = '',
    [int]$YearFrom = 0,
    [int]$YearTo = 0,
    [string]$Type = '',
    [int]$QNo = 0,
    [string]$Keyword = '',
    [int]$Limit = 50,
    [string]$Path = '',
    [string]$Config = 'config.local.json'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw '找不到 python。请先安装 Python 3.10+。' }
$args = @('-X','utf8','-m','bank.cli','--config',$Config)
switch ($Action) {
    'search' {
        $args += @('search','--limit',[string]$Limit)
        if ($Subject) { $args += @('--subject',$Subject) }
        if ($Region) { $args += @('--region',$Region) }
        if ($ExamEra) { $args += @('--exam-era',$ExamEra) }
        if ($YearFrom -gt 0) { $args += @('--year-from',[string]$YearFrom) }
        if ($YearTo -gt 0) { $args += @('--year-to',[string]$YearTo) }
        if ($Type) { $args += @('--type',$Type) }
        if ($QNo -gt 0) { $args += @('--q-no',[string]$QNo) }
        if ($Keyword) { $args += @('--keyword',$Keyword) }
    }
    'ai-search' { $args += @('ai-search',$Query,'--limit',[string]$Limit) }
    'stats' { $args += 'stats' }
    'export-app' { $args += @('export-app','--out',$Path) }
    'import-json' { $args += @('import-json',$Path) }
}
Push-Location $root
try { & $py.Source @args; exit $LASTEXITCODE } finally { Pop-Location }
