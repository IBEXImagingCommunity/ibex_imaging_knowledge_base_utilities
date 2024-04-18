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
from ibex_imaging_knowledge_base_utilities.argparse_types import file_path_endswith

"""
This script validates the contents of the fluorescent_probes.csv file.
1. Check that there are no duplicate probes.
2. Check that there are no leading or trailing whitespaces in any of the cells.
"""


def validate_fluorescent_probes_data(probes_filename):
    # shift the index number which is zero based and ignores the header so that the printed
    # row numbers match what you would see in a spreadsheet editor (e.g. excell, google docs)
    shift_index = 2

    df = pd.read_csv(probes_filename, dtype=str, keep_default_na=False)
    # check for leading/trailing whitespace in dataframe entries
    leading_trailing = df.applymap(lambda x: x != x.strip())
    leading_trailing_rows = df.index[leading_trailing.any(axis=1)].to_list()
    if leading_trailing_rows:
        print(
            "The following rows have entries with leading/trailing whitespace (please remove): "
            + f"{[str(i + shift_index) for i in leading_trailing_rows]}.",
            file=sys.stderr,
        )
        return 1
    # get duplicated probe names, if any
    duplicated_entries = df["Fluorescent Probe"][df["Fluorescent Probe"].duplicated()]
    if duplicated_entries.empty:
        return 0
    else:
        # duplicated_entries can contain the same entry multiple times, we want it as a set
        duplicate_set = set(duplicated_entries)
        print(
            "Duplicate fluorescent probes not allowed: "
            + ", ".join(
                [
                    f"{probe} rows {[i+shift_index for i in df.index[df['Fluorescent Probe']==probe].to_list()]}"
                    for probe in duplicate_set
                ]
            )
            + ".",
            file=sys.stderr,
        )
        return 1


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Validate fluorescent_probes.csv file content."
    )
    parser.add_argument(
        "probes_file",
        type=lambda x: file_path_endswith(x, ".csv"),
        help='A csv file with a column titled "Fluorescent Probe"',
    )
    args = parser.parse_args(argv)

    return validate_fluorescent_probes_data(args.zenodo_json)


if __name__ == "__main__":
    sys.exit(main())
