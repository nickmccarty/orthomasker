# TIF to GeoJSON Converter

A CLI tool that converts TIF files to GeoJSON format with automatic mask generation.

## Installation

```bash
pip install tif2geojson
```

## Usage

```bash
# Basic usage
tif2geojson input.tif output.geojson

# With options
tif2geojson input.tif output.geojson --threshold 0.5 --simplify 0.01
```

### Options

- `--threshold`: Threshold for mask generation (default: 0.5)
- `--simplify`: Simplification tolerance for geometries (default: 0.01)
- `--band`: Band index to use for mask generation (default: 1)
- `--help`: Show help message

## Development

### Setup

```bash
git clone https://github.com/nickmccarty/tif2geojson.git
cd tif2geojson
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

## License

MIT License - see LICENSE file for details.
