# Space MUD — Local Deploy Script
# Run from anywhere. Pushes code to GitHub, then SSHs into the server and deploys.
#
# Usage:
#   .\deploy.ps1              — code changes only (pull, migrate, reload)
#   .\deploy.ps1 -ResetWorld  — also rebuild all rooms/NPCs/items from JSON
#
# Prerequisites:
#   - Git remote configured (origin → GitHub)
#   - SSH key at ~/.ssh/space-mud-key.pem
#   - Changes committed before running this

param(
    [switch]$ResetWorld
)

$ErrorActionPreference = "Stop"
$KeyFile = "$env:USERPROFILE\.ssh\space-mud-key.pem"
$Server = "ubuntu@44.198.208.85"

Write-Host "=== Pushing to GitHub ===" -ForegroundColor Cyan
git -C "$PSScriptRoot" push origin main

Write-Host "=== Deploying to server ===" -ForegroundColor Cyan
if ($ResetWorld) {
    ssh -i $KeyFile $Server "~/spacemud/deploy.sh --reset-world"
} else {
    ssh -i $KeyFile $Server "~/spacemud/deploy.sh"
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Game: http://play.imadestuff.com:4001"
