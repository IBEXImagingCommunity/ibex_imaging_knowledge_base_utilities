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
import pandas as pd
import argparse
from ibex_imaging_knowledge_base_utilities.argparse_types import (
    file_path_endswith,
    dir_path,
)
from .utilities import _dataframe_2_md


def dict_glossary_to_md(
    template_file_path, data_dict_file_path, glossary_file_path, output_dir
):
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    dict_df = pd.read_csv(data_dict_file_path, encoding="ISO-8859-1")
    glossary_df = pd.read_csv(glossary_file_path, encoding="ISO-8859-1")
    with open(template_file_path, "r") as fp:
        input_md_str = fp.read()
    with open(output_dir / template_file_path.stem, "w") as fp:
        fp.write(
            input_md_str.replace(
                "{reagent_metadata_table}",
                _dataframe_2_md(
                    dict_df, index=False, colalign=["left"] * len(dict_df.columns)
                ),
            ).replace(
                "{glossary_table}",
                _dataframe_2_md(
                    glossary_df,
                    index=False,
                    colalign=["left"] * len(glossary_df.columns),
                ),
            )
        )


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Insert data dictionary and glossary from csv files into the contrib instructions markdown."
    )
    parser.add_argument(
        "md_template_file",
        type=lambda x: file_path_endswith(x, ".md.in"),
        help='Path to template markdown file which contains the strings "{reagent_metadata_table}" and "{glossary_table}".',  # noqa E501
    )
    parser.add_argument(
        "data_dictionary",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Path to the reagent data dictionary csv file.",
    )
    parser.add_argument(
        "glossary",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Path to the glossary csv file.",
    )
    parser.add_argument(
        "output_dir",
        type=dir_path,
        help="Path to the output directory (the output markdown file is written to this directory).",
    )
    args = parser.parse_args(argv)

    try:
        return dict_glossary_to_md(
            template_file_path=args.md_template_file,
            data_dict_file_path=args.data_dictionary,
            glossary_file_path=args.glossary,
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
