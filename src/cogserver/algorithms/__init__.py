from titiler.core.algorithm import Algorithms, algorithms as default_algorithms
from .rca import RapidChangeAssessment
from .flood_detection import DetectFlood

algorithms: Algorithms = default_algorithms.register(
    {
        "rca": RapidChangeAssessment,
        "flood_detection": DetectFlood,
    }
)
