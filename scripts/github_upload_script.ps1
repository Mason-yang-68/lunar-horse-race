# GitHub 上傳腳本 - 自動組織正確的檔案結構
# 執行此腳本前請確認：
# 1. 已安裝 Git (https://git-scm.com/download/win)
# 2. 已刪除舊的 GitHub Repository

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "GitHub 檔案結構整理與上傳腳本" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 設定變數
$projectPath = "c:\Users\guziy\Documents\過年紅包"
$uploadPath = Join-Path $projectPath "github_upload"
$githubRepo = "https://github.com/Mason-yang-68/lunar-horse-race.git"

# 步驟 1: 創建臨時目錄
Write-Host "[1/6] 創建臨時上傳目錄..." -ForegroundColor Yellow
if (Test-Path $uploadPath) {
    Remove-Item -Path $uploadPath -Recurse -Force
}
New-Item -Path $uploadPath -ItemType Directory -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

# 步驟 2: 複製根目錄檔案
Write-Host "[2/6] 複製根目錄檔案..." -ForegroundColor Yellow
Copy-Item (Join-Path $projectPath "server_render.py") $uploadPath -Force
Copy-Item (Join-Path $projectPath "requirements.txt") $uploadPath -Force
if (Test-Path (Join-Path $projectPath "prize_logic.py")) {
    Copy-Item (Join-Path $projectPath "prize_logic.py") $uploadPath -Force
}
Write-Host "  ✅ server_render.py" -ForegroundColor Green
Write-Host "  ✅ requirements.txt" -ForegroundColor Green

# 步驟 3: 創建並複製 templates 資料夾
Write-Host "[3/6] 創建 templates/ 資料夾..." -ForegroundColor Yellow
$templatesPath = Join-Path $uploadPath "templates"
New-Item -Path $templatesPath -ItemType Directory -Force | Out-Null
Copy-Item (Join-Path $projectPath "templates\host.html") $templatesPath -Force
Copy-Item (Join-Path $projectPath "templates\client.html") $templatesPath -Force
Write-Host "  ✅ templates/host.html" -ForegroundColor Green
Write-Host "  ✅ templates/client.html" -ForegroundColor Green

# 步驟 4: 創建並複製 static 資料夾
Write-Host "[4/6] 創建 static/ 資料夾..." -ForegroundColor Yellow
$staticPath = Join-Path $uploadPath "static"
New-Item -Path $staticPath -ItemType Directory -Force | Out-Null
Copy-Item (Join-Path $projectPath "static\style.css") $staticPath -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $projectPath "static\track_background.jpg") $staticPath -Force -ErrorAction SilentlyContinue
Write-Host "  ✅ static/style.css" -ForegroundColor Green
Write-Host "  ✅ static/track_background.jpg" -ForegroundColor Green

# 步驟 5: 創建並複製 static/images 資料夾
Write-Host "[5/6] 創建 static/images/ 資料夾..." -ForegroundColor Yellow
$imagesPath = Join-Path $staticPath "images"
New-Item -Path $imagesPath -ItemType Directory -Force | Out-Null
$horseImages = Get-ChildItem (Join-Path $projectPath "static\images\horse*.png") -ErrorAction SilentlyContinue
foreach ($img in $horseImages) {
    Copy-Item $img.FullName $imagesPath -Force
    Write-Host "  ✅ static/images/$($img.Name)" -ForegroundColor Green
}

# 步驟 6: 顯示結果
Write-Host ""
Write-Host "[6/6] 檔案結構整理完成!" -ForegroundColor Green
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "檔案結構預覽:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
tree $uploadPath /F

Write-Host ""
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "接下來的步驟:" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "1. 前往 GitHub 刪除舊的 repository (如果還存在)" -ForegroundColor White
Write-Host "   https://github.com/Mason-yang-68/lunar-horse-race/settings" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 創建新的 repository:" -ForegroundColor White
Write-Host "   Name: lunar-horse-race" -ForegroundColor Gray
Write-Host "   Visibility: Public" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 在 PowerShell 中執行以下指令:" -ForegroundColor White
Write-Host ""
Write-Host "   cd `"$uploadPath`"" -ForegroundColor Cyan
Write-Host "   git init" -ForegroundColor Cyan
Write-Host "   git add ." -ForegroundColor Cyan
Write-Host "   git commit -m `"Initial commit with correct structure`"" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git remote add origin $githubRepo" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "準備完成! 請依照上述步驟繼續" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
