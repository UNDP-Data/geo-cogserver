import re
import tempfile
from typing import List, Literal, Optional

from fastapi import Query, Response
from osgeo import gdal
from pydantic import BaseModel
from titiler.core.factory import FactoryExtension
from cogserver.vrt import VRTFactory
from xml.etree import ElementTree as ET


def create_vrt_from_urls(
        urls: List[str],
        resolution: Literal["highest", "lowest", "average", "user"] = "average",
        xRes: float = None,
        yRes: float = None,
        vrtNoData: List[int] = None,
        srcNoData: List[int] = None,
        resamplingAlg: Literal["nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"] = "nearest",

):
    """
    Create a VRT from multiple COGs supplied as URLs

    Args:
        urls (List[str]): List of URLs
        resolution (Literal["highest", "lowest", "average", "user"], optional): Resolution to use for the resulting VRT. Defaults to "average".
        xRes (float, optional): X resolution. Defaults to 0.1. Ignored if resolution is not "user".
        yRes (float, optional): Y resolution. Defaults to 0.1. Ignored if resolution is not "user".
        vrtNoData (List[int], optional): Set nodata values at the VRT band level (different values can be supplied for each band). If the option is not specified, intrinsic nodata settings on the first dataset will be used (if they exist). The value set by this option is written in the NoDataValue element of each VRTRasterBand element. Use a value of None to ignore intrinsic nodata settings on the source datasets. Defaults to 0.
        srcNoData (List[int], optional): Set nodata values for input bands (different values can be supplied for each band). If the option is not specified, the intrinsic nodata settings on the source datasets will be used (if they exist). The value set by this option is written in the NODATA element of each ComplexSource element. Use a value of None to ignore intrinsic nodata settings on the source datasets. Defaults to 0.
        resamplingAlg (Literal["nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"], optional): Resampling algorithm. Defaults to "nearest".

    Returns:
        str: VRT XML
    """
    urls = [f"/vsicurl/{url}" for url in urls]

    if vrtNoData:
        vrtNoData = [str(x) for x in vrtNoData]
        vrtNoData = " ".join(vrtNoData)
    if srcNoData:
        srcNoData = [str(x) for x in srcNoData]
        srcNoData = " ".join(srcNoData)

    options = gdal.BuildVRTOptions(
        separate=True,
        xRes=xRes,
        yRes=yRes,
        resampleAlg=resamplingAlg,
        VRTNodata=vrtNoData,
        srcNodata=srcNoData,
        resolution=resolution,
    )

    with tempfile.NamedTemporaryFile() as temp:
        ds = gdal.BuildVRT(temp.name, urls, options=options)
        ds = None

        data_types = [
            "Byte",
            "UInt16", "Int16", "CInt16",
            "UInt32", "Int32", "CInt32",
            "Float32", "CFloat32",
            "Float64", "CFloat64",
        ]

        with open(temp.name, "r") as file:
            file_text = ET.fromstring(file.read())
            available_bands = file_text.findall("VRTRasterBand")

            # found the largest data type
            largest_index = -1
            for source_band in available_bands:
                data_type = source_band.get("dataType")
                idx = data_types.index(data_type)
                if idx > largest_index:
                    largest_index = idx

            for source_band in available_bands:
                if largest_index > -1:
                    source_band.set("dataType", data_types[largest_index])
                source = None
                complex_source = source_band.find("ComplexSource")
                simple_source = source_band.find("SimpleSource")
                if complex_source is not None:
                    source = complex_source.find("SourceFilename").text
                elif simple_source is not None:
                    source = simple_source.find("SourceFilename").text
                if source is not None:
                    gdalInfo = gdal.Info(source)
                    color_interp = gdalInfo.split("ColorInterp=")[-1].split("\n")[0]
                    dataset_metadata = gdalInfo.split("Metadata:")[-1]
                    metadata_dict = {}
                    pattern = r"(.*?)=(.*)"

                    # non-case sensitive description pattern
                    description_pattern = r"(?i)description=(.*)"

                    description_matches = re.findall(description_pattern, dataset_metadata)
                    if description_matches:
                        ET.SubElement(source_band, "Description").text = description_matches[0]
                    matches = re.findall(pattern, dataset_metadata)
                    for match in matches:
                        metadata_dict[match[0].strip()] = match[1].strip()

                    source_band.append(ET.Element("Metadata"))
                    source_band.append(ET.Element("ColorInterp"))
                    source_band.find("ColorInterp").text = color_interp
                    for key, value in metadata_dict.items():
                        metadata = ET.Element("MDI")
                        metadata.set("key", key)
                        metadata.text = value
                        source_band.find("Metadata").append(metadata)
            return ET.tostring(file_text, encoding="unicode")


