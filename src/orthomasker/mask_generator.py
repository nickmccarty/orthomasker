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
        class_id: Optional[int] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        compactness: Optional[float] = None,
        merge: bool = False,
        verbose: bool = False,
    ):
        self.sam_checkpoint = sam_checkpoint
        self.model_type = model_type
        self.confidence_threshold = confidence_threshold
        self.tile_size = tile_size
        self.overlap = overlap
        self.class_name = class_name
        self.class_id = class_id
        self.min_area = min_area
        self.max_area = max_area
        self.compactness = compactness
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
                            feature_dict = {
                                "id": idx,
                                "class_name": self.class_name,
                                "area": round(area, 2),
                                "confidence": round(confidence, 1),
                                "geometry": polygon,
                            }
                            
                            # Add class_id if provided
                            if self.class_id is not None:
                                feature_dict["class_id"] = self.class_id
                            
                            results.append(feature_dict)

        gdf = gpd.GeoDataFrame(results, crs=crs)

        # Area filtering
        if self.min_area is not None:
            gdf = gdf[gdf["area"] >= self.min_area]
        if self.max_area is not None:
            gdf = gdf[gdf["area"] <= self.max_area]

        # Compactness filtering
        if self.compactness is not None:
            if self.verbose:
                print(f"🧮 Calculating compactness metrics...")
                print(f"📏 Applying compactness threshold: {self.compactness}")
            
            # Calculate perimeter and compactness (Polsby-Popper metric)
            gdf['perimeter'] = gdf['geometry'].length
            gdf['compactness'] = (4 * np.pi * gdf['area']) / (gdf['perimeter'] ** 2)
            
            # Filter based on compactness threshold
            initial_count = len(gdf)
            gdf = gdf[gdf['compactness'] >= self.compactness]
            
            if self.verbose:
                filtered_count = len(gdf)
                print(f"🔍 Compactness filter: {initial_count} → {filtered_count} features")

        # --- MERGE LOGIC ---
        if self.merge:
            if self.verbose:
                print("🔗 Merging overlapping polygons...")
            
            # Create spatial index for efficient overlap detection
            from shapely.strtree import STRtree
            
            # Build spatial index
            geometries = gdf.geometry.tolist()
            tree = STRtree(geometries)
            
            # Find groups of overlapping polygons
            visited = set()
            groups = []
            
            for idx, geom in enumerate(geometries):
                if idx in visited:
                    continue
                
                # Find all geometries that intersect with current geometry
                group_indices = set([idx])
                candidates = list(tree.query(geom))
                
                # Check actual intersection (not just bounding box overlap)
                for candidate_idx in candidates:
                    if candidate_idx != idx and geom.intersects(geometries[candidate_idx]):
                        group_indices.add(candidate_idx)
                
                # Recursively find all connected overlapping polygons
                queue = list(group_indices - {idx})
                while queue:
                    current_idx = queue.pop(0)
                    if current_idx in visited:
                        continue
                    
                    current_geom = geometries[current_idx]
                    new_candidates = list(tree.query(current_geom))
                    
                    for new_candidate_idx in new_candidates:
                        if (new_candidate_idx not in group_indices and 
                            new_candidate_idx not in visited and
                            current_geom.intersects(geometries[new_candidate_idx])):
                            group_indices.add(new_candidate_idx)
                            queue.append(new_candidate_idx)
                
                groups.append(list(group_indices))
                visited.update(group_indices)
            
            # Create merged polygons with mean confidence scores
            merged_features = []
            
            for group in groups:
                if len(group) == 1:
                    # Single polygon - keep as is
                    row = gdf.iloc[group[0]]
                    feature_dict = {
                        'geometry': row.geometry,
                        'class_name': row.class_name,
                        'area': row.area,
                        'confidence': row.confidence,
                        'compactness': row.get('compactness', None)
                    }
                    
                    # Preserve class_id if it exists
                    if 'class_id' in row and row['class_id'] is not None:
                        feature_dict['class_id'] = row['class_id']
                    
                    merged_features.append(feature_dict)
                else:
                    # Multiple overlapping polygons - merge and calculate mean confidence
                    group_gdf = gdf.iloc[group]
                    
                    # Calculate mean confidence score
                    mean_confidence = group_gdf['confidence'].mean()
                    
                    # Merge geometries
                    merged_geom = group_gdf.geometry.unary_union
                    
                    # Handle MultiPolygon case - explode into individual polygons
                    if merged_geom.geom_type == 'MultiPolygon':
                        for poly in merged_geom.geoms:
                            area = poly.area
                            feature_dict = {
                                'geometry': poly,
                                'class_name': self.class_name,
                                'area': round(area, 2),
                                'confidence': round(mean_confidence, 1)
                            }
                            
                            # Add class_id if it was set
                            if self.class_id is not None:
                                feature_dict['class_id'] = self.class_id
                            
                            # Add compactness if it was calculated
                            if self.compactness is not None:
                                perimeter = poly.length
                                compactness_val = (4 * np.pi * area) / (perimeter ** 2)
                                feature_dict['compactness'] = compactness_val
                            
                            merged_features.append(feature_dict)
                    else:
                        # Single merged polygon
                        area = merged_geom.area
                        feature_dict = {
                            'geometry': merged_geom,
                            'class_name': self.class_name,
                            'area': round(area, 2),
                            'confidence': round(mean_confidence, 1)
                        }
                        
                        # Add class_id if it was set
                        if self.class_id is not None:
                            feature_dict['class_id'] = self.class_id
                        
                        # Add compactness if it was calculated
                        if self.compactness is not None:
                            perimeter = merged_geom.length
                            compactness_val = (4 * np.pi * area) / (perimeter ** 2)
                            feature_dict['compactness'] = compactness_val
                        
                        merged_features.append(feature_dict)
            
            # Create new GeoDataFrame with merged features
            gdf = gpd.GeoDataFrame(merged_features, crs=gdf.crs)
            
            if self.verbose:
                print(f"🔗 Merged into {len(gdf)} features")

        # SAVE OUTPUT (this was missing!)
        if self.verbose:
            elapsed = time.time() - start_time
            print(f"⏱️ Processing completed in {elapsed:.1f} seconds")
            print(f"📊 Generated {len(gdf)} mask features")

        # Save to GeoJSON if output path provided
        if geojson_output:
            # Remove None values from compactness column if it exists
            if 'compactness' in gdf.columns:
                gdf = gdf.dropna(subset=['compactness'])
            
            gdf.to_file(geojson_output, driver="GeoJSON")
            if self.verbose:
                print(f"💾 Saved output to: {geojson_output}")

        return gdf