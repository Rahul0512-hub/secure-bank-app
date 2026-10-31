
# SecureBank PostgreSQL Backup Script
# Creates a custom-format backup on the host machine.

$ErrorActionPreference = "Stop"

$ContainerName = "securebank-postgres"
$DatabaseName = "securebank"
$DatabaseUser = "securebank"
$BackupDirectory = Join-Path (Get-Location) "backups"

# Create the backup directory if needed.
New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null

# Use a timestamped filename.
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDirectory "securebank_$Timestamp.dump"

Write-Host "Starting SecureBank database backup..."

# Run pg_dump inside the PostgreSQL container.
docker exec $ContainerName pg_dump `
    -U $DatabaseUser `
    -d $DatabaseName `
    -Fc `
    -f "/tmp/securebank_$Timestamp.dump"

if ($LASTEXITCODE -ne 0) {
    throw "pg_dump failed. Backup was not completed."
}

# Copy the backup from the container to the host.
docker cp "${ContainerName}:/tmp/securebank_$Timestamp.dump" $BackupFile

if ($LASTEXITCODE -ne 0) {
    throw "Could not copy the backup file to the host."
}

# Remove the temporary backup from the container.
docker exec $ContainerName rm "/tmp/securebank_$Timestamp.dump"

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Backup succeeded, but temporary container file cleanup failed."
}

# Display backup file information.
$BackupInfo = Get-Item $BackupFile

Write-Host ""
Write-Host "Backup completed successfully."
Write-Host "File: $($BackupInfo.FullName)"
Write-Host "Size: $([math]::Round($BackupInfo.Length / 1KB, 2)) KB"
