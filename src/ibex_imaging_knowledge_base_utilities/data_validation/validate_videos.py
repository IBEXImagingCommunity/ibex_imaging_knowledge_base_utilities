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
import json
import argparse
import pandas as pd
from ibex_imaging_knowledge_base_utilities.argparse_types import file_path_endswith
from .utilities import validate_df

"""
This script validates the contents of the videos.csv file. Do basic validation and ensure that
the contributors are all listed in the .zenodo.json file.
"""


def validate_videos(csv_file_name, json_config_file_name, zenodo_json_file_name):
    df = pd.read_csv(csv_file_name, dtype=str, keep_default_na=False)
    with open(json_config_file_name) as fp:
        configuration_dict = json.load(fp)

    # Get the list of contributor ORCIDs from the .zenodo.json file and
    # enforce that contributors listed in the videos files are in the zenodo
    # file. Assume the zenodo file has been validated, so ORCID information is
    # available.
    with open(zenodo_json_file_name) as fp:
        zenodo_dict = json.load(fp)
    orcids = [data["orcid"].strip() for data in zenodo_dict["creators"]]

    if "multi_value_column_is_in" in configuration_dict:
        configuration_dict["multi_value_column_is_in"]["Contributors"] = orcids
    else:
        configuration_dict["multi_value_column_is_in"] = {"Contributors": orcids}
    return validate_df(df, **configuration_dict)


def main(argv=None):

    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Validation of videos.csv file.")
    parser.add_argument(
        "csv_file",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Video csv file to validate.",
    )
    parser.add_argument(
        "json_config_file",
        type=lambda x: file_path_endswith(x, ".json"),
        help="Configuration file for basic validation.",
    )
    parser.add_argument(
        "zenodo_json_file",
        type=lambda x: file_path_endswith(x, ".json"),
        help=".zenodo.json file which contains the ORCIDs of all contributors.",
    )

    args = parser.parse_args(argv)
    return validate_videos(args.csv_file, args.json_config_file, args.zenodo_json_file)


if __name__ == "__main__":
    sys.exit(main())
