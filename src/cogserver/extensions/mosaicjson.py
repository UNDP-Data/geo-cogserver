from dataclasses import dataclass
from typing import List, Optional

from cogeo_mosaic.mosaic import MosaicJSON
from cogserver.dependencies import SignedDatasetPaths
from fastapi import Depends, Query
from pydantic import BaseModel
from titiler.core.factory import TilerFactory, FactoryExtension
from titiler.core.resources.responses import JSONResponse
from typing_extensions import Annotated

urls = Annotated[List[str], Query(..., description="Dataset URLs")]


class MosaicJsonCreateItem(BaseModel):
    # url: List[str] = Query(..., description="Dataset URL")
    urls: List[str] = urls
    minzoom: int = 0
    maxzoom: int = 22
    attribution: str = None


@dataclass
class MosaicJsonExtension(FactoryExtension):

    def create_mosaic_json(self, urls=None, minzoom=None, maxzoom=None, attribution=None):
        mosaicjson = MosaicJSON.from_urls(urls=urls, minzoom=minzoom, maxzoom=maxzoom, )
        if attribution is not None:
            mosaicjson.attribution = attribution
        return mosaicjson

    # Register method is mandatory and must take a TilerFactory object as input
    def register(self, factory: TilerFactory):
        @factory.router.get(
            "/build",
            response_model=MosaicJSON,
            response_model_exclude_none=True,
            response_class=JSONResponse,
            responses={
                200: {"description": "Return a MosaicJSON from multiple COGs."}},
            operation_id=f"mosaicjson_get_build"
        )
        def build_mosaicJSON(
                url=Depends(SignedDatasetPaths),
                minzoom: Optional[int] = 0,
                maxzoom: Optional[int] = 22,
                attribution: Optional[str] = None

        ):
            return self.create_mosaic_json(urls=url, minzoom=minzoom, maxzoom=maxzoom, attribution=attribution)

        @factory.router.post(
            "/build",
            response_model=MosaicJSON,
            response_model_exclude_none=True,
            response_class=JSONResponse,
            responses={
                200: {"description": "Return a MosaicJSON from multiple COGs."}},
            operation_id=f"mosaicjson_post_build"
        )
        def build_mosaicJSON(payload: MosaicJsonCreateItem):
            url = SignedDatasetPaths(payload.urls)
            minzoom = payload.minzoom
            maxzoom = payload.maxzoom
            attribution = payload.attribution

            return self.create_mosaic_json(urls=url, minzoom=minzoom, maxzoom=maxzoom, attribution=attribution)
