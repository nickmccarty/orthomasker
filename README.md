# TIF to GeoJSON Converter

A CLI tool that converts TIF files to GeoJSON format with automatic mask generation.

## Installation

```bash
pip install orthomasker
```

## Usage

```bash
# Using CLI
orthomasker your_input_filename.tif your_output_filename.geojson --sam-checkpoint sam_vit_h_4b8939.pth --confidence-threshold 80 --verbose

# Using Python
from orthomasker.converter import TifToGeoJsonConverter

# Set up the converter (use the path to your .pth file)
converter = TifToGeoJsonConverter(
    sam_checkpoint="sam_vit_h_4b8939.pth",
    confidence_threshold=80.0,
    verbose=True,
)

# Provide your own test TIF file (upload or use a sample)
input_tif = "your_input_filename.tif"
output_geojson = "your_output_filename.geojson"

converter.convert(input_tif, output_geojson)
```

### Options

- `--sam-checkpoint`: Path to SAM model weights (default: sam_vit_h_4b8939.pth)

- `--model-type`: SAM model type (`vit_h`, `vit_l`, `vit_b`; default: vit_h)

- `--confidence-threshold`: Minimum stability score to keep a mask (0–100; default: 0, no filter)

- `--tile-size`: Tile size for processing (default: 1024)

- `--overlap`: Tile overlap in pixels (default: 128)

- `--class-name`: Class label for output features (default: sam_object)

- `--fixed-bounds`: Bounding box (minx, miny, maxx, maxy) in image CRS

- `--verbose`: Enable verbose output

## Development

### Setup

```bash
git clone https://github.com/nickmccarty/orthomasker.git
cd orthomasker
pip install -r requirements.txt
pip install -e ".[ml, dev]"
```

## License

MIT License - see LICENSE file for details.
