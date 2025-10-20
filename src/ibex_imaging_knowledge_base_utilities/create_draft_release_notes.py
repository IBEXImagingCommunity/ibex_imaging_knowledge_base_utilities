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

import argparse
import json
import bibtexparser
import pandas as pd
import subprocess
import sys

"""
This utility script creates draft release notes highlighting the differences between
two tagged versions of the IBEX Imaging Community Knowledge-Base (KB). The script compares
the content of the KB data files for the two tags and creates a file that is used as a starting
point for the official release notes on GitHub. See the KB GitHub actions create_draft_release.yml
for usage in the process of creating a new release.
"""


def read_reagent_resources_csv(reagent_file):
    # read reagent resources csv and split the multi-value columns into lists,
    # value separator is ";"
    # entry may also be "NA" or empty string.
    df = pd.read_csv(reagent_file, dtype=str, keep_default_na=False)
    df["Agree"] = df["Agree"].apply(
        lambda x: [v.strip() for v in x.split(";") if v.strip() not in ["", "NA"]]
    )
    df["Disagree"] = df["Disagree"].apply(
        lambda x: [v.strip() for v in x.split(";") if v.strip() not in ["", "NA"]]
    )
    df["MD5"] = df["MD5"].apply(
        lambda x: [v.strip() for v in x.split(";") if v.strip() not in ["", "NA"]]
    )
    return df


