# SecureBank PostgreSQL Restore Script
# Restores a custom-format backup into a new database.
# The original securebank database is protected.

param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,

    [Parameter(Mandatory = $true)]
    [string]$TargetDatabase
)

$ErrorActionPreference = "Stop"

$ContainerName = "securebank-postgres"
$DatabaseUser = "securebank"
$ContainerBackup = "/tmp/securebank_restore.dump"

# Validate the target database name.
if ($TargetDatabase -notmatch '^[a-zA-Z_][a-zA-Z0-9_]*$') {
    throw "Invalid database name. Use letters, numbers, and underscores."
}

# Protect the original database.
if ($TargetDatabase -eq "securebank") {
    throw "Restore refused: the original securebank database cannot be overwritten."
}

# Check that the backup file exists.
if (-not (Test-Path -LiteralPath $BackupFile -PathType Leaf)) {
    throw "Backup file not found: $BackupFile"
}

# Check that the PostgreSQL container is running.
$ContainerStatus = docker inspect -f '{{.State.Running}}' $ContainerName

if ($LASTEXITCODE -ne 0 -or $ContainerStatus -ne "true") {
    throw "PostgreSQL container is not running."
}

# Check whether the target database already exists.
$ExistingDatabase = docker exec $ContainerName psql `
    -U $DatabaseUser `
    -d postgres `
    -tAc "SELECT 1 FROM pg_database WHERE datname = '$TargetDatabase'"

if ($LASTEXITCODE -ne 0) {
    throw "Could not check whether the target database exists."
}

if ($null -ne $ExistingDatabase -and $ExistingDatabase.Trim() -eq "1") {
    throw "Target database already exists. Choose a new database name; existing databases are never overwritten."
}

Write-Host "Creating target database: $TargetDatabase"

docker exec $ContainerName psql `
    -U $DatabaseUser `
    -d postgres `
    -c "CREATE DATABASE `"$TargetDatabase`";"

if ($LASTEXITCODE -ne 0) {
    throw "Could not create the target database."
}

try {
    Write-Host "Copying backup into PostgreSQL container..."

    docker cp $BackupFile "${ContainerName}:${ContainerBackup}"

    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the backup file."
    }

    Write-Host "Restoring database..."

    docker exec $ContainerName pg_restore `
        -U $DatabaseUser `
        -d $TargetDatabase `
        $ContainerBackup

    if ($LASTEXITCODE -ne 0) {
        throw "Database restore failed."
    }

    Write-Host ""
    Write-Host "Database restored successfully."
    Write-Host "Target database: $TargetDatabase"
}
catch {
    Write-Host "Restore failed. Removing the incomplete target database..."

    docker exec $ContainerName psql `
        -U $DatabaseUser `
        -d postgres `
        -c "DROP DATABASE IF EXISTS `"$TargetDatabase`";"

    throw
}
finally {
    docker exec $ContainerName rm -f $ContainerBackup | Out-Null
}