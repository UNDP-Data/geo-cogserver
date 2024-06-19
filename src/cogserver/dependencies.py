from fastapi import Query
from typing_extensions import Annotated
from typing import List
import base64


def parse_signed_url(url: str = None):
    if '?' in url:
        furl, b64token = url.split('?')
        try:
            decoded_token = base64.b64decode(b64token).decode()
        except Exception:
            decoded_token = b64token
        decoded_url = f'{furl}?{decoded_token}'
    else:
        decoded_url = f'{url}'
    return decoded_url


def SignedDatasetPath(url: Annotated[str, Query(description="Unsigned/signed dataset URL")]) -> str:
    """
        FastAPI dependency function that enables
        COG endpoint to handle Azure Blob located&signed raster files
        and combine them into one  multiband GDAL VRT file.
        This allows one to use titiler's  expression parameter
        to perform simple but powerful multiband computations.
        Example
            expression=((b1>0.5)&(b3<100))/b4;

        Each url consists of a base64 encoded SAS token:

        http://localhost:8000/cog/statistics? \
        url=https://undpngddlsgeohubdev01.blob.core.windows.net/testforgeohub/HREA_Algeria_2012_v1%2FAlgeria_rade9lnmu_2012.tif?c3Y9MjAyMC0xMC0wMiZzZT0yMDIyLTAzLTA0VDE0JTNBMzIlM0E0M1omc3I9YiZzcD1yJnNpZz0lMkJUZVd0UnRScG1uNmpTQ1ZHY2JuV3dhUWMlMkJjRlp5c05ENjRDUDlyMERNRSUzRA==& \
        url=https://undpngddlsgeohubdev01.blob.core.windows.net/testforgeohub/HREA_Algeria_2012_v1%2FAlgeria_set_zscore_sy_2012.tif?c3Y9MjAyMC0xMC0wMiZzZT0yMDIyLTAzLTA0VDE0JTNBMzIlM0E0M1omc3I9YiZzcD1yJnNpZz1DTFRBQmI5aVRmV3UlMkZ0VHElMkZ4MCUyQm1hUDFUYVM5eUtDMnB3UTBjOUZmMlNBJTNE \

        The returned value is a str representing a RAM stored GDAL VRT file
        which Titiler will use to resolve the request

        Obviously the rasters need to spatially overlap. Additionaly, the VRT can be created with various params
        (spatial align, resolution, resmapling) that, to some extent can influence the performace of the server

    """
    return parse_signed_url(url=url)


def SignedDatasetPaths(url: Annotated[List[str], Query(description="Unsigned/signed dataset URLs")]) -> str:
    """
        FastAPI dependency function that enables
        COG endpoint to handle Azure Blob located&signed raster files
        and combine them into one  multiband GDAL VRT file.
        This allows one to use titiler's  expression parameter
        to perform simple but powerful multiband computations.
        Example
            expression=((b1>0.5)&(b3<100))/b4;

        Each url consists of a base64 encoded SAS token:

        http://localhost:8000/cog/statistics? \
        url=https://undpngddlsgeohubdev01.blob.core.windows.net/testforgeohub/HREA_Algeria_2012_v1%2FAlgeria_rade9lnmu_2012.tif?c3Y9MjAyMC0xMC0wMiZzZT0yMDIyLTAzLTA0VDE0JTNBMzIlM0E0M1omc3I9YiZzcD1yJnNpZz0lMkJUZVd0UnRScG1uNmpTQ1ZHY2JuV3dhUWMlMkJjRlp5c05ENjRDUDlyMERNRSUzRA==& \
        url=https://undpngddlsgeohubdev01.blob.core.windows.net/testforgeohub/HREA_Algeria_2012_v1%2FAlgeria_set_zscore_sy_2012.tif?c3Y9MjAyMC0xMC0wMiZzZT0yMDIyLTAzLTA0VDE0JTNBMzIlM0E0M1omc3I9YiZzcD1yJnNpZz1DTFRBQmI5aVRmV3UlMkZ0VHElMkZ4MCUyQm1hUDFUYVM5eUtDMnB3UTBjOUZmMlNBJTNE \

        The returned value is a str representing a RAM stored GDAL VRT file
        which Titiler will use to resolve the request

        Obviously the rasters need to spatially overlap. Additionally, the VRT can be created with various params
        (spatial align, resolution, resampling) that, to some extent can influence the performance of the server

    """
    decoded_urls = list()
    for src_url in url:
        decoded_urls.append(parse_signed_url(url=src_url))
    return decoded_urls
