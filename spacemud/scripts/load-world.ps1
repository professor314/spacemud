# Load world content from JSON data files
# Run from the spacemud/ directory
# Server must be running first (run setup.ps1 or 'evennia start')

Write-Host "Loading world content..." -ForegroundColor Cyan

$env:DJANGO_SETTINGS_MODULE = "server.conf.settings"
python -c "import django; django.setup(); import evennia; evennia._init(); from world.batch_code import main; main(type('C', (), {'msg': staticmethod(print)})())"

Write-Host ""
Write-Host "Reloading server to pick up new world data..." -ForegroundColor Cyan
evennia reload

Write-Host ""
Write-Host "World loaded. Go to http://localhost:4001 and type 'look'." -ForegroundColor Green
Write-Host "If you're in Limbo, disconnect and reconnect, then type 'look'." -ForegroundColor Yellow
