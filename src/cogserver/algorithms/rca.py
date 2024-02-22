from typing import Sequence

import numpy
from pydantic import Field
from rio_tiler.models import ImageData

from titiler.core.algorithm.base import BaseAlgorithm


class RapidChangeAssessment(BaseAlgorithm):
    """Rapid change assessment."""
    # parameters
    threshold: float = Field(
        0.8, ge=0.0, lt=1.0,
        title="Threshold(%)",
        description="Threshold (%) to mask changes which is ranged between 0 and 1"
    )

    # metadata
    input_nbands: int = 2
    input_description: str = "the first two bands will be used to compute change detection."

    output_nbands: int = 1
    output_dtype: int = "uint8"
    output_min: Sequence[int] = [0]
    output_max: Sequence[int] = [1]
    output_description: str = "Masked result which has changed greater than threshold"

    def __call__(self, img: ImageData) -> ImageData:
        """Rapid change assessment."""
        b1 = img.array[0].astype("float32")
        b2 = img.array[1].astype("float32")

        diff = numpy.abs(b1 - b2)
        total = numpy.abs(b1) + numpy.abs(b2)

        arr = numpy.ma.MaskedArray(diff / total > self.threshold, dtype=self.output_dtype)
        bnames = img.band_names
        return ImageData(
            arr,
            assets=img.assets,
            crs=img.crs,
            bounds=img.bounds,
            band_names=[f"(abs({bnames[1]} - {bnames[0]}) / ({bnames[1]} + {bnames[0]})) > {self.threshold}"],
        )
