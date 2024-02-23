from titiler.core.algorithm import Algorithms, algorithms as default_algorithms
from .rca import RapidChangeAssessment

algorithms: Algorithms = default_algorithms.register(
    {
        "rca": RapidChangeAssessment
    }
)
