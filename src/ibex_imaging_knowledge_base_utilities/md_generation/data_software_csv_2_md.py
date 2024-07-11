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
from ibex_imaging_knowledge_base_utilities.argparse_types import (
    file_path_endswith,
    dir_path,
)
from .utilities import _description_2_md, _dataframe_2_md

"""
This script converts the IBEX knowledge-base datasets.csv and software.csv files to markdown.

This script is automatically run when modifications to the datasets.csv or software.csv files are merged
into the main branch of the ibex_knowledge_base repository (see .github/workflows/data2md.yml).

Assumption: The csv files are valid. They conform to the expected column titles, column order does not matter.
            (datasets file includes columns titled: Title,Details,Year,URL,Associated Publication DOIs,License).
            (software file includes columns titled: Title,Details,Year,URL,Repository,Language,License,
             Associated Publication DOIs).
"""


def dataset_2_title_md_str(dataset_info):
    # title, download url and license always have content but a dataset may not have a publication associated
    # with it.
    title_md_str = f"{dataset_info['Title']} [[download]({dataset_info['URL']}), license: {dataset_info['License']}"
    if not dataset_info["Associated Publication DOIs"]:
        title_md_str += "]"
    else:
        publication_dois = [
            p.strip()
            for p in dataset_info["Associated Publication DOIs"].split(";")
            if p.strip() != ""
        ]
        title_md_str += (
            ", associated publication DOIs: "
            + ", ".join([f"[{p}](https://doi.org/{p})" for p in publication_dois])
            + "]"
        )
    return title_md_str


def software_2_title_md_str(software_info):
    # title, download url and license always have content but software may not have a publication associated and the
    # programming language and repository may not be known
    title_md_str = f"{software_info['Title']} [[download]({software_info['URL']}), license: {software_info['License']}"
    if software_info["Language"]:
        title_md_str += f", language: {software_info['Language']}"
    if software_info["Repository"]:
        title_md_str += f", [repository]({software_info['Repository']})"
    if not software_info["Associated Publication DOIs"]:
        title_md_str += "]"
    else:
        publication_dois = [
            p.strip()
            for p in software_info["Associated Publication DOIs"].split(";")
            if p.strip() != ""
        ]
        title_md_str += (
            ", associated publication DOIs: "
            + ", ".join([f"[{p}](https://doi.org/{p})" for p in publication_dois])
            + "]"
        )
    return title_md_str


def data_software_csv_to_md(
    template_file_path, data_csv_file_path, software_csv_file_path, output_dir
):
    """
    Convert the IBEX knowledge-base datasets and software csv files to markdown. Output is written
    to the given output directory using the given template file name. The template_file_path file is
    expected to contain the strings {data_table} and {software_table} which are replaced with the
    contents of the actual tables.
    """
    # Process the datasets csv:
    # Read the information, keep entries that are "NA", don't convert to nan and sort according
    # to year in reverse chronological order.
    df = pd.read_csv(data_csv_file_path, dtype=str, keep_default_na=False)
    df = df.sort_values(by=["Year"], ascending=False)

    # Create the title portion of the datasets table
    df["Title"] = df[["Title", "URL", "Associated Publication DOIs", "License"]].apply(
        lambda x: dataset_2_title_md_str(x), axis=1
    )
    # Convert the detailed description to markdown, with the details html markup (accordion view).
    df["Details"] = df["Details"].apply(_description_2_md)
    dataset_table = df[["Title", "Details"]]

    # Process the software csv:
    # Read the information, keep entries that are "NA", don't convert to nan and sort according
    # to year in reverse chronological order.
    df = pd.read_csv(software_csv_file_path, dtype=str, keep_default_na=False)
    df = df.sort_values(by=["Year"], ascending=False)

    # Create the title portion of the datasets table
    df["Title"] = df[
        [
            "Title",
            "URL",
            "Repository",
            "Language",
            "Associated Publication DOIs",
            "License",
        ]
    ].apply(lambda x: software_2_title_md_str(x), axis=1)
    # Convert the detailed description to markdown, with the details html markup (accordion view).
    df["Details"] = df["Details"].apply(_description_2_md)
    software_table = df[["Title", "Details"]]

    with open(template_file_path, "r") as fp:
        input_md_str = fp.read()
    with open(output_dir / template_file_path.stem, "w") as fp:
        fp.write(
            input_md_str.format(
                data_table=_dataframe_2_md(
                    dataset_table, index=False, colalign=["left", "left"]
                ),
                software_table=_dataframe_2_md(
                    software_table, index=False, colalign=["left", "left"]
                ),
            )
        )


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Convert knowledge-base datasets and software file information from csv to md and "
        + "combine with the template file."
    )
    parser.add_argument(
        "md_template_file",
        type=lambda x: file_path_endswith(x, ".md.in"),
        help='Path to template markdown file which contains the strings "{data_table}" and "{software_table}".',
    )
    parser.add_argument(
        "data_csv_file",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Path to the datasets.csv file.",
    )
    parser.add_argument(
        "software_csv_file",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Path to the software.csv file.",
    )
    parser.add_argument(
        "output_dir",
        type=dir_path,
        help="Path to the output directory (the data_and_software.md file is written to this directory).",
    )
    args = parser.parse_args(argv)

    try:
        return data_software_csv_to_md(
            template_file_path=args.md_template_file,
            data_csv_file_path=args.data_csv_file,
            software_csv_file_path=args.software_csv_file,
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
