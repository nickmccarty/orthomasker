"""TIF to GeoJSON converter with SAM-based automatic mask generation."""

__version__ = "0.1.0"
__author__ = "Nicholas McCarty"
__email__ = "nick@upskilled.consulting"

from .converter import TifToGeoJsonConverter
from .mask_generator import MaskGenerator

__all__ = ["TifToGeoJsonConverter", "MaskGenerator"]
