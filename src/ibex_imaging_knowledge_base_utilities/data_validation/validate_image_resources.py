# =========================================================================
#
#  Copyright Ziv Yaniv
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# =========================================================================

import sys
import os
import json
import argparse
import pandas as pd
from ibex_imaging_knowledge_base_utilities.argparse_types import (
    file_path_endswith,
    dir_path,
)
from .utilities import validate_df, md5sum

"""
This script validates the contents of the image_resources.csv file. Do basic validation and ensure
that the image files listed in the image_resources exist and have the expected hash (are not corrupt).
"""


def validate_image_resources(
    csv_file_name, json_config_file_name, supporting_material_root_dir
):
    # List of files that may be in the supporting_materials directory
    # structure and that we should ignore when comparing to the list of
    # images found in the image_resources.csv.
    # The supporting materials directory is expected to contain markdown
    # files with file extension ".md" and all other files are assumed to
    # be images.
    FILES_IGNORE = [".DS_Store"]

    df = pd.read_csv(csv_file_name, dtype=str, keep_default_na=False)
    with open(json_config_file_name) as fp:
        configuration_dict = json.load(fp)

    # Perform basic validation using the given configuration file
    res = validate_df(df, **configuration_dict)
    # check if basic validation failed
    if res != 0:
        return res

    # Get series with full path to image files, assume there is no column titled file_full_path
    # in the original data frame
    df["file_full_path"] = df["file"].apply(
        lambda x: os.path.join(supporting_material_root_dir, x)
    )

    # Display long file paths when printing series which
    # contain problematic files, no ellipsis. Set the pandas width
    # in characters of a column in the repr of the cell content
    # to be unlimited.
    pd.set_option("display.max_colwidth", None)

    # Check files exist
    problematic_files = df["file_full_path"][
        df["file_full_path"].apply(lambda x: not os.path.isfile(x))
    ]
    if not problematic_files.empty:
        print(
            f"The following files do not exist: {problematic_files}",
            file=sys.stderr,
        )
        return 1

    # Get all the files where the hash recorded in the image resources file differs from the actual file hash
    problematic_files = df["file"][
        df[["file_full_path", "md5"]].apply(
            lambda x: md5sum(x.iloc[0]) != x.iloc[1],
            axis=1,
        )
    ]
    if not problematic_files.empty:
        print(
            f"The hash value for the following files does not match the actual value: {problematic_files}",
            file=sys.stderr,
        )
        return 1

    # Get all the non markdown file names and make sure that they match those in
    # the image_resources.csv. The supporting material subdirectory is expected
    # to contain markdown files and images, no other files.
    image_file_paths_from_supporting_material_dir = []
    for dir_name, subdir_names, file_names in os.walk(supporting_material_root_dir):
        for file in file_names:
            if not file.endswith(".md") and file not in FILES_IGNORE:
                image_file_paths_from_supporting_material_dir.append(
                    os.path.join(os.path.abspath(dir_name), file)
                )
    image_file_paths_from_supporting_material_dir = set(
        image_file_paths_from_supporting_material_dir
    )
    image_file_paths_from_csv = set(df["file_full_path"])
    superfluous_image_files = image_file_paths_from_supporting_material_dir.difference(
        image_file_paths_from_csv
    )
    if superfluous_image_files:
        print(
            "The following files are superfluous to those expected from the "
            + f"contents of the image_resources.csv file: {superfluous_image_files}"
        )
        return 1

    return 0


def main(argv=None):

    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Validation of image_resources.csv file."
    )
    parser.add_argument(
        "csv_file",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Image resources csv file to validate.",
    )
    parser.add_argument(
        "json_config_file",
        type=lambda x: file_path_endswith(x, ".json"),
        help="Configuration file for basic validation.",
    )
    parser.add_argument(
        "supporting_material_root_dir",
        type=dir_path,
        help="Path to supporting material root directory.",
    )

    args = parser.parse_args(argv)

    return validate_image_resources(
        args.csv_file, args.json_config_file, args.supporting_material_root_dir
    )


if __name__ == "__main__":
    sys.exit(main())