def create_draft_release_notes(old_tag, new_tag, output_file):
    csv_txt = [
        ("data/protocols.csv", "Protocols: "),
        ("data/videos.csv", "Videos: "),
        ("data/datasets.csv", "Datasets: "),
        ("data/software.csv", "Software tools: "),
    ]
    reagent_file = "data/reagent_resources.csv"
    zenodo_file = ".zenodo.json"
    publications_file = "data/publications.bib"

    release_notes_str = (
        "We are proud to announce a new release of the IBEX Imaging "
        "Community Knowledge-Base!\n\n"
        "All changes and updates have been integrated into the "
        "[official Knowledge-Base web-site]"
        "(https://ibeximagingcommunity.github.io/ibex_imaging_knowledge_base).\n\n"
        "This release includes the following updates compared to the "
        "previous release:\n"
    )

    try:
        # Read data from old tag
        subprocess.run(["git", "checkout", old_tag], check=True, capture_output=True)
        old_dfs = [
            pd.read_csv(csv_file, dtype=str, keep_default_na=False)
            for csv_file, _ in csv_txt
        ]
        old_reagent_resources_df = read_reagent_resources_csv(reagent_file)
        with open(zenodo_file) as fp:
            old_zenodo_dict = json.load(fp)
        with open(publications_file) as biblatex_file:
            old_bib_database = bibtexparser.load(biblatex_file)

        # Read data from new tag
        subprocess.run(["git", "checkout", new_tag], check=True, capture_output=True)
        new_dfs = [
            pd.read_csv(csv_file, dtype=str, keep_default_na=False)
            for csv_file, _ in csv_txt
        ]
        new_reagent_resources_df = read_reagent_resources_csv(reagent_file)
        with open(zenodo_file) as fp:
            new_zenodo_dict = json.load(fp)
        with open(publications_file) as biblatex_file:
            new_bib_database = bibtexparser.load(biblatex_file)

        # Compute the number of new reagent validations. Only consider the
        # columns that define the reagent validation configuration.
        cols_to_ignore = [
            "Agree",
            "Disagree",
            "Contributor",
            "Image Files",
            "Captions",
            "MD5",
        ]
        cols_to_use = [
            col
            for col in new_reagent_resources_df.columns.to_list()
            if col not in cols_to_ignore
        ]
        # Outer merge of the new and old reagent resources dataframes using the
        # subset of columns that define a reagent validation configuration. The
        # indicator column _merge will show whether the row is present in both
        # dataframes ("both"), or only in one of them ("left_only" or "right_only").
        # The cols_to_ignore are copied as is and the column headers are suffixed
        # with _new and _old.
        comparison_df = new_reagent_resources_df.merge(
            old_reagent_resources_df,
            on=cols_to_use,
            suffixes=("_new", "_old"),
            indicator=True,
            how="outer",
        )
        differences = comparison_df[comparison_df["_merge"] != "both"]
        reagent_additions = sum(differences["_merge"] == "left_only")
        reagent_deletions = sum(differences["_merge"] == "right_only")
        # Compute the number of replicated reagent validations.
        common_rows = comparison_df["_merge"] == "both"
        # count number of new replications for configurations that existed
        # in the old release
        replication_old_configurations = (
            comparison_df[common_rows]["Agree_new"].apply(len)
            + comparison_df[common_rows]["Disagree_new"].apply(len)
            - comparison_df[common_rows]["Agree_old"].apply(len)
            - comparison_df[common_rows]["Disagree_old"].apply(len)
        ).sum()
        new_release_rows = comparison_df["_merge"] == "left_only"
        # count number of new replications in new configurations, subtract 1
        # because the first instance is not a replication
        replication_new_configurations = (
            comparison_df[new_release_rows]["Agree_new"].apply(len)
            + comparison_df[new_release_rows]["Disagree_new"].apply(len)
            - 1
        ).sum()
        total_replications = (
            replication_old_configurations + replication_new_configurations
        )
        if reagent_additions > 0 or reagent_deletions > 0 or total_replications > 0:
            release_notes_str += "* Reagent validation results: "
            all_reagent_strs = []
            if reagent_additions > 0:
                all_reagent_strs.append(f"{reagent_additions} added")
            if reagent_deletions > 0:
                all_reagent_strs.append(f"{reagent_deletions} removed")
            if total_replications > 0:
                all_reagent_strs.append(f"{total_replications} replicated")
            release_notes_str += ", ".join(all_reagent_strs) + "\n"
        # Compute reagent validation image differences
        # Collect the MD5 hashes from all image lists into a set
        # for old and new and compare the sets.
        old_image_list = []
        for img_list in old_reagent_resources_df["MD5"]:
            old_image_list.extend(img_list)
        old_images = set(old_image_list)
        new_image_list = []
        for img_list in new_reagent_resources_df["MD5"]:
            new_image_list.extend(img_list)
        new_images = set(new_image_list)
        added_images = new_images - old_images
        removed_images = old_images - new_images
        if added_images or removed_images:
            release_notes_str += "* Images supporting reagent validation results: "
            all_image_strs = []
            if added_images:
                all_image_strs.append(f"{len(added_images)} added")
            if removed_images:
                all_image_strs.append(f"{len(removed_images)} removed")
            release_notes_str += ", ".join(all_image_strs) + "\n"

        # Compute differences between new and old csv files
        for old_df, (_, header), new_df in zip(old_dfs, csv_txt, new_dfs):
            old_count = len(old_df)
            new_count = len(new_df)
            if new_count > old_count:
                release_notes_str += f"* {header}: {new_count - old_count} added\n"
            elif new_count < old_count:
                release_notes_str += f"* {header}: {old_count - new_count} removed\n"
        # Compute differences between new and old publication files, all bibtex entries
        # have a doi field (required by the knowledge-base).
        old_dois = set([bib_entry["doi"] for bib_entry in old_bib_database.entries])
        new_dois = set([bib_entry["doi"] for bib_entry in new_bib_database.entries])
        new_publications = new_dois - old_dois
        removed_publications = old_dois - new_dois
        if new_publications or removed_publications:
            release_notes_str += "* Publications: "
            all_publication_strs = []
            if new_publications:
                all_publication_strs.append(f"{len(new_publications)} added")
            if removed_publications:
                all_publication_strs.append(f"{len(removed_publications)} removed")
            release_notes_str += ", ".join(all_publication_strs) + "\n"

        # Get ORCIDS for first time contributors to this release
        previous_contributors = set([c["orcid"] for c in old_zenodo_dict["creators"]])
        current_contributors = set([c["orcid"] for c in new_zenodo_dict["creators"]])
        first_time_contributors = current_contributors - previous_contributors
        if first_time_contributors:
            release_notes_str += (
                "## Congratulations\n"
                "Congratulations and thank you to everyone who contributed to this release.\n"
                "We would like to especially recognize the following new contributors "
                "(identified by their unique Open Researcher and Contributor ID):\n"
            )
            release_notes_str += ", ".join(
                [
                    f"[{orcid}](https://orcid.org/{orcid})"
                    for orcid in first_time_contributors
                ]
            )
            release_notes_str += "\n"

        output_file.write(release_notes_str)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git operation failed: {e}")
    except Exception as e:
        raise Exception(f"Error reading files: {e}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Create draft release notes highlighting differences between two "
        "tagged KB versions. Script must be run from the directory containing the git repository."
    )
    parser.add_argument(
        "old_release_tag",
        type=str,
        help="Git tag for the old release.",
    )
    parser.add_argument(
        "new_release_tag",
        type=str,
        help="Git tag for the new release.",
    )
    parser.add_argument(
        "output_file",
        type=argparse.FileType("w"),
        help="File to write the draft release notes to.",
    )
    args = parser.parse_args(argv)

    try:
        create_draft_release_notes(
            args.old_release_tag,
            args.new_release_tag,
            args.output_file,
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
