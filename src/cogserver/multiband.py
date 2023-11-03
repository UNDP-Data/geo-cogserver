import attr
from typing import List, Dict, Type
from cogserver.dependencies import SignedDatasetPath
import logging
import dataclasses
from fastapi import FastAPI
from titiler.core.factory import TilerFactory, MultiBandTilerFactory
from titiler.application import __version__ as titiler_version
from rio_tiler.errors import InvalidBandName
from rio_tiler.io import BaseReader, COGReader, MultiBandReader
from morecantile import TileMatrixSet
from rio_tiler.constants import WEB_MERCATOR_TMS

logging.basicConfig()
logger = logging.getLogger(__name__)


@attr.s
class MultiFilesBandsReader(MultiBandReader):
    """Multiple Files as Bands."""

    input: List[str] = attr.ib(kw_only=True)
    reader_options: Dict = attr.ib(factory=dict)
    tms: TileMatrixSet = attr.ib(default=WEB_MERCATOR_TMS)
    reader: Type[BaseReader] = attr.ib(default=COGReader)

    def __attrs_post_init__(self):
        """Fetch Reference band to get the bounds."""

        self.bands = [f"b{ix + 1}" for ix in range(len(self.input))]

        # We assume the files are similar so we use the first one to
        # get the bounds/crs/min,maxzoom
        # Note: you can skip that and hard code values
        with self.reader(self.input[0], tms=self.tms, **self.reader_options) as cog:
            self.bounds = cog.bounds
            self.crs = cog.crs
            self.minzoom = cog.minzoom
            self.maxzoom = cog.maxzoom

    def _get_band_url(self, band: str) -> str:
        """Validate band's name and return band's url."""
        if band not in self.bands:
            raise InvalidBandName(f"{band} is not valid")

        index = self.bands.index(band)
        return self.input[index]
