from dataclasses import dataclass, field
from typing import Tuple, List, Optional

import rasterio
from starlette.responses import Response
from fastapi import Depends, FastAPI, Query
from titiler.core.factory import BaseTilerFactory, FactoryExtension, TilerFactory
from titiler.core.dependencies import RescalingParams
from titiler.core.factory import TilerFactory
from titiler.core.resources.enums import ImageType

@dataclass
class createMosaicJsonExtension(FactoryExtension):
    pass
