from typing import List, Sequence

import numpy as np
from titiler.core.algorithm import BaseAlgorithm
from rio_tiler.models import ImageData
from skimage.filters import threshold_otsu

## Credit: Sashka Warner (https://github.com/sashkaw)
"""
MIT License

Copyright (c) 2023 Sashka Warner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class DetectFlood(BaseAlgorithm):
    title: str = "Flood detection "
    description: str = "Algorithm to calculate Modified Normalized Difference Water Index (MNDWI), and apply Otsu thresholding algorithm to identify surface water"

    """
    Desc: Algorithm to calculate Modified Normalized Difference Water Index (MNDWI),
    and apply Otsu thresholding algorithm to identify surface water.
    """

    input_bands: List = [
        {'title': 'Green band', 'description': 'The green band with the wavelength between 0.53µm - 0.59µm',
         'required': True,
         'keywords': ['Green band']},
        {'title': 'Short wave infrared band', 'description': 'The SWIR band with wavelength between 0.9μ – 1.7μm',
         'required': True,
         'keywords': ['Shortwave infrared band']},
    ]
    input_description: str = "The bands that will be used to make this calculation"

    # Metadata
    input_nbands: int = 2
    output_nbands: int = 1
    output_min: Sequence[int] = [-1]
    output_max: Sequence[int] = [1]
    output_colormap_name: str = 'viridis'

    def __call__(self, img: ImageData, *args, **kwargs):
        # Extract bands of interest
        green_band = img.data[0].astype("float32")
        swir_band = img.data[1].astype("float32")

        # Calculate Modified Normalized Difference Water Index (MNDWI)
        numerator = (green_band - swir_band)
        denominator = (green_band + swir_band)
        # Use np.divide to avoid divide by zero errors
        mndwi_arr = np.divide(numerator, denominator, np.zeros_like(numerator), where=denominator != 0)

        # Apply Otsu thresholding method
        otsu_threshold = threshold_otsu(mndwi_arr)

        # Use Otsu threshold to classify the computed MNDWI
        classified_arr = mndwi_arr >= otsu_threshold

        # Reshape data -> ImageData only accepts image in form of (count, height, width)
        # classified_arr = np.around(classified_arr).astype(int)
        # classified_arr = np.expand_dims(classified_arr, axis=0).astype(self.output_dtype)
        classified_arr = np.expand_dims(classified_arr, axis=0).astype(int)

        return ImageData(
            classified_arr,
            img.mask,
            assets=img.assets,
            crs=img.crs,
            bounds=img.bounds,
        )
