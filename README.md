# NFTGEN V1
A command line utility for batch image generation of NFT - style images. Given a source folder in the working directory that contains a single background `png` and multiple `png` overlays of the same size, this utility generates every possible combination of those images where no two overlayed images share any attributes (see [On-Attributes](#on-attributes)) into a destination folder in the working directory.

## Requirements:
This script requires `Pillow` and `tqdm`. They can be installed with 
```bash
pip install -r requirements.txt
```

## Usage:
```
usage: python3 NFTGenV1.py [-h] -i INPUT_FOLDER_NAME -o OUTPUT_FOLDER_NAME [-p IMAGE_PREFIX]
                   [-a ATTRIBUTES [ATTRIBUTES ...]]
```
```
required arguments: 

-i INPUT_FOLDER_NAME, --input-folder-name INPUT_FOLDER_NAME

    └──Name of input (source) folder in working directory.

-o OUTPUT_FOLDER_NAME, --output-folder-name OUTPUT_FOLDER_NAME

    └──Name of output folder in working directory.
```
```
optional arguments:

-h, --help            show this help message and exit.
                
-p IMAGE_PREFIX, --image-prefix IMAGE_PREFIX
    
    └── Name of the prefix for each batch generated image (default:img).     

-a ATTRIBUTES [ATTRIBUTES ...], --attributes ATTRIBUTES [ATTRIBUTES ...]

    └── List the attributes that you want every batch-generated image to share.
```

## On Attributes:
This program classifies each image file with attributes that are written out in its filename. Each generated image will use *at most* a single source image for each unique attribute (i.e. no generated images use two source images that share an attribute).
-   All attributes should be written with characters `[A-Z-]` *between* underscores.
    > For example, the filename
    >```
    >prefix_FOO_FOO-BAR_0000.png
    >```
    > has two attributes, `FOO` and `FOO-BAR`.

-   The attribute **`BACKGROUND`** is special, and should be reserved for the background image that serves as the "base" for every other layer.
    
-   There must always be an image with the `BACKGROUND` attribute in the source folder.
