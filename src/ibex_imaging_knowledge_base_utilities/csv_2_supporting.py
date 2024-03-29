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
import numpy as np
import pathlib
import argparse
import sys
from .argparse_types import file_path_endswith, dir_path

"""
This utility script facilitates batch creation of supporting material files from a comma-separated-value
file. The csv file follows the format of the knowledge-base reagent_resources.csv, with the following differences:
1. Each row is expected to contain a single ORCID, either in the Agree or Disagree column. # noqa W291
2. Two additional columns, "Publications" and "Notes". The "Notes" column is free text and can include markdown formatting.
The "Publications" column contains the prefixes of markdown files that contain the publication information. If multiple 
publications are associated with the same row, they are separated by a semicolon. These files are expected to be in the
same directory as the csv input file.

Example entry for "Publications" column:"radtke_pnas;radtke_nat_prot", corresponding markdown files are
radtke_pnas.md and radtke_nat_prot.md.

All supporting materials files follow the same structure which is defined by a template file. Generally speaking, 
template based file generation is best done using a dedicated tool such as jinja (https://jinja.palletsprojects.com/).
As our use case is very simple, string formatting is sufficient and we avoid dependency on an additional tool. 

The supporting material files are created with the expected names in the specific directory: target_conjugate/orcid.md.

NOTE: This script is intended for initial creation of supporting material files. If the file target_conjugate/orcid.md
already exists, DO NOT use the same directory for output. Instead, provide a temporary directory for output. You
then need to reconcile the newly created file(s) with the existing one(s). The numbering of the publications
and notes need to be updated when the new file content is added to the existing content and the configuration 
table needs to be updated too. This is a MANUAL step.
"""


def pubs2orcid_and_number(x, pub2number):
    pubnumbers = ", ".join(
        [
            pub2number[r.strip()] if r.strip() in pub2number else ""
            for r in x[0].split(";")
        ]
    )
    orcid_str = f"[{x[1]}](https://orcid.org/{x[1]})"
    return orcid_str + " [" + pubnumbers + "]" if pubnumbers else orcid_str


def replace_char_list(input_str, change_chars_list, replacement_char):
    """
    Given an input string replace all characters that are in the change_char_list to the replacement_char.
    """
    for c in change_chars_list:
        if c in input_str:
            input_str = input_str.replace(c, replacement_char)
    return input_str


def create_md_files(
    target_conjugate,
    all_df,
    template_str,
    publications_dict,
    supporting_material_root_dir,
):
    # List of characters that will be replaced with an underscore. Some of these are invalid
    # in file paths in windows/linux/osx and some don't work well when they appear in file
    # paths used by jekyll and GitHub to create a static page. We replace all of them with
    # an underscore.
    invalid_chars = [
        " ",
        "\t",
        "/",
        "\\",
        "{",
        "}",
        "[",
        "]",
        "(",
        ")",
        "<",
        ">",
        ":",
        "&",
    ]

    tc_rows = all_df[
        (all_df[target_conjugate.index[0]] == target_conjugate[0])
        & (all_df[target_conjugate.index[1]] == target_conjugate[1])
    ]
    orcids = [
        orcid
        for orcid in pd.concat(
            [tc_rows["Agree"], tc_rows["Disagree"]]
        ).drop_duplicates()
        if orcid != "" and orcid != "NA"
    ]
    data_path = supporting_material_root_dir / pathlib.Path(
        replace_char_list(
            input_str=f"{target_conjugate[0]}_{target_conjugate[1]}",
            change_chars_list=invalid_chars,
            replacement_char="_",
        )
    )
    data_path.mkdir(parents=True, exist_ok=True)
    result_file_paths = []

    for orcid in orcids:
        configurations_table = tc_rows[
            (tc_rows["Agree"] == orcid) | (tc_rows["Disagree"] == orcid)
        ]
        notes_list = [
            x for x in list(configurations_table["Notes"].unique()) if x.strip()
        ]
        notes_str = '<a name="notes"></a>\n' + "\n".join(
            [f"{i}. " + x for i, x in enumerate(notes_list, start=1)]
        )
        notes2number = dict(
            zip(notes_list, [f"[{i}](#notes)" for i in range(1, len(notes_list) + 1)])
        )
        configurations_table["Notes"].replace(notes2number, inplace=True)

        actual_publications = set(
            [
                r.strip()
                for publication in configurations_table["Publications"].to_list()
                for r in publication.split(";")
            ]
        )
        # We sort the resulting intersection set even though it is not necessary from a functionality standpoint.
        # It is necessary for obtaining consistent results for testing. Otherwise, the order can change
        # in repeated script runs.
        publications_list = sorted(
            actual_publications.intersection(publications_dict.keys())
        )
        publications_str = "\n".join(
            [
                f"{i}. " + publications_dict[publication]
                for i, publication in enumerate(publications_list, start=1)
            ]
        )
        publications2number = dict(
            zip(
                publications_list,
                [f"[{i}](#publications)" for i in range(1, len(publications_list) + 1)],
            )
        )
        configurations_table["Agree"] = configurations_table[
            ["Publications", "Agree"]
        ].apply(
            lambda x: pubs2orcid_and_number(x, pub2number=publications2number), axis=1
        )
        # add link to contributor's orcid site to the orcid
        configurations_table["Contributor"] = configurations_table["Contributor"].apply(
            lambda x: f"[{x}](https://orcid.org/{x})"
        )
        configurations_table = configurations_table.drop(["Publications"], axis=1)

        data_dict = {}
        data_dict["configurations_table"] = configurations_table.fillna("").to_markdown(
            index=False
        )
        data_dict["notes"] = notes_str
        data_dict["publications"] = (
            '<a name="publications"></a>\n' + publications_str
            if publications_str
            else ""
        )
        file_path = data_path / pathlib.Path(orcid + ".md")
        with open(file_path, "w") as fp:
            fp.write(template_str.format(**data_dict))
        result_file_paths.append(file_path)
    return result_file_paths


