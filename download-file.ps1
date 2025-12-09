# PowerShell script to download file from FileResponse endpoint

# Method 1: Using Invoke-WebRequest (works for smaller files)
$response = Invoke-WebRequest -Uri "http://localhost:8000/zonal_stats?polygon_url=YOUR_URL&raster_url=YOUR_URL"
# The file bytes are in $response.Content
[System.IO.File]::WriteAllBytes("zonal_stats.fgb", $response.Content)

# Method 2: Using Invoke-WebRequest with OutFile (simpler)
Invoke-WebRequest -Uri "http://localhost:8000/zonal_stats?polygon_url=YOUR_URL&raster_url=YOUR_URL" -OutFile "zonal_stats.fgb"

# Method 3: Using System.Net.WebClient (good for large files)
$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile("http://localhost:8000/zonal_stats?polygon_url=YOUR_URL&raster_url=YOUR_URL", "zonal_stats.fgb")
$webClient.Dispose()

# Method 4: Using Invoke-RestMethod (also works)
$bytes = Invoke-RestMethod -Uri "http://localhost:8000/zonal_stats?polygon_url=YOUR_URL&raster_url=YOUR_URL" -Method Get
[System.IO.File]::WriteAllBytes("zonal_stats.fgb", $bytes)


