# Push local SQLite database and media to the Coolify server.
# Usage (PowerShell):
#   .\scripts\push_production_data.ps1 -Server "root@YOUR_SERVER_IP"
#
# Prerequisites:
#   - OpenSSH client (scp) installed
#   - Server folders exist: /data/yvesgashugi/data and /data/yvesgashugi/media
#   - Local migrations applied: python manage.py migrate

param(
    [Parameter(Mandatory = $true)]
    [string]$Server,

    [string]$RemoteDataDir = "/data/yvesgashugi/data",
    [string]$RemoteMediaDir = "/data/yvesgashugi/media",

    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$dbFile = Join-Path $ProjectRoot "db.sqlite3"
$mediaDir = Join-Path $ProjectRoot "media"

if (-not (Test-Path $dbFile)) {
    Write-Error "Local database not found: $dbFile`nRun migrations locally first: python manage.py migrate"
}

Write-Host "==> Applying local migrations (ensures schema matches code)..."
Push-Location $ProjectRoot
python manage.py migrate --noinput
Pop-Location

$dbSizeMb = [math]::Round((Get-Item $dbFile).Length / 1MB, 2)
Write-Host "==> Uploading db.sqlite3 (${dbSizeMb} MB) to ${Server}:${RemoteDataDir}/db.sqlite3"

ssh $Server "mkdir -p '$RemoteDataDir' '$RemoteMediaDir'"
scp $dbFile "${Server}:${RemoteDataDir}/db.sqlite3"

if (Test-Path $mediaDir) {
    $fileCount = (Get-ChildItem $mediaDir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "==> Uploading media/ ($fileCount files) to ${Server}:${RemoteMediaDir}/"
    scp -r "$mediaDir/*" "${Server}:${RemoteMediaDir}/"
} else {
    Write-Warning "No local media/ folder found — skipping media upload."
}

Write-Host ""
Write-Host "Done. On the server, verify:"
Write-Host "  ssh $Server 'ls -lh ${RemoteDataDir}/db.sqlite3 && ls ${RemoteMediaDir} | head'"
Write-Host ""
Write-Host "In Coolify, confirm persistent storage:"
Write-Host "  ${RemoteDataDir}  ->  /app/data"
Write-Host "  ${RemoteMediaDir} ->  /app/media"
Write-Host ""
Write-Host "Then restart/redeploy the application container."
