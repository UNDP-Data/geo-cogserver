from typing import Sequence

import numpy
from pydantic import Field
from rio_tiler.models import ImageData

from titiler.core.algorithm.base import BaseAlgorithm


class RapidChangeAssessment(BaseAlgorithm):

    title: str = "Rapid Change Assessment Tool"
    description: str = "Quick assessment to detect changes by comparing two bands"

    """Rapid change assessment."""
    # parameters
    threshold: float = Field(
        0.8, ge=0.0, le=1.0,
        title="Threshold(%)",
        description="Threshold (%) to mask changes which is ranged between 0 and 1"
    )

    cloud_mask: bool = Field(
        False,
        title="Cloud mask",
        description="If enabled, cloud will be removed masked by band 3 and band 4."
    )

    cloud_mask_threshold: int = Field(
        1,
        title="Cloud mask threshold",
        description="Remove cloud if band value is greater than this threshold"
    )

    # metadata
    input_nbands: int = 2
    input_description: str = "the first two bands will be used to compute change detection. " \
                             "the last two bands will be used to mask the result. " \
                             "The first two bands are required. "

    output_nbands: int = 1
    output_dtype: int = "uint8"
    output_min: Sequence[int] = [0]
    output_max: Sequence[int] = [1]
    output_description: str = "Masked result which has changed greater than threshold"

    def __call__(self, img: ImageData) -> ImageData:
        """Rapid change assessment."""
        b1 = img.array[0].astype("float16")
        b2 = img.array[1].astype("float16")

        diff = numpy.abs(b1 - b2)
        total = numpy.abs(b1) + numpy.abs(b2)

        # If the difference is more than threshold, return 1. Otherwise return 0
        data = (diff / total > self.threshold)

        # add additional mask condition to remove cloud
        if self.cloud_mask and len(img.array) > 2:
            # add the third band to mask
            b3 = img.array[2].astype("uint8")
            valid_mask = (b3 > self.cloud_mask_threshold)

            if len(img.array) > 3:
                # add the fourth band to mask if available
                b4 = img.array[3].astype("uint8")
                valid_mask = valid_mask | (b4 > self.cloud_mask_threshold)
            arr = numpy.ma.masked_array(data, dtype=self.output_dtype, mask=valid_mask)
        else:
            arr = numpy.ma.masked_array(data, dtype=self.output_dtype)

        bnames = img.band_names
        return ImageData(
            arr,
            assets=img.assets,
            crs=img.crs,
            bounds=img.bounds,
            band_names=[f"(abs({bnames[1]} - {bnames[0]}) / ({bnames[1]} + {bnames[0]})) > {self.threshold}"],
        )
