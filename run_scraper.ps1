# Run scraper and push only changed files to GitHub
Set-Location $PSScriptRoot

Write-Host "Running scraper..."
python scraper.py

Write-Host "Checking for changes..."
$changes = git status --porcelain

if ($changes) {
    Write-Host "Changes detected, pushing to GitHub..."
    git add -A
    git commit -m "Update job listings - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git push
    Write-Host "Done."
} else {
    Write-Host "No changes, nothing to push."
}
