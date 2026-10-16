# migrate_fresh.ps1 - Complete fresh migration script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MasteryAI Fresh Migration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Confirm action
$confirmation = Read-Host "This will DELETE your entire database. Continue? (yes/no)"
if ($confirmation -ne 'yes') {
    Write-Host "Migration cancelled." -ForegroundColor Red
    exit
}

Write-Host "`n1. Cleaning up old files..." -ForegroundColor Yellow

# Delete database
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "   ✓ Deleted db.sqlite3" -ForegroundColor Green
}

# Delete migration files (keep __init__.py)
$migrationDirs = @("lessons\migrations", "api\migrations")
foreach ($dir in $migrationDirs) {
    if (Test-Path $dir) {
        Get-ChildItem "$dir\*.py" -Exclude "__init__.py" | ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Host "   ✓ Deleted $($_.Name)" -ForegroundColor Green
        }
    }
}

# Delete __pycache__ folders
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    Write-Host "   ✓ Deleted $($_.Name)" -ForegroundColor Green
}

Write-Host "`n2. Creating fresh migrations..." -ForegroundColor Yellow
python manage.py makemigrations lessons
python manage.py makemigrations api

Write-Host "`n3. Applying migrations..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "`n4. Migration status:" -ForegroundColor Yellow
python manage.py showmigrations

Write-Host "`n5. Creating superuser..." -ForegroundColor Yellow
python manage.py createsuperuser

Write-Host "`n6. Loading sample data..." -ForegroundColor Yellow
$loadData = Read-Host "Load sample data? (yes/no)"
if ($loadData -eq 'yes') {
    python refresh_db.py
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "  1. Run server: python manage.py runserver"
Write-Host "  2. Admin panel: http://127.0.0.1:8000/admin/"
Write-Host "  3. API root: http://127.0.0.1:8000/api/v1/"
Write-Host "========================================" -ForegroundColor Green