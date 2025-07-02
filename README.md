# Raster Feature Extractor

A CLI tool and Python library for extracting vector features from geospatial raster (TIF) files using Meta AI's Segment Anything Model (SAM), and exporting them as GeoJSON.

## Installation

```bash
pip install orthomasker
```

Note: Installation using `pip` will fail in environments lacking a previous installation of the `GDAL` library, which is notoriously difficult to install using `pip`. Instead, using `conda` is generally recommended:

- `conda create -n your_env_name python=3.10 gdal -c conda-forge`
- `conda activate your_env_name`
- `pip install orthomasker`

## Demo

<a href="https://colab.research.google.com/drive/1Yvp9eETLlqrcVZdYu6AP4-viLV-xFdYU?usp=sharing#offline=true&sandboxMode=true" target="_blank">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

## Usage

```bash
# Using CLI
orthomasker your_input_filename.tif your_output_filename.geojson

# Using Python
from orthomasker.feature_extractor import RasterFeatureExtractor

# Provide your own test TIF file (upload or use a sample)
input_tif = "your_input_filename.tif"
output_geojson = "your_output_filename.geojson"

# Set up the extractor (use the path to your .pth file)
extractor = RasterFeatureExtractor()

extractor.convert(input_tif, output_geojson)
```

### Options

- `--sam-checkpoint`: Path to SAM model weights (default: `sam_vit_h_4b8939.pth`)

- `--model-type`: SAM model type (`vit_h`, `vit_l`, `vit_b`; default: `vit_h`)

- `--confidence-threshold`: Minimum stability score to keep a mask (`0–100`; default: `0`, no filter)

- `--tile-size`: Tile size for processing (default: `1024`)

- `--overlap`: Tile overlap in pixels (default: `128`)

- `--class-name`: Class label for output features (default: `sam_object`)

- `--class-id`: Class ID (e.g., `1`) for output features (optional)

- `--min-area`: Minimum area (in square units of TIF CRS) for output features (optional)

- `--max-area`: Maximum area (in square units of TIF CRS) for output features (optional)

- `--compactness`: Minimum compactness threshold (`0.0`–`1.0`) using Polsby-Popper metric for filtering irregular shapes (optional)

- `--fixed-bounds`: Bounding box (`minx`, `miny`, `maxx`, `maxy`) in image CRS

- `--merge`: Merge overlapping polygons in output (optional)

- `--verbose`: Enable verbose output

## Compactness Filtering

The `--compactness` option allows you to filter out irregular or elongated shapes by setting a minimum compactness threshold. This uses the Polsby-Popper compactness metric:
<br>
<br>
`Compactness = (4π × Area) / (Perimeter²)`

- Perfect circle: compactness = 1.0
- Square: compactness ≈ 0.785
- Elongated shapes: compactness approaches 0.0

<br>
Common threshold values:

- 0.1: Very permissive (removes only extremely irregular shapes)
- 0.3: Moderate filtering (removes highly irregular shapes)
- 0.6: Strict filtering (keeps only relatively compact shapes)
- 0.8: Very strict (keeps only very round/square shapes)

## Acknowledgments

This project leverages [Meta AI’s Segment Anything Model (SAM)](https://github.com/facebookresearch/segment-anything) for automatic mask generation; many thanks to Alexander Kirillov, et al. for their work!

## Citations

```
@article{kirillov2023segany,
title={Segment Anything},
author={Kirillov, Alexander and Mintun, Eric and Ravi, Nikhila and Mao, Hanzi and Rolland, Chloe and Gustafson, Laura and Xiao, Tete and Whitehead, Spencer and Berg, Alexander C. and Lo, Wan-Yen and Doll{'a}r, Piotr and Girshick, Ross},
journal={arXiv:2304.02643},
year={2023}
}
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.