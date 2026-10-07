# ═══════════════════════════════════════════════════════════════
#  🛑 ERP Test Automation - Stop All Services
# ═══════════════════════════════════════════════════════════════

Clear-Host
Write-Host ""
Write-Host "  🛑 إيقاف كل الخدمات..." -ForegroundColor Red
Write-Host ""

$stopped = @()

# Flask
$py = Get-Process python -ErrorAction SilentlyContinue
if ($py) {
    $py | Stop-Process -Force
    Write-Host "  ✅ اتقفل Flask ($($py.Count) عملية)" -ForegroundColor Green
    $stopped += "Flask"
} else {
    Write-Host "  ℹ️  Flask مش شغال" -ForegroundColor Gray
}

# cloudflared
$cf = Get-Process cloudflared -ErrorAction SilentlyContinue
if ($cf) {
    $cf | Stop-Process -Force
    Write-Host "  ✅ اتقفل cloudflared ($($cf.Count) عملية)" -ForegroundColor Green
    $stopped += "cloudflared"
} else {
    Write-Host "  ℹ️  cloudflared مش شغال" -ForegroundColor Gray
}

# ngrok (لو شغال)
$ng = Get-Process ngrok -ErrorAction SilentlyContinue
if ($ng) {
    $ng | Stop-Process -Force
    Write-Host "  ✅ اتقفل ngrok" -ForegroundColor Green
    $stopped += "ngrok"
}

# Chrome (اختياري - لو عايز)
# Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host ""
if ($stopped.Count -gt 0) {
    Write-Host "  ✅ اتقفل: $($stopped -join ', ')" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  مفيش حاجة كانت شغالة" -ForegroundColor Gray
}
Write-Host ""

Start-Sleep -Seconds 1
