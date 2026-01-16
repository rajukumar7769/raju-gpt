# Cleanup Script for Backup Files
# This script helps identify backup files that can be safely removed

Write-Host "=== RAJU-GPT Backup Files Cleanup ===" -ForegroundColor Cyan
Write-Host ""

# Find all backup files
$backupFiles = @(
    "gpt_app\views_backup.py",
    "gpt_app\views_backup2.py",
    "templates\index_backup.html",
    "templates\index_backup2.html"
)

Write-Host "Backup files found in project:" -ForegroundColor Yellow
foreach ($file in $backupFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  ✓ $file ($size bytes)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ $file (not found)" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "Current active files:" -ForegroundColor Green
Write-Host "  • gpt_app\views.py (active implementation)" -ForegroundColor Green
Write-Host "  • templates\index.html (active template)" -ForegroundColor Green

Write-Host ""
Write-Host "Recommendation:" -ForegroundColor Cyan
Write-Host "  These backup files are now ignored by .gitignore"
Write-Host "  You can safely delete them if you don't need them anymore."
Write-Host ""

$response = Read-Host "Would you like to delete all backup files? (yes/no)"

if ($response -eq "yes" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Deleting backup files..." -ForegroundColor Yellow
    
    foreach ($file in $backupFiles) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "  ✓ Deleted: $file" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "✓ Cleanup completed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Backup files preserved. They are already ignored by git." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
