# Installation Instructions

## Basic Installation

```bash
pip install orthomasker
```

Note: Installation using `pip` will fail in environments lacking a previous installation of the `GDAL` library, which is notoriously difficult to install using `pip`. Instead, using `conda` is generally recommended:

- `conda create -n your_env_name python=3.10 gdal -c conda-forge`
- `conda activate your_env_name`
- `pip install orthomasker`

## Demo

<a href="https://colab.research.google.com/drive/1Yvp9eETLlqrcVZdYu6AP4-viLV-xFdYU?usp=sharing#offline=true&sandboxMode=true">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

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

### PyTorch with CUDA
The requirements include PyTorch with CUDA 12.5 support. If you need a different CUDA version or CPU-only PyTorch, visit https://pytorch.org/get-started/locally/ for the appropriate installation command.

### OpenCV
Multiple OpenCV packages are included for maximum compatibility:
- `opencv-python`: Basic OpenCV functionality
- `opencv-contrib-python`: OpenCV with additional modules
- `opencv-python-headless`: OpenCV without GUI dependencies (good for servers)

## Verification

Test your installation:
```bash
python -c "import orthomasker; print('Installation successful!')"
```
