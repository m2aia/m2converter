# imzML to NRRD/NPY Converter

Docker container for converting imzML files to NRRD and NumPy formats using m2aia and SimpleITK.

## Features

- Converts imzML mass spectrometry imaging data to NRRD and NumPy formats
- Supports both centroid and profile imzML files
- Auto-detects centroids from centroid-format imzML files
- Flexible output options: individual NRRD files, spatial arrays, or flattened lists
- Built-in metadata preservation
- Configurable m/z tolerance

## Quick Start

### Using Docker Compose (Recommended)

1. **Build the image:**
   ```bash
   docker-compose build
   ```

2. **Run the conversion:**
   ```bash
   docker-compose up
   ```

   This will process `kidney_glomerulie/01.imzML` and output files to the `output/` directory.

3. **Process a different file:**
   Edit the `command` line in `docker-compose.yml`:
   ```yaml
   command: ["/input/02.imzML", "--output-dir", "/output", "--save-npy-spatial"]
   ```

### Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t imzml-to-nrrd .
   ```

2. **Run with auto-detected centroids (centroid format only):**
   ```bash
   docker run --rm \
     -v $(pwd)/kidney_glomerulie:/input:ro \
     -v $(pwd)/output:/output \
     imzml-to-nrrd /input/01.imzML --output-dir /output --save-npy-spatial
   ```

3. **Run with specific centroids and NRRD output:**
   ```bash
   docker run --rm \
     -v $(pwd)/kidney_glomerulie:/input:ro \
     -v $(pwd)/output:/output \
     imzml-to-nrrd /input/01.imzML --output-dir /output \
       --centroids 500.0 600.0 700.0 --save-nrrd --save-npy-spatial --save-npy-list
   ```

4. **Run with custom tolerance:**
   ```bash
   docker run --rm \
     -v $(pwd)/kidney_glomerulie:/input:ro \
     -v $(pwd)/output:/output \
     imzml-to-nrrd /input/01.imzML --output-dir /output \
       --tolerance 100 --save-npy-spatial
   ```

## Command-Line Options

- `imzml_file` (required): Path to the input imzML file
- `--centroids`: List of m/z values to extract (if not specified, auto-detects from centroid files)
- `--output-dir`: Output directory (default: same as input)
- `--tolerance`: m/z tolerance in ppm (default: 75)
- `--save-nrrd`: Save individual NRRD files for each m/z value
- `--save-npy-spatial`: Save 3D NumPy array [height, width, n_features] with spatial structure
- `--save-npy-list`: Save 2D NumPy array [n_pixels, n_features] as flattened list
- `--npy-output`: Custom output filename for NumPy arrays (default: `<input>_data`)

## Examples

### Save spatial NumPy array only

```bash
docker run --rm \
  -v $(pwd)/kidney_glomerulie:/input:ro \
  -v $(pwd)/output:/output \
  imzml-to-nrrd /input/01.imzML --output-dir /output --save-npy-spatial
```

### Save all output formats

```bash
docker run --rm \
  -v $(pwd)/kidney_glomerulie:/input:ro \
  -v $(pwd)/output:/output \
  imzml-to-nrrd /input/01.imzML --output-dir /output \
    --save-nrrd --save-npy-spatial --save-npy-list
```

### Process with specific centroids

```bash
docker run --rm \
  -v $(pwd)/kidney_glomerulie:/input:ro \
  -v $(pwd)/output:/output \
  imzml-to-nrrd /input/01.imzML --output-dir /output \
    --centroids 500.0 600.0 700.0 --save-npy-list
```

### Batch process all files

```bash
for i in {01..10}; do
  docker run --rm \
    -v $(pwd)/kidney_glomerulie:/input:ro \
    -v $(pwd)/output:/output \
    imzml-to-nrrd /input/${i}.imzML --output-dir /output --save-npy-spatial
done
```

## Output Files

Depending on the options used, the script generates:

### NRRD Files (--save-nrrd)
- `01_mz_500.0000.nrrd` - Individual ion images for each m/z value
- 2D intensity images with metadata (m/z value, tolerance, source file)
- GZIP compression enabled

### NumPy Arrays

**Spatial format (--save-npy-spatial):**
- `01_data_spatial.npy` - 3D array [height, width, n_features]
- Preserves spatial structure of the imaging data

**List format (--save-npy-list):**
- `01_data_list.npy` - 2D array [n_pixels, n_features]
- Flattened pixel list format

**Metadata:**
- `01_data_metadata.npz` - Contains m/z values, tolerance, and image dimensions

### Loading NumPy Data

```python
import numpy as np

# Load spatial data
spatial_data = np.load('01_data_spatial.npy')  # Shape: (height, width, n_features)

# Load list data
list_data = np.load('01_data_list.npy')  # Shape: (n_pixels, n_features)

# Load metadata
metadata = np.load('01_data_metadata.npz')
mz_values = metadata['mz_values']
tolerance = metadata['tolerance_ppm']
width = metadata['image_width']
height = metadata['image_height']
```

## Spectrum Type Support

- **Centroid imzML**: Automatically extracts centroids from the file when `--centroids` is not specified
- **Profile/Continuous imzML**: Requires manual centroid specification via `--centroids`
