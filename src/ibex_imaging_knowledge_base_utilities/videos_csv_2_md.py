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
import argparse
import sys
from .argparse_types import file_path_endswith, dir_path
from datetime import date
from .utilities import _description_2_md, _dataframe_2_md

"""
This script converts the IBEX knowledge-base videos.csv file to markdown.

The script is automatically run when modifications to the videos.csv file are merged
into the main branch of the ibex_knowledge_base repository (see .github/workflows/data2md.yml).

Assumption: The videos.csv file is valid. It conforms to the expected format
            (includes columns titled: Title,URL,Details,Category,Year,Month,Day).
            Category entries are either "general" or "tutorial".
"""


def videos_csv_to_md(template_file_path, csv_file_path, output_dir):
    """
    Convert the IBEX knowledge-base videos csv file to markdown. Output is written to the given output
    directory using the given template file name. The template_file_path file is expected
    to contain the strings {general_table} and {tutorial_table} which are replaced with the contents
    of the actual tables.
    """
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(csv_file_path, dtype=str, keep_default_na=False)
    # Add the hyperlink to the title column, using the string "detailed protocol"
    df["Title"] = df[["Title", "URL"]].apply(
        lambda x: f"{x[0]} [[video]({x[1]})].", axis=1
    )
    # Convert the detailed description to markdown, with the details html markup (accordion view).
    df["Details"] = df["Details"].apply(_description_2_md)

    # Combine the separate Year, Month, Day columns into a date column. Conversion to int
    # gets rid of any leading zeros (if someone used 04 and not 4 to denote april).
    # Sort in reverse chronological order.
    df["Date"] = df[["Year", "Month", "Day"]].apply(
        lambda x: date(int(x[0]), int(x[1]), int(x[2])), axis=1
    )
    df.sort_values(by=["Date"], ascending=False, inplace=True)
    with open(template_file_path, "r") as fp:
        input_md_str = fp.read()
    with open(output_dir / template_file_path.stem, "w") as fp:
        fp.write(
            input_md_str.format(
                general_table=_dataframe_2_md(
                    df[df["Category"] == "general"][["Title", "Details"]],
                    index=False,
                    colalign=["left", "left"],
                ),
                tutorial_table=_dataframe_2_md(
                    df[df["Category"] == "tutorial"][["Title", "Details"]],
                    index=False,
                    colalign=["left", "left"],
                ),
            )
        )


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Convert knowledge-base videos file from csv to md and link using URL."
    )
    parser.add_argument(
        "md_template_file",
        type=lambda x: file_path_endswith(x, ".md.in"),
        help='Path to template markdown file which contains the strings "{general_table}" and "{tutorial_table}".',
    )
    parser.add_argument(
        "csv_file",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Path to the video.csv file.",
    )
    parser.add_argument(
        "output_dir",
        type=dir_path,
        help="Path to the output directory (the videos.md file is written to this directory).",
    )
    args = parser.parse_args(argv)

    try:
        return videos_csv_to_md(
            template_file_path=args.md_template_file,
            csv_file_path=args.csv_file,
            output_dir=args.output_dir,
        )
    except Exception as e:
        print(
            f"{e}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