def single_orcid(x):
    num_orcids = 0
    for v in x:
        if v.strip() != "" and v != "NA":
            num_orcids += len(v.split(";"))
    return num_orcids == 1


def csv_2_supporting(csv_file, supporting_material_root_dir, supporting_template_file):
    orcid_column_names = ["Agree", "Disagree"]
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)

    # Check that there is only one ORCID per row.
    single_orcid_rows = df[orcid_column_names].apply(single_orcid, axis=1)
    if not single_orcid_rows.all():
        raise ValueError(
            f"Invalid file {csv_file}, following rows contain more than one ORCID:\n{list(single_orcid_rows[single_orcid_rows==False].index)}"  # noqa E501
        )

    # Check that dataframe does not contain preceding or trailing whitespace in entries
    df_stripped_whitespace = df.applymap(lambda x: x.strip(), na_action="ignore")
    diff_entries = np.where(
        (df != df_stripped_whitespace)
        & ~(df.isnull() & df_stripped_whitespace.isnull())
    )
    if diff_entries[0].size > 0:
        raise ValueError(
            "Dataframe entries contain preceding or trailing whitespace, please remove [row, col, value]:\n"
            + "\n".join(
                [
                    f"{row+2},{col+1}: {val}"
                    for row, col, val in zip(
                        diff_entries[0], diff_entries[1], df.values[diff_entries]
                    )
                ]
            )
        )
    with open(supporting_template_file) as fp:
        template_str = fp.read()
    # Get the publications strings
    possible_publications = [
        r.strip()
        for publication in df["Publications"].unique()
        for r in publication.split(";")
    ]
    publications = set(possible_publications)
    publications.discard(
        ""
    )  # get rid of blanks - error in the file, superfluous semicolon, but easy to deal with
    publications_dict = {}
    for publication in publications:
        try:
            with open(csv_file.parent / pathlib.Path(publication + ".md"), "r") as fp:
                publications_dict[publication] = fp.read()
        except FileNotFoundError:
            print(
                f"Warning: publications ({publication}.md) file doesn't exist, ignoring."
            )

    unique_target_conjugate = df[
        ["Target Name / Protein Biomarker", "Conjugate"]
    ].drop_duplicates()
    return unique_target_conjugate.apply(
        lambda x: create_md_files(
            x, df, template_str, publications_dict, supporting_material_root_dir
        ),
        axis=1,
    ).explode()  # explode takes series of lists and returns series of entries


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create supporting material files from a csv which has the same structure as the "
        + 'reagent_resources.csv and two additional columns "Publications" and "Notes".'
    )
    parser.add_argument("csv_file", type=lambda x: file_path_endswith(x, ".csv"))
    parser.add_argument(
        "supporting_template_file", type=lambda x: file_path_endswith(x, ".md.in")
    )
    parser.add_argument("supporting_material_root_dir", type=dir_path)
    args = parser.parse_args(argv)

    try:
        csv_2_supporting(
            args.csv_file,
            args.supporting_material_root_dir,
            args.supporting_template_file,
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
