from fastapi import FastAPI
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi import Depends
import asyncio
from typing import List
import rasterio
import xml.etree.ElementTree as ET

def get_path_dependency(app:FastAPI=None, arg_name=None):
    """
    Extract the first dependency of any kind whose arg name is arg_name
    Used  in conjunction
    :param app:
    :param field_name:
    :return:
    """

    for r in app.routes:
        if hasattr(r, 'dependant') and r.dependant:
            for d in r.dependant.dependencies:
                if d.query_params:
                    fields = [f.name for f in d.query_params]
                    if arg_name in fields:
                        fi = fields.index(arg_name)
                        return r.dependant.dependencies[fi].call


def replace_dependency(app=None, new_dependency=None, arg_name=None):
    print('JUSSI')
    depends = Depends(new_dependency)
    for r in app.routes:
        if hasattr(r, 'dependant') and r.dependant:
            for d in r.dependant.dependencies:
                if d.query_params:
                    fields = [f.name for f in d.query_params]
                    if arg_name in fields:
                        #print(r.path)
                        fi = fields.index(arg_name)
                        old = r.dependant.dependencies.pop(fi)
                        r.dependant.dependencies.insert(  # type: ignore
                            fi,
                            get_parameterless_sub_dependant(
                                depends=depends, path=r.path_format  # type: ignore
                            ),
                        )
                        r.dependencies.extend([depends])
            #print([[e.call for n in e.query_params if n.name == arg_name] for e in r.dependant.dependencies if e])
            #print(r.dependencies)


async def create_vrt_from_urls(urls: List[str]):
    first_url = urls[0]
    first_ds_src = rasterio.open(first_url)
    first_ds_profile = first_ds_src.profile
    first_ds_rasterXSize = first_ds_profile.get("width")
    first_ds_rasterYSize = first_ds_profile.get("height")
    first_ds_crs = first_ds_profile.get("crs")
    first_ds_transform = first_ds_profile.get("transform")
    first_ds_dtype = first_ds_profile.get("dtype")
    first_ds_nodata = first_ds_profile.get("nodata")
    first_ds_blockxsize = first_ds_profile.get("blockxsize")
    first_ds_blockysize = first_ds_profile.get("blockysize")

    if not all([first_ds_rasterXSize, first_ds_rasterYSize, first_ds_crs, first_ds_transform, first_ds_dtype, first_ds_nodata]):
        missing = [k for k, v in locals().items() if v is None]
        raise ValueError(f"The following necessary metadata is missing in source data or could not be retrieved.: {missing}")

    initial_vrt_string = \
        f"""
            <VRTDataset rasterXSize="{first_ds_rasterXSize}" rasterYSize="{first_ds_rasterYSize}">
                <SRS dataAxisToSRSAxisMapping="1,2">{first_ds_crs.to_wkt()}</SRS>
                <GeoTransform> {first_ds_transform.a}, {first_ds_transform.b}, {first_ds_transform.c}, {first_ds_transform.d}, {first_ds_transform.e}, {first_ds_transform.f} </GeoTransform>
            </VRTDataset>
        """
    tree = ET.ElementTree(ET.fromstring(initial_vrt_string))
    root = tree.getroot()
    for url in urls:
        ds_src = rasterio.open(url)
        ds_profile = ds_src.profile
        rasterXSize = ds_profile.get("width")
        rasterYSize = ds_profile.get("height")
        crs = ds_profile.get("crs")
        transform = ds_profile.get("transform")
        dtype = ds_profile.get("dtype")
        nodata = ds_profile.get("nodata")
        blockxsize = ds_profile.get("blockxsize")
        blockysize = ds_profile.get("blockysize")

        band = ET.SubElement(root, "VRTRasterBand", dataType=dtype, band=str(url.split("/")[-1]))
        ET.SubElement(band, "NoDataValue").text = str(nodata)
        source = ET.SubElement(band, "ComplexSource", resampling="near")
        ET.SubElement(source, "SourceFilename").text = f"/vsicurl/{url}"
        ET.SubElement(source, "SourceBand").text = "1"
        source_properties = ET.SubElement(source, "SourceProperties", RasterXSize=str(rasterXSize), RasterYSize=str(rasterYSize), DataType=dtype, BlockXSize=str(blockxsize), BlockYSize=str(blockysize))
        src_rect = ET.SubElement(source, "SrcRect", xOff="0", yOff="0", xSize=str(rasterXSize), ySize=str(rasterYSize))
        dst_rect = ET.SubElement(source, "DstRect", xOff="0", yOff="0", xSize=str(rasterXSize), ySize=str(rasterYSize))
        ET.SubElement(source, "NODATA").text = str(nodata)
    return ET.tostring(root)

if __name__ == "__main__":
    asyncio.run(create_vrt_from_urls(
        urls=[
            "https://undpgeohub.blob.core.windows.net/geo-nightlights/test/SVDNB_npp_d20231229.rade9d_sunfiltered.tif",
            "https://undpgeohub.blob.core.windows.net/geo-nightlights/test/SVDNB_npp_d20240101.rade9d_sunfiltered.tif"
        ]))