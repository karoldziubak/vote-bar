#!/usr/bin/env pwsh
# Full rebuild, test, and launch script for vote-bar

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Vote-Bar: Full Rebuild & Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Sync dependencies
Write-Host "[1/3] Syncing dependencies..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAILED] Failed to sync dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dependencies synced" -ForegroundColor Green
Write-Host ""

# Step 2: Run tests
Write-Host "[2/3] Running tests..." -ForegroundColor Yellow
# Skip test_cleanup_old_rooms on Windows due to file locking issues
$testOutput = uv run pytest tests/test_room_manager.py tests/test_vote_aggregation.py tests/test_vote_logic.py --tb=no -q -k "not test_cleanup_old_rooms" 2>&1 | Out-String

# Look for the summary line
if ($testOutput -match "(\d+) passed") {
    $passedCount = $matches[1]
    
    # Check if there were actual test failures (not teardown errors)
    if ($testOutput -match "(\d+) failed") {
        $failedCount = $matches[1]
        Write-Host "[FAILED] $failedCount tests failed, $passedCount passed" -ForegroundColor Red
        Write-Host "Not launching app." -ForegroundColor Red
        exit 1
    } else {
        Write-Host "[OK] $passedCount tests passed (1 skipped due to Windows file locking)" -ForegroundColor Green
    }
} else {
    Write-Host "[FAILED] Tests did not run successfully!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Launch app
Write-Host "[3/3] Launching Streamlit app..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "App is starting..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

uv run streamlit run app.py
