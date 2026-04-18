# Reset world: delete all world objects and reload from JSON
# Run from the spacemud/ directory
# WARNING: This deletes all rooms, NPCs, hostiles, artifacts, and repairable objects.
# Player accounts and characters are preserved.

Write-Host "WARNING: This will delete all world objects and reload from JSON." -ForegroundColor Red
$confirm = Read-Host "Type 'yes' to confirm"

if ($confirm -eq "yes") {
    Write-Host "Resetting world..." -ForegroundColor Cyan
    $env:DJANGO_SETTINGS_MODULE = "server.conf.settings"
    python manage.py reset_world --confirm

    Write-Host "Reloading server..." -ForegroundColor Cyan
    evennia reload

    Write-Host "World reset complete." -ForegroundColor Green
    Write-Host "Disconnect and reconnect in the browser, then type 'look'." -ForegroundColor Yellow
} else {
    Write-Host "Cancelled." -ForegroundColor Yellow
}
