from titiler.application import main as default
from cogserver.dependencies import SignedDatasetPath
import logging
import dataclasses
from fastapi import FastAPI
from titiler.core.factory import TilerFactory, MultiBandTilerFactory
from titiler.application import __version__ as titiler_version
from cogserver.landing import setup_landing
from starlette.middleware.cors import CORSMiddleware
from titiler.mosaic.factory import MosaicTilerFactory


logging.basicConfig()
logger = logging.getLogger(__name__)



api_settings = default.api_settings




#################################### APP ######################################
app = FastAPI(
    title=api_settings.name,
    openapi_url="/api",
    docs_url="/api.html",
    description="""A modern dynamic tile server built on top of FastAPI and Rasterio/GDAL.
---

**Documentation**: <a href="https://developmentseed.org/titiler/" target="_blank">https://developmentseed.org/titiler/</a>

**Source Code**: <a href="https://github.com/developmentseed/titiler" target="_blank">https://github.com/developmentseed/titiler</a>

---
""",
    version=titiler_version,
    root_path=api_settings.root_path,
)

###############################################################################

#################################### COG ######################################
cog = TilerFactory(
    router_prefix="/cog",
    extensions=[
        # cogValidateExtension(),
        # cogViewerExtension(),
        # stacExtension(),
    ],
    path_dependency=SignedDatasetPath
)
app.include_router(cog.router, prefix="/cog", tags=["Cloud Optimized GeoTIFF"])

###############################################################################

############################# MosaicJSON ######################################
from cogserver.extensions import createMosaicJsonExtension
mosaic = MosaicTilerFactory(
    router_prefix="/mosaicjson",
    path_dependency=SignedDatasetPath,
    extensions=[
        createMosaicJsonExtension()
    ]
)
app.include_router(mosaic.router, prefix="/mosaicjson", tags=["MosaicJSON"])


###############################################################################

############################# MultiBand #######################################




###############################################################################


############################# Algorithms ######################################




###############################################################################


############################# TileMatrixSets ##################################




###############################################################################


setup_landing(app)


# Set all CORS enabled origins
if api_settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )