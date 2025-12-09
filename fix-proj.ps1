# Fix PROJ Database Version Mismatch
# This script resolves the "PROJ database version 2 vs 4" error
# that occurs after computer restarts

Write-Host "Fixing PROJ database version mismatch..." -ForegroundColor Yellow

# Activate conda environment
Write-Host "`nActivating conda environment 'geoenv'..." -ForegroundColor Cyan
conda activate geoenv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate conda environment. Make sure conda is initialized." -ForegroundColor Red
    exit 1
}

# Check current PROJ version
Write-Host "`nChecking PROJ installation..." -ForegroundColor Cyan
python -c "import rasterio; print(f'PROJ: {rasterio.__proj_version__}'); print(f'GDAL: {rasterio.__gdal_version__}')"

# Reinstall PROJ and related packages to ensure database consistency
Write-Host "`nReinstalling PROJ, GDAL, and rasterio to fix database version mismatch..." -ForegroundColor Cyan
conda install -y proj gdal rasterio -c conda-forge

# Clear PROJ cache if it exists
$projCachePath = "$env:CONDA_PREFIX\Library\share\proj\proj.db"
if (Test-Path $projCachePath) {
    Write-Host "`nFound PROJ database at: $projCachePath" -ForegroundColor Cyan
    Write-Host "The database will be updated by conda install..." -ForegroundColor Yellow
}

# Verify the fix
Write-Host "`nVerifying PROJ installation..." -ForegroundColor Cyan
python -c "from rasterio.crs import CRS; crs = CRS.from_epsg(4326); print(f'Successfully created CRS from EPSG:4326 - {crs}')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ PROJ database issue resolved!" -ForegroundColor Green
    Write-Host "You can now run 'uvicorn cogserver.server:app --reload' without errors." -ForegroundColor Green
} else {
    Write-Host "`n✗ Issue may persist. Try running:" -ForegroundColor Red
    Write-Host "  conda clean --all" -ForegroundColor Yellow
    Write-Host "  conda install -y proj gdal rasterio -c conda-forge --force-reinstall" -ForegroundColor Yellow
}


