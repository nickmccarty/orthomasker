# Installation Instructions

## Basic Installation

Install the core dependencies:
```bash
pip install -r requirements.txt
```

Or install via pip (after publishing):
```bash
pip install ortho-masker
```

## Development Installation

For development with all dev tools:
```bash
pip install -r requirements-dev.txt
```

Or using the optional dependencies:
```bash
pip install -e .[dev]
```

## Machine Learning Features

For advanced mask generation using Segment Anything Model:
```bash
pip install -r requirements-ml.txt
```

Or using optional dependencies:
```bash
pip install -e .[ml]
```

You'll also need to download the SAM model weights:
```bash
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

## Complete Installation (All Features)

```bash
pip install -e .[dev,ml]
```

## Platform-Specific Notes

### GDAL Installation
GDAL can be tricky to install. Consider using conda for easier GDAL management:
```bash
conda install -c conda-forge gdal
```

### PyTorch with CUDA
The requirements include PyTorch with CUDA 12.4 support. If you need a different CUDA version or CPU-only PyTorch, visit https://pytorch.org/get-started/locally/ for the appropriate installation command.

### OpenCV
Multiple OpenCV packages are included for maximum compatibility:
- `opencv-python`: Basic OpenCV functionality
- `opencv-contrib-python`: OpenCV with additional modules
- `opencv-python-headless`: OpenCV without GUI dependencies (good for servers)

## Verification

Test your installation:
```bash
python -c "import ortho-masker; print('Installation successful!')"
```
