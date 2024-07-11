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

"""
This script computes statistics from the reagent_resources.csv file and injects them into the input markdown file.
The statistics include:
  * number_of_contributors
  * number_of_recommended_antibodies
  * number_of_not_recommended_antibodies
  * number_of_fluorophores
  * number_of_tissues

The input markdown file includes variables with the names above which are replaced with the computed values (e.g.
{number_of_contributors}). Additionally it includes the variable {do_not_edit_message} which warns against directly
editing the resulting markdown file, edit the input markdown file instead.

This script is automatically run when modifications to the reagent_resources.csv or the index.md.in file are merged
into the main branch of the ibex_knowledge_base repository (see .github/workflows/data2md.yml).

Assumption: The reagent_resources.csv file is valid. It conforms to the expected format (empty entries denoted
by the string "NA").
"""


def update_index_stats(md_template_file, input_csv, output_dir):
    with open(md_template_file, "r") as fp:
        input_md_str = fp.read()
    stats_dictionary = compute_stats_dictionary(input_csv)
    output_str = input_md_str
    for k, v in stats_dictionary.items():
        output_str = output_str.replace("{" + k + "}", str(v))
    with open(output_dir / md_template_file.stem, "w") as fp:
        fp.write(output_str)


def entry2list(entry):
    """
    Replace a string entry with a If the entry is
    nan a null string or "NA" return an empty list.
    Otherwise, the string is split using the semicolon as
    the separator character, leading and trailing whitespace is
    removed from the substrings.
    """
    if pd.isna(entry) or entry.strip() == "":
        return set()
    else:
        res_list = [v.strip() for v in entry.split(";") if v.strip() != ""]
        res = set(res_list)
        if len(res_list) != len(res):
            raise ValueError(f"entry with duplicate values - {entry}")
        return res


def compute_stats_dictionary(input_csv):
    stats_dict = {}
    df = pd.read_csv(input_csv, dtype=str, keep_default_na=False)
    # Compute number of contributors, both original and folks that
    # replicated the validation and either agree or disagree with the
    # original contribution. The original contributor added the ORCID
    # to the "Agree" column and the "Contributor" column, so no need to
    # look at the "Contributor" column.
    all_contributions = df["Agree"].tolist() + df["Disagree"].tolist()
    all_unique_contributors = set(
        [
            v.strip()
            for x in all_contributions
            for v in x.split(";")
            if v.strip() != "NA"
        ]
    )
    stats_dict["number_of_contributors"] = len(all_unique_contributors)
    stats_dict["number_of_validated_reagents"] = len(df)
    stats_dict["number_of_fluorescent_probes"] = len(
        df["Conjugate"][
            ~df["Conjugate"].isin(
                [
                    "NA",
                    "Unconjugated",
                    "Biotin",
                    "HRP",
                    "UT014",
                    "UT015",
                    "UT016",
                    "UT019",
                ]
            )
        ].unique()
    )
    stats_dict["number_of_tissues"] = len(
        df[["Target Species", "Target Tissue", "Tissue State"]].drop_duplicates()
    )
    return stats_dict


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Update stats in the index.md file.")
    parser.add_argument(
        "md_template_file",
        type=lambda x: file_path_endswith(x, ".md.in"),
        help="Path to template markdown file which contains the following strings:\n\t"
        + "\n\t".join(
            [
                "{number_of_contributors}",
                "{number_of_recommended_antibodies}",
                "{number_of_not_recommended_antibodies}",
                "{number_of_fluorophores}",
                "{number_of_tissues}",
            ]
        ),
    )
    parser.add_argument(
        "input_csv",
        type=lambda x: file_path_endswith(x, ".csv"),
        help="Path to the reagent_resources.csv file.",
    )
    parser.add_argument(
        "output_dir",
        type=dir_path,
        help="Path to the output directory (the output markdown file is written to this directory).",
    )
    args = parser.parse_args(argv)

    try:
        update_index_stats(args.md_template_file, args.input_csv, args.output_dir)
    except Exception as e:
        print(
            f"{e}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
