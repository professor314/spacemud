# First-time setup: install dependencies, migrate database, start server
# Run from the spacemud/ directory

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Running database migration..." -ForegroundColor Cyan
evennia migrate

Write-Host "Starting server..." -ForegroundColor Cyan
Write-Host "You will be prompted to create a superuser account." -ForegroundColor Yellow
evennia start

Write-Host ""
Write-Host "Server started. Open http://localhost:4001 in your browser." -ForegroundColor Green
