# Rebuild and restart Docker container with latest code

Write-Host "Rebuilding Docker container with latest code..." -ForegroundColor Cyan

# Stop any running containers
docker-compose down

# Rebuild the container (no cache to ensure fresh build)
docker-compose build --no-cache

# Start the container
docker-compose up -d

Write-Host "Docker container rebuilt and started!" -ForegroundColor Green
Write-Host "App running at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Gray
