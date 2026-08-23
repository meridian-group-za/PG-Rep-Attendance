# Daily refresh of the P&G Rep Attendance dashboard's August data.
# Re-runs extract_month.py against the live "Rep Attendance Auto - August 2026.xlsx"
# workbook and overwrites attendance-data.js in place, so the dashboard
# picks up fresh numbers on next page load with no manual step.
# Scheduled via Task Scheduler: "P&G Rep Attendance Daily Refresh", daily at 09:00.
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\CarinPillay\AppData\Local\Python\bin\python.exe"
$source = Join-Path (Split-Path -Parent $scriptDir) "Rep Attendance Auto - August 2026.xlsx"
$output = Join-Path $scriptDir "attendance-data.js"
$extractScript = Join-Path $scriptDir "extract_month.py"
$logFile = Join-Path $scriptDir "refresh_log.txt"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
try {
    & $python $extractScript $source "AUG" $output "ATTENDANCE_DATA" 2>&1 | Out-File -FilePath $logFile -Append -Encoding utf8
    Add-Content -Path $logFile -Value "$timestamp - OK"
} catch {
    Add-Content -Path $logFile -Value "$timestamp - FAILED: $_"
}
