from typing import Annotated, Literal, Optional
from titiler.application import main as default
from cogserver.dependencies import SignedDatasetPath
from cogserver.algorithms import algorithms
from rio_tiler.io import STACReader
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import logging
import rasterio
from fastapi import FastAPI, Query
from titiler.core.factory import TilerFactory, MultiBaseTilerFactory, AlgorithmFactory, ColorMapFactory
from titiler.application import __version__ as titiler_version
from titiler.core.models.OGC import Landing, Conformance
from titiler.core.resources.enums import MediaType
from titiler.core.templating import create_html_response
from titiler.core.utils import accept_media_type, update_openapi
from titiler.mosaic.factory import MosaicTilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from titiler.mosaic.errors import MOSAIC_STATUS_CODES
from titiler.extensions.stac import stacExtension

from cogserver.vrt import VRTFactory
from cogserver.extensions.mosaicjson import MosaicJsonExtension
from cogserver.extensions.vrt import VRTExtension

logger = logging.getLogger(__name__)

api_settings = default.api_settings

#################################### APP ######################################
app = FastAPI(
    title=api_settings.name,
    openapi_url="/api",
    docs_url="/index.html",
    description="""A modern dynamic tile server built on top of FastAPI and Rasterio/GDAL.
---

**Documentation**: <a href="https://developmentseed.org/titiler/" target="_blank">https://developmentseed.org/titiler/</a>

**Source Code**: <a href="https://github.com/developmentseed/titiler" target="_blank">https://github.com/developmentseed/titiler</a>

---
""",
    version=titiler_version,
    root_path=api_settings.root_path,
)

# Fix OpenAPI response header for OGC Common compatibility
update_openapi(app)

TITILER_CONFORMS_TO = {
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/req/core",
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/req/landing-page",
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/req/oas30",
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/req/html",
    "http://www.opengis.net/spec/ogcapi-common-1/1.0/req/json",
}

###############################################################################


#################################### COG ######################################
cog = TilerFactory(
    router_prefix="/cog",
    extensions=[
        # cogValidateExtension(),
        # cogViewerExtension(),
        stacExtension(),
    ],
    path_dependency=SignedDatasetPath,
    process_dependency=algorithms.dependency
)
app.include_router(cog.router, prefix="/cog", tags=["Cloud Optimized GeoTIFF"])
TITILER_CONFORMS_TO.update(cog.conforms_to)
###############################################################################

############################# MosaicJSON ######################################


mosaic = MosaicTilerFactory(
    router_prefix="/mosaicjson",
    path_dependency=SignedDatasetPath,
    process_dependency=algorithms.dependency,
    extensions=[
        MosaicJsonExtension()
    ]
)
app.include_router(mosaic.router, prefix="/mosaicjson", tags=["MosaicJSON"])
TITILER_CONFORMS_TO.update(mosaic.conforms_to)
###############################################################################



############################# STAC #######################################
# STAC endpoints

stac = MultiBaseTilerFactory(
    reader=STACReader,
    router_prefix="/stac",
    extensions=[
        # stacViewerExtension(),
    ],
    path_dependency=SignedDatasetPath,
    process_dependency=algorithms.dependency,
)

app.include_router(
    stac.router, prefix="/stac", tags=["SpatioTemporal Asset Catalog"]
)
TITILER_CONFORMS_TO.update(stac.conforms_to)

###############################################################################


############################# MultiBand #######################################


###############################################################################


############################# Algorithms ######################################

algorithmsFactory = AlgorithmFactory(supported_algorithm=algorithms)

app.include_router(
    algorithmsFactory.router, tags=["Algorithms"]
)

TITILER_CONFORMS_TO.update(algorithmsFactory.conforms_to)

############################## VRT ###################################


vrt = VRTFactory(
    router_prefix="/vrt",
    path_dependency=SignedDatasetPath,
    extensions=[
        VRTExtension()
    ]
)

app.include_router(vrt.router, prefix="/vrt", tags=["VRT"])
TITILER_CONFORMS_TO.update(vrt.conforms_to)


###############################################################################


############################# TileMatrixSets ##################################


