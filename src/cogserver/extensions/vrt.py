import tempfile
from typing import List, Literal, Optional

from fastapi import Query, Response
from osgeo import gdal
from titiler.core.factory import FactoryExtension
from cogserver.vrt import VRTFactory


async def create_vrt_from_urls(
        urls: List[str],
        resolution: Literal["highest", "lowest", "average", "user"] = "average",
        xRes: float = 0.1,
        yRes: float = 0.1,
        vrtNoData: List[str] = 0,
        srcNoData: List[str] = 0,
        resamplingAlg: Literal["nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"] = "nearest",

):
    """
    Create a VRT from multiple COGs supplied as URLs

    Args:
        urls (List[str]): List of URLs
        resolution (Literal["highest", "lowest", "average", "user"], optional): Resolution to use for the resulting VRT. Defaults to "average".
        xRes (float, optional): X resolution. Defaults to 0.1. Ignored if resolution is not "user".
        yRes (float, optional): Y resolution. Defaults to 0.1. Ignored if resolution is not "user".
        vrtNoData (List[str], optional): Set nodata values at the VRT band level (different values can be supplied for each band). If the option is not specified, intrinsic nodata settings on the first dataset will be used (if they exist). The value set by this option is written in the NoDataValue element of each VRTRasterBand element. Use a value of None to ignore intrinsic nodata settings on the source datasets. Defaults to 0.
        srcNoData (List[str], optional): Set nodata values for input bands (different values can be supplied for each band). If the option is not specified, the intrinsic nodata settings on the source datasets will be used (if they exist). The value set by this option is written in the NODATA element of each ComplexSource element. Use a value of None to ignore intrinsic nodata settings on the source datasets. Defaults to 0.
        resamplingAlg (Literal["nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"], optional): Resampling algorithm. Defaults to "nearest".

    Returns:
        str: VRT XML
    """
    urls = [f"/vsicurl/{url}" for url in urls]
    if vrtNoData:
        vrtNoData = " ".join(vrtNoData)
    if srcNoData:
        srcNoData = " ".join(srcNoData)

    options = gdal.BuildVRTOptions(
        separate=True,
        bandList=list(range(1, len(urls) + 1)),
        xRes=xRes,
        yRes=yRes,
        resampleAlg=resamplingAlg,
        VRTNodata=vrtNoData,
        srcNodata=srcNoData,
        resolution=resolution
    )

    with tempfile.NamedTemporaryFile() as temp:
        gdal.BuildVRT(temp.name, urls, options=options)
        with open(temp.name, "r") as file:
            return file.read()


class VRTExtension(FactoryExtension):
    """
    VRT Extension for the VRTFactory
    """
    def register(self, factory: VRTFactory):
        """
        Register the VRT extension to the VRTFactory

        Args:
            factory (VRTFactory): VRTFactory instance

        Returns:
            None
        """
        @factory.router.get(
            "/",
            response_class=Response,
            responses={200: {"description": "Return a VRT from multiple COGs."}},
        )
        async def create_vrt(
                urls: List[str] = Query(..., description="Dataset URLs"),

                srcNoData: List[str] = Query(None,
                                             description="Set nodata values for input bands (different values can be supplied for each band). If more than one value is supplied all values should be quoted to keep them together as a single operating system argument. If the option is not specified, the intrinsic nodata settings on the source datasets will be used (if they exist). The value set by this option is written in the NODATA element of each ComplexSource element. Use a value of None to ignore intrinsic nodata settings on the source datasets."),
                vrtNoData: List[str] = Query(None,
                                             description="Set nodata values at the VRT band level (different values can be supplied for each band). If more than one value is supplied all values should be quoted to keep them together as a single operating system argument. If the option is not specified, intrinsic nodata settings on the first dataset will be used (if they exist). The value set by this option is written in the NoDataValue element of each VRTRasterBand element. Use a value of None to ignore intrinsic nodata settings on the source datasets."),
                resamplingAlg: Literal[
                    "nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"] = Query("nearest",
                                                                                                         description="Resampling algorithm"),
                resolution: Literal["highest", "lowest", "average", "user"] = Query("average",
                                                                                    description="Resolution to use for the resulting VRT"),
                xRes: Optional[float] = Query(None, description="X resolution"),
                yRes: Optional[float] = Query(None, description="Y resolution")
        ):
            """
            Create a VRT from multiple COGs supplied as URLs

            Args:
                urls (List[str]): List of URLs
                srcNoData (List[str], optional): Set nodata values for input bands (different values can be supplied for each band). If the option is not specified, the intrinsic nodata settings on the source datasets will be used (if they exist). The value set by this option is written in the NODATA element of each ComplexSource element. Use a value of None to ignore intrinsic nodata settings on the source datasets. Defaults to None.
                vrtNoData (List[str], optional): Set nodata values at the VRT band level (different values can be supplied for each band). If the option is not specified, intrinsic nodata settings on the first dataset will be used (if they exist). The value set by this option is written in the NoDataValue element of each VRTRasterBand element. Use a value of None to ignore intrinsic nodata settings on the source datasets. Defaults to None.
                resamplingAlg (Literal["nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"], optional): Resampling algorithm. Defaults to "nearest".
                resolution (Literal["highest", "lowest", "average", "user"], optional): Resolution to use for the resulting VRT. Defaults to "average".
                xRes (Optional[float], optional): X resolution. Defaults to None.
                yRes (Optional[float], optional): Y resolution. Defaults to None.

            Returns:
                Response: VRT XML
            """
            if len(urls) < 1:
                return Response("Please provide at least two URLs", status_code=400)

            if resolution == "user" and (not xRes or not yRes):
                return Response("Please provide xRes and yRes for user resolution", status_code=400)

            return Response(await create_vrt_from_urls(
                urls=urls,
                xRes=xRes,
                yRes=yRes,
                srcNoData=srcNoData,
                vrtNoData=vrtNoData,
                resamplingAlg=resamplingAlg,
                resolution=resolution
            ), media_type="application/xml")
