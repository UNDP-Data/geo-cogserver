import sys
import geopandas as gpd
import numpy as np
from exactextract import exact_extract
import rasterio
from io import BytesIO

pseudo_mercator = (
    'PROJCS["WGS 84 / Pseudo-Mercator",'
    'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
    'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],'
    'PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],'
    'PARAMETER["scale_factor",1],PARAMETER["false_easting",0],'
    'PARAMETER["false_northing",0],UNIT["metre",1],AUTHORITY["EPSG","3857"]]'
)  # hardcoded WKT for EPSG:3857

"""
Compute zonal statistics.

Args:
    polygons_url: URL to polygon file
    raster_url: URL to raster file
"""
def compute_zonal_stats(polygons_url, raster_url):
    print("Starting zonal stats...")

    # POLYGONS AND RASTER MUST OVERLAP IN THE SAME COORDINATE SYSTEM
    polygons = gpd.read_file(polygons_url)

    ds = exact_extract(raster_url, polygons, ['sum', 'mean', 'count'], include_geom='True', output='pandas', progress=True)

    buffer = BytesIO() # Create in-memory BytesIO object (stream) that is similar to a file but is stored in RAM instead of disk
    ds.to_file(buffer, driver="FlatGeoBuf") # Write FGB to the in-memory buffer
    
    buffer.seek(0)  # Go back to start of buffer
    file_bytes = buffer.read() # Read bytes from buffer
    buffer.close()
    return file_bytes


if __name__ == "__main__":
    compute_zonal_stats(sys.argv[1], sys.argv[2])


# Invoke-WebRequest -Uri "http://localhost:8000/zonal_stats?polygon_url=https://undpgeohub.blob.core.windows.net/hrea/admin/v5/adm0_polygons.fgb&raster_url=https://undpgeohub.blob.core.windows.net/stacdata/gdp/2001/gdp.tif" -OutFile "test3.fgb"
