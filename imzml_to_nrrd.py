#!/usr/bin/env python3
"""
Convert imzML file peaks to NRRD files.
This script reads an imzML file and generates a separate NRRD file for each m/z value
either from a provided centroid list or from the file's own centroids.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import SimpleITK as sitk
import m2aia as m2


def main():
    parser = argparse.ArgumentParser(
        description="Convert imzML peaks to NRRD files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert using file's own centroids
  python imzml_to_nrrd.py input.imzML
  
  # Convert using specific m/z values
  python imzml_to_nrrd.py input.imzML --centroids 100.5 200.3 300.7
  
  # Save individual NRRD files
  python imzml_to_nrrd.py input.imzML --save-nrrd
  
  # Save 3D numpy array [height, width, n_features]
  python imzml_to_nrrd.py input.imzML --save-npy-spatial
  
  # Save 2D numpy array [n_pixels, n_features]
  python imzml_to_nrrd.py input.imzML --save-npy-list
  
  # Save both formats
  python imzml_to_nrrd.py input.imzML --save-npy-spatial --save-npy-list
  
  # Specify output directory
  python imzml_to_nrrd.py input.imzML --output-dir ./output
        """
    )
    
    parser.add_argument(
        "imzml_file",
        type=str,
        help="Path to the input imzML file"
    )
    
    parser.add_argument(
        "--centroids",
        type=float,
        nargs='+',
        default=None,
        help="List of m/z centroid values (if not provided, uses file's centroids)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for NRRD files (default: same as input file)"
    )
    
    parser.add_argument(
        "--tolerance",
        type=float,
        default=75,
        help="m/z tolerance in ppm (default: 75)"
    )
    
    parser.add_argument(
        "--save-nrrd",
        action="store_true",
        help="Save individual NRRD files for each m/z value"
    )
    
    parser.add_argument(
        "--save-npy-spatial",
        action="store_true",
        help="Save 3D numpy array [height, width, n_features] with spatial structure"
    )
    
    parser.add_argument(
        "--save-npy-list",
        action="store_true",
        help="Save 2D numpy array [n_pixels, n_features] as flattened list"
    )
    
    parser.add_argument(
        "--npy-output",
        type=str,
        default=None,
        help="Output filename for numpy array (default: <input>_data.npy)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    imzml_path = Path(args.imzml_file)
    if not imzml_path.exists():
        print(f"Error: Input file '{imzml_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if imzml_path.suffix.lower() != '.imzml':
        print(f"Warning: Input file does not have .imzML extension", file=sys.stderr)
    
    # Set output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = imzml_path.parent
    
    print(f"Loading imzML file: {imzml_path}")
    
    # Load the imzML file using m2aia
    try:
        img = m2.ImzMLReader(str(imzml_path))
        
    except Exception as e:
        print(f"Error loading imzML file: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded imzML file successfully")
    
    # Get spectrum type
    spectrum_type = img.GetSpectrumType()
    print(f"Spectrum type: {spectrum_type}")
    
    # Determine which centroids to use
    if args.centroids:
        centroids = np.array(args.centroids, dtype=np.float32)
        print(f"Using {len(centroids)} provided centroid values")
    else:
        # Check if the file is centroid format
        if "Centroid" in str(spectrum_type):
            # Get centroids from the file's centroid list
            try:
                centroids = img.GetXAxis()  # Returns (mz, intensity)
                print(f"Using {len(centroids)} centroids from centroid imzML file")
            except Exception as e:
                print(f"Error extracting centroids from file: {e}", file=sys.stderr)
                print("Please provide centroids manually using --centroids", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: File is not in centroid format ({spectrum_type})", file=sys.stderr)
            print("Please provide centroids manually using --centroids", file=sys.stderr)
            sys.exit(1)
    
    if len(centroids) == 0:
        print("Error: No centroids found", file=sys.stderr)
        sys.exit(1)
    
    # Set tolerance
    img.SetTolerance(args.tolerance)
    
    print(f"Tolerance: {args.tolerance} ppm")
    print(f"Processing {len(centroids)} peaks...")
    
    # Initialize data matrix if numpy output is requested
    data_matrix_3d = None
    data_matrix_2d = None
    image_shape = None
    
    # Process each centroid
    for i, mz in enumerate(centroids):
        try:
            # Get the ion image for this m/z value (returns ITK image)
            itk_image = img.GetImage(mz, args.tolerance)
            
            # Convert ITK image to SimpleITK image
            sitk_image = sitk.Cast(itk_image, sitk.sitkFloat32)
            
            # Initialize data matrix on first image if needed
            if (args.save_npy_spatial or args.save_npy_list) and image_shape is None:
                image_shape = sitk_image.GetSize()
                data_matrix_3d = np.zeros((image_shape[1], image_shape[0], len(centroids)), dtype=np.float32)
                print(f"Allocated 3D data matrix: {data_matrix_3d.shape} [height, width, n_features]")
            
            # Get numpy array for data matrix if requested
            if data_matrix_3d is not None:
                ion_array = sitk.GetArrayFromImage(sitk_image)
                data_matrix_3d[:, :, i] = ion_array
            
            # Save NRRD file if requested
            if args.save_nrrd:
                # Generate output filename
                output_filename = f"{imzml_path.stem}_mz_{mz:.4f}.nrrd"
                output_path = output_dir / output_filename
                
                # Set metadata
                sitk_image.SetMetaData('mz_value', str(float(mz)))
                sitk_image.SetMetaData('tolerance_ppm', str(args.tolerance))
                sitk_image.SetMetaData('source_file', str(imzml_path.name))
                
                # Write NRRD file using SimpleITK (with compression)
                sitk.WriteImage(sitk_image, str(output_path), useCompression=True)
            
            if (i + 1) % 10 == 0 or (i + 1) == len(centroids):
                print(f"  Processed {i + 1}/{len(centroids)}: m/z = {mz:.4f}")
        except Exception as e:
            print(f"Warning: Failed to process m/z {mz:.4f}: {str(e)}", file=sys.stderr)
            continue
    
    # Save numpy arrays if requested
    if args.save_npy_spatial or args.save_npy_list:
        # Determine output filename
        if args.npy_output:
            npy_base = output_dir / args.npy_output
        else:
            npy_base = output_dir / f"{imzml_path.stem}_data"
        
        if args.save_npy_spatial:
            output_spatial = npy_base.parent / f"{npy_base.stem}_spatial.npy"
            np.save(str(output_spatial), data_matrix_3d)
            print(f"\nSpatial numpy array saved: {output_spatial}")
            print(f"  Shape: {data_matrix_3d.shape} [height, width, n_features]")
            print(f"  Size: {data_matrix_3d.nbytes / (1024**2):.2f} MB")
        
        if args.save_npy_list:
            # Reshape to 2D: [height*width, n_features]
            data_matrix_2d = data_matrix_3d.reshape(-1, len(centroids))
            output_list = npy_base.parent / f"{npy_base.stem}_list.npy"
            np.save(str(output_list), data_matrix_2d)
            print(f"\nList numpy array saved: {output_list}")
            print(f"  Shape: {data_matrix_2d.shape} [n_pixels, n_features]")
            print(f"  Size: {data_matrix_2d.nbytes / (1024**2):.2f} MB")
        
        # Save metadata file with m/z values
        metadata_file = npy_base.parent / f"{npy_base.stem}_metadata.npz"
        np.savez(
            str(metadata_file),
            mz_values=centroids,
            tolerance_ppm=args.tolerance,
            image_width=image_shape[0] if image_shape else 0,
            image_height=image_shape[1] if image_shape else 0,
            source_file=str(imzml_path.name)
        )
        print(f"\nMetadata saved: {metadata_file}")
    
    if args.save_nrrd:
        print(f"\nNRRD files saved to: {output_dir}")
    
    print(f"\nConversion complete!")


if __name__ == "__main__":
    main()