class VrtCreationParameters(BaseModel):
    urls: List[str]
    xRes: Optional[float] = None
    yRes: Optional[float] = None
    srcNoData: Optional[List[int]] = None
    vrtNoData: Optional[List[int]] = None
    resamplingAlg: Literal[
        "nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"]
    resolution: Literal["highest", "lowest", "average"]


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
            "",
            response_class=Response,
            responses={200: {"description": "Return a VRT from multiple COGs."}},
            summary="Create a VRT from multiple COGs",
            operation_id=f"vrt_get"
        )
        def create_vrt(
                url: List[str] = Query(..., description="Dataset URLs"),

                srcNoData: List[int] = Query(None,
                                             description="Set nodata values for input bands (different values can be supplied for each band). If the option is not specified, the intrinsic nodata settings on the source datasets will be used (if they exist). The value set by this option is written in the NODATA element of each ComplexSource element. Use a value of None to ignore intrinsic nodata settings on the source datasets."),
                vrtNoData: List[int] = Query(None,
                                             description="Set nodata values at the VRT band level (different values can be supplied for each band). If the option is not specified, intrinsic nodata settings on the first dataset will be used (if they exist). The value set by this option is written in the NoDataValue element of each VRTRasterBand element. Use a value of None to ignore intrinsic nodata settings on the source datasets."),
                resamplingAlg: Literal[
                    "nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"] = Query("nearest",
                                                                                                         description="Resampling algorithm"),
                resolution: Literal["highest", "lowest", "average", "user"] = Query("average",
                                                                                    description="Resolution to use for the resulting VRT"),
                xRes: Optional[float] = Query(None,
                                              description="X resolution. Applicable only when `resolution` is `user`"),
                yRes: Optional[float] = Query(None,
                                              description="Y resolution. Applicable only when `resolution` is `user`")
        ):
            if len(url) < 1:
                return Response("Please provide at least two URLs", status_code=400)

            if resolution == "user" and (not xRes or not yRes):
                return Response("Please provide xRes and yRes for user resolution", status_code=400)

            return Response(create_vrt_from_urls(
                urls=url,
                xRes=xRes,
                yRes=yRes,
                srcNoData=srcNoData,
                vrtNoData=vrtNoData,
                resamplingAlg=resamplingAlg,
                resolution=resolution
            ), media_type="application/xml")

        @factory.router.post(
            "",
            response_class=Response,
            responses={200: {"description": "Return a VRT from multiple COGs."}},
            summary="Create a VRT from multiple COGs",
            operation_id=f"vrt_post"
        )
        def create_vrt(
                payload: VrtCreationParameters,
        ):
            urls = payload.urls
            if len(urls) < 1:
                return Response("Please provide at least one URL", status_code=400)
            return Response(create_vrt_from_urls(
                urls=urls,
                xRes=payload.xRes,
                yRes=payload.yRes,
                srcNoData=payload.srcNoData,
                vrtNoData=payload.vrtNoData,
                resamplingAlg=payload.resamplingAlg,
                resolution=payload.resolution
            ), media_type="application/xml")
