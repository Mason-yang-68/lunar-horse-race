# GitHub Upload Script
Write-Host "Creating upload directory..." -ForegroundColor Yellow

$projectPath = "c:\Users\guziy\Documents\過年紅包"
$uploadPath = Join-Path $projectPath "github_upload"

# Clean and create upload directory
if (Test-Path $uploadPath) {
    Remove-Item -Path $uploadPath -Recurse -Force
}
New-Item -Path $uploadPath -ItemType Directory -Force | Out-Null

# Copy root files
Write-Host "Copying root files..." -ForegroundColor Yellow
Copy-Item (Join-Path $projectPath "server_render.py") $uploadPath -Force
Copy-Item (Join-Path $projectPath "requirements.txt") $uploadPath -Force

# Create and copy templates
Write-Host "Creating templates folder..." -ForegroundColor Yellow
$templatesPath = Join-Path $uploadPath "templates"
New-Item -Path $templatesPath -ItemType Directory -Force | Out-Null
Copy-Item (Join-Path $projectPath "templates\host.html") $templatesPath -Force
Copy-Item (Join-Path $projectPath "templates\client.html") $templatesPath -Force

# Create and copy static
Write-Host "Creating static folder..." -ForegroundColor Yellow
$staticPath = Join-Path $uploadPath "static"
New-Item -Path $staticPath -ItemType Directory -Force | Out-Null
Copy-Item (Join-Path $projectPath "static\style.css") $staticPath -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $projectPath "static\track_background.jpg") $staticPath -Force -ErrorAction SilentlyContinue

# Create and copy static/images
Write-Host "Creating static/images folder..." -ForegroundColor Yellow
$imagesPath = Join-Path $staticPath "images"
New-Item -Path $imagesPath -ItemType Directory -Force | Out-Null
$horseImages = Get-ChildItem (Join-Path $projectPath "static\images\horse*.png") -ErrorAction SilentlyContinue
foreach ($img in $horseImages) {
    Copy-Item $img.FullName $imagesPath -Force
}

# Also copy audio if exists
if (Test-Path (Join-Path $projectPath "static\audio")) {
    $audioPath = Join-Path $staticPath "audio"
    New-Item -Path $audioPath -ItemType Directory -Force | Out-Null
    Copy-Item (Join-Path $projectPath "static\audio\*") $audioPath -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "File structure ready!" -ForegroundColor Green
Write-Host "Location: $uploadPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Delete old repo at: https://github.com/Mason-yang-68/lunar-horse-race/settings" -ForegroundColor White
Write-Host "2. Create new repo with name: lunar-horse-race (Public)" -ForegroundColor White
Write-Host "3. Run these commands:" -ForegroundColor White
Write-Host ""
Write-Host "cd `"$uploadPath`"" -ForegroundColor Cyan
Write-Host "git init" -ForegroundColor Cyan
Write-Host "git add ." -ForegroundColor Cyan
Write-Host "git commit -m `"Correct folder structure`"" -ForegroundColor Cyan
Write-Host "git branch -M main" -ForegroundColor Cyan
Write-Host "git remote add origin https://github.com/Mason-yang-68/lunar-horse-race.git" -ForegroundColor Cyan
Write-Host "git push -u origin main" -ForegroundColor Cyan
