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
from .argparse_types import file_path, file_path_endswith_md_in, dir_path


"""
This script converts the IBEX knowledge-base protocols.csv file to markdown.

This script is automatically run when modifications to the protocols.csv file are merged
into the main branch of the ibex_knowledge_base repository (see .github/workflows/data2md.yml).

Assumption: The protocols.csv file is valid. It conforms to the expected format
            (three columns titled: Title,URL,Details).
"""


def _description_2_md(description):
    num_words = 3  # number of words in the short description
    num_spaces = 0
    for i, c in enumerate(description):
        if c == " ":
            num_spaces = num_spaces + 1
            if num_spaces == num_words:
                break
    # Because the html code will go inside a markdown table and we are using kramdown,
    # default markdown renderer for jekyll, we need to wrap it with nomarkdown to tell kramdown to leave it
    # as is.
    return (
        "{::nomarkdown}"
        + f"<details ><summary>{description[0:i]}...</summary><p>{description}</p></details>"
        + "{:/}"
    )


def protocols_csv_to_md(template_file_path, csv_file_path, output_dir):
    """
    Convert the IBEX knowledge-base protocols csv file to markdown. Output is written to the given output
    directory using the given template file name. The template_file_path file is expected
    to contain the string {protocols_table} which is replaced with the contents of the actual table.
    """
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(csv_file_path, dtype=str, keep_default_na=False)
    # Add the hyperlink to the title column, using the string "detailed protocol"
    df["Title"] = df[["Title", "URL"]].apply(
        lambda x: f"{x[0]} [[detailed protocol]({x[1]})].", axis=1
    )
    # Convert the detailed description to markdown, with the details html markup (accordion view).
    df["Details"] = df["Details"].apply(_description_2_md)

    with open(template_file_path, "r") as fp:
        input_md_str = fp.read()
    with open(output_dir / template_file_path.stem, "w") as fp:
        fp.write(
            input_md_str.format(
                protocols_table=df[["Title", "Details"]].to_markdown(
                    index=False, colalign=["left", "left"]
                )
            )
        )


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Convert knowledge-base protocols file from csv to md and link using URL."
    )
    parser.add_argument(
        "md_template_file",
        type=file_path_endswith_md_in,
        help='Path to template markdown file which contains the string "{protocol_table}".',
    )
    parser.add_argument(
        "csv_file", type=file_path, help="Path to the protocols.csv file."
    )
    parser.add_argument(
        "output_dir",
        type=dir_path,
        help="Path to the output directory (the protocols.md file is written to this directory).",
    )
    args = parser.parse_args(argv)

    try:
        return protocols_csv_to_md(
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
