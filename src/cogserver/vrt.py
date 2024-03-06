from fastapi import APIRouter
from titiler.core.factory import MultiBaseTilerFactory


router = APIRouter()


class VRTFactory(MultiBaseTilerFactory):
    """
    Override the MultiBaseTilerFactory to add a VRT endpoint
    Empty register_routes method to override all routes and have no routes
    """

    def register_routes(self):
        pass