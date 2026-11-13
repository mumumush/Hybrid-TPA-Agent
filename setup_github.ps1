# ==============================================================================
# Hybrid TPA-Agent: GitHub 連接與自動推送腳本
# ==============================================================================
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Hybrid TPA-Agent: GitHub 遠端儲存庫連接精靈" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

$username = "ping29065147"
$repoName = "Hybrid-TPA-Agent"
$remoteUrl = "https://github.com/$username/$repoName.git"

Write-Host "偵測到您的 GitHub 帳號: $username" -ForegroundColor Green
Write-Host "建議的儲存庫名稱: $repoName" -ForegroundColor Green
Write-Host "目標遠端網址: $remoteUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "請確認您是否已在 GitHub 上手動建立了該儲存庫？" -ForegroundColor White
Write-Host "若尚未建立，請先前往: https://github.com/new 建立一個名為 $repoName 的公開或私人專案。" -ForegroundColor Magenta
Write-Host ""

$confirm = Read-Host "是否立即設定遠端 origin 並推送到 GitHub? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    try {
        git remote remove origin 2>$null
        git remote add origin $remoteUrl
        Write-Host "[OK] 已成功新增 remote origin: $remoteUrl" -ForegroundColor Green
        
        git branch -M main
        Write-Host "[OK] 主分支已切換為 main" -ForegroundColor Green
        
        Write-Host "正在推送到 GitHub (若跳出登入視窗請依照瀏覽器指示授權)..." -ForegroundColor Yellow
        git push -u origin main
        Write-Host "[SUCCESS] 專案已成功推送到您的 GitHub！" -ForegroundColor Green
        Write-Host "查看您的專案: https://github.com/$username/$repoName" -ForegroundColor Cyan
    } catch {
        Write-Host "[ERROR] 推送失敗，請確認儲存庫是否已在 GitHub 建立或驗證授權。" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
} else {
    Write-Host "已取消推送操作。您可隨時手動執行: git push -u origin main" -ForegroundColor Gray
}
