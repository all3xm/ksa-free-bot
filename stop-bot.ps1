$ErrorActionPreference = "Stop"

$projectDirectory = [System.IO.Path]::GetFullPath($PSScriptRoot)
$pidFile = [System.IO.Path]::Combine($projectDirectory, "data", "bot.pid")
$botFile = [System.IO.Path]::Combine($projectDirectory, "bot.py")

if (-not [System.IO.File]::Exists($pidFile)) {
    Write-Host "KSA Free BOT is already offline."
    exit 0
}

$storedText = [System.IO.File]::ReadAllText($pidFile).Trim()
$botProcessId = 0
if (-not [int]::TryParse($storedText, [ref]$botProcessId) -or $botProcessId -le 0) {
    [System.IO.File]::Delete($pidFile)
    Write-Host "Removed an old bot status file. The bot is offline."
    exit 0
}

$candidate = Get-CimInstance Win32_Process -Filter "ProcessId = $botProcessId" -ErrorAction SilentlyContinue
if ($null -eq $candidate) {
    [System.IO.File]::Delete($pidFile)
    Write-Host "KSA Free BOT is already offline."
    exit 0
}

$commandLine = [string]$candidate.CommandLine
if ($candidate.Name -notmatch '^python(?:w)?\.exe$' -or $commandLine.IndexOf($botFile, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
    Write-Host "Safety check stopped the shutdown: that process does not belong to this bot."
    Write-Host "You can close the bot's Command Prompt window instead."
    exit 2
}

Stop-Process -Id $botProcessId
Start-Sleep -Milliseconds 500
if ($null -ne (Get-Process -Id $botProcessId -ErrorAction SilentlyContinue)) {
    Write-Host "The bot did not stop. Close its Command Prompt window manually."
    exit 3
}

[System.IO.File]::Delete($pidFile)
Write-Host "KSA Free BOT stopped successfully."
exit 0
