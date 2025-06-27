# Raster Feature Extractor

A CLI tool and Python library for extracting vector features from geospatial raster (TIF) files using the Segment Anything Model (SAM), and exporting them as GeoJSON.

## Installation

```bash
pip install orthomasker
```

## Usage

```bash
# Using CLI
orthomasker your_input_filename.tif your_output_filename.geojson \
    --sam-checkpoint sam_vit_h_4b8939.pth \
    --confidence-threshold 80 \
    --min-area 100 \
    --max-area 10000 \
    --verbose

# Using Python
from orthomasker.converter import RasterFeatureExtractor

# Set up the extractor (use the path to your .pth file)
extractor = RasterFeatureExtractor(
    sam_checkpoint="sam_vit_h_4b8939.pth",
    confidence_threshold=80.0,
    min_area=100.0,      # Optional: filter by minimum area
    max_area=10000.0,    # Optional: filter by maximum area
    verbose=True,
)

# Provide your own test TIF file (upload or use a sample)
input_tif = "your_input_filename.tif"
output_geojson = "your_output_filename.geojson"

extractor.convert(input_tif, output_geojson)
```

### Options

- `--sam-checkpoint`: Path to SAM model weights (default: sam_vit_h_4b8939.pth)

- `--model-type`: SAM model type (`vit_h`, `vit_l`, `vit_b`; default: vit_h)

- `--confidence-threshold`: Minimum stability score to keep a mask (0–100; default: 0, no filter)

- `--tile-size`: Tile size for processing (default: 1024)

- `--overlap`: Tile overlap in pixels (default: 128)

- `--class-name`: Class label for output features (default: sam_object)

- `--min-area`: Minimum area (in square units of TIF CRS) for output features (optional)

- `--max-area`: Maximum area (in square units of TIF CRS) for output features (optional)

- `--fixed-bounds`: Bounding box (minx, miny, maxx, maxy) in image CRS

- `--merge`: Merge overlapping polygons in output (optional)

- `--verbose`: Enable verbose output

## Development

### Setup

```bash
git clone https://github.com/nickmccarty/orthomasker.git
cd orthomasker
pip install -r requirements.txt
pip install -e ".[ml,dev]"
```

## Acknowledgments

This project leverages [Meta AI’s Segment Anything Model (SAM)](https://github.com/facebookresearch/segment-anything) for automatic mask generation, which is faciliated by utilizing [`segment-anything-py`](https://pypi.org/project/segment-anything-py/) as a dependency; many thanks to Wu, et al. for their work!

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

MIT License - see LICENSE file for details.
