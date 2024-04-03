from typing import Sequence
import numpy
from typing import List
from pydantic import Field
from rio_tiler.models import ImageData
from titiler.core.algorithm.base import BaseAlgorithm







class RapidChangeAssessment(BaseAlgorithm):

    title: str = "Rapid Change Assessment Tool"
    description: str = "Detect changes by subtracting relative radiances between two images taken between and after an event"

    """Rapid change assessment."""
    # parameters
    # threshold: float = Field(
    #     default=0, ge=0.0, le=1.0,
    #     title="Threshold(%)",
    #     description="Only pixels with change/decrease above this threshold will be supplied"
    # )

    only_negative: bool = Field(
        default=True,
        title='Only negative',
        description='Compute only pixels whose values have decreased between the two dates'

    )

    # cloud_mask: bool = Field(
    #     False,
    #     title="Cloud mask",
    #     description="If enabled, cloud will be removed masked by band 3 and band 4."
    # )

    cloud_mask_value: int = Field(
        default=1,
        ge=0,
        le=5,
        title="Cloud mask threshold",
        description="Inclusive cloud threshold. Specifying a value results in considering all lower values",
        options_descriptions = ['No clouds', 'Almost no clouds', 'Very few clouds', 'Partially cloudy', 'Cloudy', 'Very cloudy' ]
    )



    # metadata
    input_nbands: int = 2
    input_description: str = "The bands that will be used to detect changes"
    input_bands: List = [
        {'title': 'Start date image', 'description': 'The image before the event',  'required':True},
        {'title': 'End date image', 'description': 'The image after the event',  'required':True},
        {'title': 'Start date cloud mask', 'description': 'The cloud mask of the image before the event',
         'required': True},
        {'title': 'End date cloud mask', 'description': 'The cloud mask of the image after the event',
         'required': True},
    ]

    # input_second_image_title: str = 'Second image'
    # input_second_image_description: str = 'The image after the event'

    output_nbands: int = 1
    output_dtype: int = "int8"
    output_min: Sequence[int] = [-100]
    output_max: Sequence[int] = [100]
    output_description: str = "Pixels/locations whose values have decreased/changed"

    def __call__(self, img: ImageData) -> ImageData:
        """Rapid change assessment."""
        b1 = img.array[0]
        b2 = img.array[1]
        b2 = b2 / b2.max()
        b1 = b1 / b1.max()
        valid_mask = (img.array[2].astype('uint8') > self.cloud_mask_value) | (img.array[3].astype('uint8') > self.cloud_mask_value)
        diff = b2-b1
        data = diff
        v = .1
        #v = data.ptp()*.1

        datam = (data > -v) & (data < v)

        if self.only_negative:
            datam |= data>0


        arr = numpy.ma.masked_array(data*100, dtype=self.output_dtype, mask=valid_mask | datam )

        word = 'changes' if not self.only_negative else 'decrease'

        return ImageData(
            arr,
            assets=img.assets,
            crs=img.crs,
            bounds=img.bounds,
            band_names=[f"Relative {word} in pixels value"],
        )

