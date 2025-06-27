"""Core conversion logic for TIF to GeoJSON using SAM."""

from pathlib import Path
from typing import Optional, Tuple

from .mask_generator import MaskGenerator

class RasterFeatureExtractor:
    """
    Converts TIF files to GeoJSON using SAM mask generation.
    """

    def __init__(
        self,
        sam_checkpoint: str = "sam_vit_h_4b8939.pth",
        model_type: str = "vit_h",
        confidence_threshold: float = 0.0,
        tile_size: int = 1024,
        overlap: int = 128,
        class_name: str = "sam_object",
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        compactness: Optional[float] = None,
        merge: bool = False,
        verbose: bool = False,
    ):
        self.mask_generator = MaskGenerator(
            sam_checkpoint=sam_checkpoint,
            model_type=model_type,
            confidence_threshold=confidence_threshold,
            tile_size=tile_size,
            overlap=overlap,
            class_name=class_name,
            min_area=min_area,
            max_area=max_area,
            compactness=compactness,
            merge=merge,
            verbose=verbose,
        )

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        fixed_bounds: Optional[Tuple[float, float, float, float]] = None,
    ) -> None:
        """
        Convert TIF file to GeoJSON using SAM masks.

        Args:
            input_path: Path to input TIF.
            output_path: Path to output GeoJSON.
            fixed_bounds: Optional bounding box (minx, miny, maxx, maxy).
        """
        self.mask_generator.generate_geojson(
            tif_path=str(input_path),
            geojson_output=str(output_path),
            fixed_bounds=fixed_bounds,
        )