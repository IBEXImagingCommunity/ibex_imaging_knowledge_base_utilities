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

import pandas as pd
import sys
import argparse
import json
from ibex_imaging_knowledge_base_utilities.argparse_types import (
    csv_path,
    file_path_endswith,
)
from .validation_utilities import validate_df

"""
This script validates the contents of a csv file using the settings specified in
a JSON configuration file. Validate that there is no leading or trailing whitespace.

Possible JSON configuration settings:
data_required_column_names - Columns that cannot contain empty entries.
data_optional_column_names - Columns that may contain empty entries. Together with the data_required_column_names these
list all of the column names.
unique_entry_columns - columns that cannot contain duplicates.
url_columns - columns containing a single url (check for existence, no 404)
multi_url_columns - columns containing multiple urls per column with semicolon separating between them.
doi_columns - columns containing a single doi (URL is constructed as https://doi.org/{doi}).
Check for existence, no 404.
multi_doi_columns - columns containing multiple dois with semicolon separating between them
(URL is constructed as https://doi.org/{doi}). Check for existence, no 404.
column_is_in - columns containing a single entry that has to be in the specified set of values.
multi_value_column_is_in - columns containing multiple entries separated by semicolons that have to be in the
specified set of values.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description="Basic csv file content validation.")
    parser.add_argument(
        "csv_file",
        type=csv_path,
        help="Input csv file to validate.",
    )
    parser.add_argument(
        "json_config_file",
        type=lambda x: file_path_endswith(x, ".json"),
        help="Configuration file.",
    )

    args = parser.parse_args(argv)

    df = pd.read_csv(args.csv_file, dtype=str, keep_default_na=False)
    with open(args.json_config_file) as fp:
        configuration_dict = json.load(fp)
    return validate_df(df, **configuration_dict)


if __name__ == "__main__":
    sys.exit(main())
