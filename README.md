## IBEX Imaging Knowledge-Base Utilities

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) &nbsp;&nbsp;
![Package Testing](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base_utilities/actions/workflows/main.yml/badge.svg)

The scripts in this repository are utilities used to manage the [IBEX Imaging Community Knowledge-Base](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base) (KB) and
accompanying [website](https://ibeximagingcommunity.github.io/ibex_imaging_knowledge_base).

### Installation

1. Create a Python virtual environment using [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/projects/conda/en/stable/).
2. Follow [these instructions](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base_utilities/releases/latest) to install the latest utilities.

### Validating the KB information

On the commandline, go to the root directory of the KB and run the relevant command for the file(s) you want to validate. For the current way to run the validation scripts, see their usage in the GitHub [actions workflow](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base/blob/26fc5ccc4a4bb36239cc7b9e311a6cd8211e5d1c/.github/workflows/main.yml#L84-L92). These are the commands that are automatically run when data is added to the KB repository.

### Converting the KB information to markdown

On the commandline, go to the root directory of the KB and run the relevant command for the file(s) you want to convert. Note that the conversion of the publications bibliography file to markdown assumes that the [pandoc program](https://pandoc.org/) is installed (a general document conversion program supporting many common formats such as LaTex, docx).

For the current way to run the conversion scripts, see their usage in the GitHub [actions workflow](https://github.com/IBEXImagingCommunity/ibex_imaging_knowledge_base/blob/26fc5ccc4a4bb36239cc7b9e311a6cd8211e5d1c/.github/workflows/main.yml#L173-L209).


### Creating supporting material

Creating supporting material can be done manually, writing markdown files or in a semi-automated fashion using the [csv2supporting](src/ibex_imaging_knowledge_base_utilities/csv_2_supporting.py) script:

```
csv2supporting reagents_batch.csv supporting_template_file.md.in output_directory --image_dir new_image_dir
```

1. reagents_batch.csv: csv [input file](tests/data/reagent_batch.csv). The file follows the reagent_resources.csv format with two additional columns titled "Publications" and "Notes". The "Notes" column is free text and can include markdown formatting. The "Publications" column contains the prefixes of markdown file names that contain the publication information. If multiple publications are associated with the same row, they are separated by a semicolon. These files are expected to be in the same directory as the csv input file (for example contents see [radtke_pnas.md](tests/data/radtke_pnas.md) and [radtke_nat_prot.md](tests/data/radtke_nat_prot.md)).  
&#x26A0; Note:
    * Leading and trailing whitespaces are removed from the csv (required by the KB).   
    * If images are provided as input to the script, optional `--image_dir` argument, their MD5 hashes are computed and added in the column titled MD5. If there was content in that column it is overwritten.
    * The input file is **overwritten** by the updated information.

2. supporting_template_file.md.in: [template file](tests/data/supporting_template.md.in) used to create supporting material files.

3. output_directory: path to directory where the supporting material files are written.
4. new_image_dir: optional argument, directory containing the images listed in the csv input file. These will be copied to the relevant output directories based on the path to the file listed in the csv. That is, if the file `all_images/image.jpg` is listed in the csv file as `FOXP3_eF570/image.jpg`, it will be copied to the `FOXP3_eF570` directory.
