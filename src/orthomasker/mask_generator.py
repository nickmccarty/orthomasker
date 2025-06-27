import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

import torch
import numpy as np
import rasterio
from rasterio.windows import from_bounds, Window
from rasterio.features import shapes
import shapely.geometry as sg
import geopandas as gpd

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

class MaskGenerator:
    """
    Generates masks using the Segment Anything Model (SAM) and outputs as GeoJSON features.
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
        merge: bool = False,
        verbose: bool = False,
    ):
        self.sam_checkpoint = sam_checkpoint
        self.model_type = model_type
        self.confidence_threshold = confidence_threshold
        self.tile_size = tile_size
        self.overlap = overlap
        self.class_name = class_name
        self.min_area = min_area
        self.max_area = max_area
        self.merge = merge
        self.verbose = verbose

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        sam = sam_model_registry[self.model_type](checkpoint=self.sam_checkpoint)
        sam.to(device)
        self.mask_generator = SamAutomaticMaskGenerator(sam)

    def generate_geojson(
        self,
        tif_path: str,
        geojson_output: Optional[str] = None,
        fixed_bounds: Optional[Tuple[float, float, float, float]] = None,
    ) -> gpd.GeoDataFrame:
        """
        Generate SAM masks for a TIF and return (and optionally save) as GeoDataFrame/GeoJSON.

        Args:
            tif_path: Path to input TIF file.
            geojson_output: Path to output GeoJSON (optional).
            fixed_bounds: Optional (minx, miny, maxx, maxy) bounding box.

        Returns:
            GeoDataFrame with all (possibly merged) mask polygons.
        """
        results: List[Dict[str, Any]] = []
        start_time = time.time()

        with rasterio.open(tif_path) as src:
            transform = src.transform
            crs = src.crs
            width, height = src.width, src.height

            # Determine processing window
            if fixed_bounds:
                window = from_bounds(*fixed_bounds, transform=src.transform).round_offsets().round_lengths()
                if self.verbose:
                    print(f"🧭 Using fixed bounds: {fixed_bounds}")
            else:
                window = Window(0, 0, width, height)
                if self.verbose:
                    print("🧭 Using full image bounds")

            if self.verbose:
                print(f"📂 Processing mosaic: {tif_path}")
                print(f"🔲 Pixel window for processing: {window}")

            for y in range(int(window.row_off), int(window.row_off + window.height), self.tile_size - self.overlap):
                for x in range(int(window.col_off), int(window.col_off + window.width), self.tile_size - self.overlap):
                    if self.verbose:
                        print(f"  ⚙️ Processing tile at x={x}, y={y}")

                    win_width = min(self.tile_size, width - x)
                    win_height = min(self.tile_size, height - y)
                    tile_window = Window(x, y, win_width, win_height)
                    tile_transform = src.window_transform(tile_window)

                    # Read tile (channels 1,2,3)
                    image_tile = src.read([1, 2, 3], window=tile_window)
                    if np.all(image_tile == 0):
                        if self.verbose:
                            print("    ⏭️ Skipped empty tile")
                        continue

                    # SAM expects HWC, uint8
                    tile_img = np.moveaxis(image_tile, 0, -1)
                    if tile_img.dtype != np.uint8:
                        tile_img = ((tile_img - tile_img.min()) / (tile_img.ptp() + 1e-8) * 255).astype(np.uint8)

                    masks = self.mask_generator.generate(tile_img)
                    for idx, mask in enumerate(masks):
                        confidence = mask["stability_score"] * 100
                        if confidence < self.confidence_threshold:
                            continue

                        for poly, _ in shapes(mask["segmentation"].astype(np.uint8), transform=tile_transform):
                            polygon = sg.shape(poly)
                            area = polygon.area
                            results.append({
                                "id": idx,
                                "class_name": self.class_name,
                                "area": round(area, 2),
                                "confidence": round(confidence, 1),
                                "geometry": polygon,
                            })

        gdf = gpd.GeoDataFrame(results, crs=crs)

        # Area filtering
        if self.min_area is not None:
            gdf = gdf[gdf["area"] >= self.min_area]
        if self.max_area is not None:
            gdf = gdf[gdf["area"] <= self.max_area]

        # --- MERGE LOGIC ---
        if self.merge:
            # Merge all touching/overlapping polygons into distinct polygons
            # This will dissolve all geometries into as few polygons as possible
            dissolved = gdf.dissolve()  # attributes will be lost except geometry
            # Explode into individual polygons if MultiPolygon
            merged_gdf = dissolved.explode(index_parts=False).reset_index(drop=True)
            # Optionally, add class_name and area back
            merged_gdf["class_name"] = self.class_name
            merged_gdf["area"] = merged_gdf.geometry.area
            gdf = merged_gdf

        # Save and/or return
        if geojson_output:
            if self.verbose:
                print("\n💾 Saving results to GeoJSON...")
            gdf.to_file(geojson_output, driver="GeoJSON")
            if self.verbose:
                print(f"✅ Done. Saved to: {geojson_output}")
                print(f"⏱️ Total time: {time.time() - start_time:.2f} seconds")
        return gdf