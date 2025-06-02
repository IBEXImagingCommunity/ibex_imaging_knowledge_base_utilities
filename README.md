## IBEX Imaging Knowledge-Base Utilities

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) &nbsp;&nbsp;
![Package Testing](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base_utilities/actions/workflows/main.yml/badge.svg)

The scripts in this repository are utilities used to manage the [IBEX Imaging Community Knowledge-Base](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base) and
accompanying [website](https://ibeximagingcommunity.github.io/ibex_imaging_knowledge_base).

### Installation

1. Create a Python virtual environment using [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/projects/conda/en/stable/).
2. Follow [these instructions](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base_utilities/releases/latest) to install the latest utilities.

### Creating supporting material

Creating supporting material can be done manually, writing markdown files or in a semi-automated fashion using the [csv2supporting](src/ibex_imaging_knowledge_base_utilities/csv_2_supporting.py) script.

Example data for use with the script:
1. csv [input file](tests/data/reagent_batch.csv). The file follows the reagent_resources.csv format with two additional columns titled "Publications" and "Notes". The "Notes" column is free text and can include markdown formatting. The "Publications" column contains the prefixes of markdown file names that contain the publication information. If multiple
publications are associated with the same row, they are separated by a semicolon. These files are expected to be in the
same directory as the csv input file (for example contents see [radtke_pnas.md](tests/data/radtke_pnas.md) and [radtke_nat_prot.md](tests/data/radtke_nat_prot.md)).
2. [Template file](tests/data/supporting_template.md.in) used to create supporting material files.

Create supporting material from the csv file:
```
csv2supporting csv_file supporting_template_file output_directory --image_dir all_images
```

The optional argument `--image_dir` is a directory containing all the images listed in the csv input file. These will be copied to the relevant output directories based on the path to the file listed in the csv. That is, if the file `all_images/image.jpg` is listed in the csv file as `FOXP3_eF570/image.jpg`, it will be copied to the `FOXP3_eF570` directory.
