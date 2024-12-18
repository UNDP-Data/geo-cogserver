from fastapi import APIRouter
from titiler.core.factory import TilerFactory


router = APIRouter()


class VRTFactory(TilerFactory):
    """
    Override the TilerFactory to add a VRT endpoint
    Empty register_routes method to override all routes and have no routes
    """

    def register_routes(self):
        pass