###############################################################################


############################# ColorMap ##################################
# Colormaps endpoints
cmaps = ColorMapFactory()
app.include_router(
    cmaps.router,
    tags=["ColorMaps"],
)
TITILER_CONFORMS_TO.update(cmaps.conforms_to)

###############################################################################


@app.get("/health", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {
        "versions": {
            "titiler": titiler_version,
            "rasterio": rasterio.__version__,
            "gdal": rasterio.__gdal_version__,
            "proj": rasterio.__proj_version__,
            "geos": rasterio.__geos_version__,
        }
    }


@app.get(
    "/",
    response_model=Landing,
    response_model_exclude_none=True,
    responses={
        200: {
            "content": {
                "text/html": {},
                "application/json": {},
            }
        },
    },
    tags=["OGC Common"],
)
def landing(
    request: Request,
    f: Annotated[
        Optional[Literal["html", "json"]],
        Query(
            description="Response MediaType. Defaults to endpoint's default or value defined in `accept` header."
        ),
    ] = None,
):
    """TiTiler landing page."""
    data = {
        "title": "geo-cogserver",
        "description": "A TiTiler extension for UNDP GeoHub which is a modern dynamic tile server built on top of FastAPI and Rasterio/GDAL.",
        "links": [
            {
                "title": "Landing page",
                "href": str(request.url_for("landing")),
                "type": "text/html",
                "rel": "self",
            },
            {
                "title": "The API definition (JSON)",
                "href": str(request.url_for("openapi")),
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "rel": "service-desc",
            },
            {
                "title": "The API documentation",
                "href": str(request.url_for("swagger_ui_html")),
                "type": "text/html",
                "rel": "service-doc",
            },
            {
                "title": "Conformance Declaration",
                "href": str(request.url_for("conformance")),
                "type": "text/html",
                "rel": "http://www.opengis.net/def/rel/ogc/1.0/conformance",
            },
            {
                "title": "geo-cogserver source code (external link)",
                "href": "https://github.com/UNDP-Data/geo-cogserver",
                "type": "text/html",
                "rel": "doc",
            },
            {
                "title": "TiTiler Documentation (external link)",
                "href": "https://developmentseed.org/titiler/",
                "type": "text/html",
                "rel": "doc",
            },
            {
                "title": "TiTiler source code (external link)",
                "href": "https://github.com/developmentseed/titiler",
                "type": "text/html",
                "rel": "doc",
            },
        ],
    }

    output_type: Optional[MediaType]
    if f:
        output_type = MediaType[f]
    else:
        accepted_media = [MediaType.html, MediaType.json]
        output_type = accept_media_type(
            request.headers.get("accept", ""), accepted_media
        )

    if output_type == MediaType.html:
        return create_html_response(
            request,
            data,
            title="TiTiler",
            template_name="landing",
        )

    return data


@app.get(
    "/conformance",
    response_model=Conformance,
    response_model_exclude_none=True,
    responses={
        200: {
            "content": {
                "text/html": {},
                "application/json": {},
            }
        },
    },
    tags=["OGC Common"],
)
def conformance(
    request: Request,
    f: Annotated[
        Optional[Literal["html", "json"]],
        Query(
            description="Response MediaType. Defaults to endpoint's default or value defined in `accept` header."
        ),
    ] = None,
):
    """Conformance classes.

    Called with `GET /conformance`.

    Returns:
        Conformance classes which the server conforms to.

    """
    data = {"conformsTo": sorted(TITILER_CONFORMS_TO)}

    output_type: Optional[MediaType]
    if f:
        output_type = MediaType[f]
    else:
        accepted_media = [MediaType.html, MediaType.json]
        output_type = accept_media_type(
            request.headers.get("accept", ""), accepted_media
        )

    if output_type == MediaType.html:
        return create_html_response(
            request,
            data,
            title="Conformance",
            template_name="conformance",
        )

    return data

add_exception_handlers(app, DEFAULT_STATUS_CODES)
add_exception_handlers(app, MOSAIC_STATUS_CODES)

# Set all CORS enabled origins
if api_settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

