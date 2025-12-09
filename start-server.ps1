# Start COG Server with proper conda environment activation
# This ensures PROJ database version compatibility

Write-Host "Starting COG Server..." -ForegroundColor Cyan

# Activate conda environment
Write-Host "Activating conda environment 'geoenv'..." -ForegroundColor Yellow
conda activate geoenv

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate conda environment 'geoenv'" -ForegroundColor Red
    Write-Host "Make sure the environment exists: conda env list" -ForegroundColor Yellow
    exit 1
}

# Verify PROJ is working
Write-Host "`nVerifying PROJ installation..." -ForegroundColor Yellow
python -c "from rasterio.crs import CRS; CRS.from_epsg(4326)" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nWARNING: PROJ database version mismatch detected!" -ForegroundColor Red
    Write-Host "Run '.\fix-proj.ps1' first to fix the issue." -ForegroundColor Yellow
    exit 1
}

# Start the server
Write-Host "`nStarting uvicorn server..." -ForegroundColor Green
Write-Host "Server will be available at http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

uvicorn cogserver.server:app --reload


