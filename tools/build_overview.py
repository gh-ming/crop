import os
from osgeo import gdal

def build_overviews(input_dir, output_dir):
    # Get a list of all TIFF files in the input directory
    tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]

    for tiff_file in tiff_files:
        # Open the TIFF file
        tiff_path = os.path.join(input_dir, tiff_file)
        dataset = gdal.Open(tiff_path, gdal.GA_Update)

        if dataset is not None:
            # Build overviews for the TIFF file
            # dataset.BuildOverviews("average", [2, 4, 8, 16])

            # Generate pyramid file (.ovr) for the TIFF file
            gdal.SetConfigOption("USE_RRD", "YES")
            gdal.SetConfigOption("HFA_USE_RRD", "YES")
            dataset.BuildOverviews("average", [2, 4, 8, 16], gdal.TermProgress_nocb)

            print(f"Built overviews for {tiff_file}")

    print("Batch overview building completed.")

# Specify the input and output directories
input_directory = r"G:\download\2024_环境与灾害遥感上机\作业内容\环境与灾害遥感上机实验_2024\data"
output_directory = r"G:\download\2024_环境与灾害遥感上机\作业内容\环境与灾害遥感上机实验_2024\data"

# Call the function to build overviews
build_overviews(input_directory, output_directory)
