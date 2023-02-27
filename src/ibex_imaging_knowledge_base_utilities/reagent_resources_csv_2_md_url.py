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
import pathlib
from .argparse_types import file_path, file_path_endswith_md_in, dir_path
import requests
from itertools import chain

"""
This script converts the IBEX knowledge-base reagent_resources.csv file to markdown and
adds hyperlinks between the ORCID entries and the supporting material files.
The links cannot exist in the original csv file, or in a simple way in an excel
spreadsheet because we use multiple links in the same table cell (Agree/Disagree),
functionality excel does not support in a simple manner.

On the other hand, using markdown for the reagent-resources table does not address all our
needs either, sorting and filtering are not possible or are very cumbersome. We
therefore use the csv file as the official reagent-resources, and it is what
contributors edit.

Additionally, the script adds hyperlinks between the entries in the "UniProt Accession Number"
column and their respective entries in the Universal Protein Resource Knowledge-Base
(https://www.uniprot.org/uniprotkb), and between the vendor names and their web-sites based on a user
provided csv file mapping between the names and URLs. By default the script attempts to get the relevant
web page to confirm existence. If the response is not as expected a warning is printed, but the URL is still
used. We take this approach because some sites are set up to prevent robot scraping and denial of service
attacks making it more complex to check if the URL exists.

The resulting markdown file "reagent_resources.md" is written to the parent directory of the supporting
material.

This script is automatically run when modifications to the reagent_resources.csv file are merged
into the main branch of the ibex_knowledge_base repository (see .github/workflows/main.yml).

Assumption: The reagent_resources.csv file is valid. It conforms to the expected format (empty entries denoted
by the string "NA").
"""


def short_circuit_requests_get(url, params=None, **kwargs):
    res = requests.Response()
    # It's always a success
    res.status_code = 200
    return res


request_timeout = 1
request_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
}


def csv_to_md_str_dict(csv_file_path):
    df = pd.read_csv(csv_file_path, dtype=str, keep_default_na=False)
    data_dict = dict(zip(df["Vendor"], df["URL"]))
    md_str_dict = {}
    for raw_text, url_target in data_dict.items():
        try:
            res = requests.get(
                url_target,
                timeout=request_timeout,
                headers=request_headers,
                allow_redirects=True,
            )
            # HTTP 200 status code for success
            if res.status_code == 200:
                md_str_dict[raw_text] = f"[{raw_text}]({url_target})"
            else:
                print(
                    "Warning: problem with {raw_text} URL ({url_target}), check link..."
                )
                md_str_dict[raw_text] = f"[{raw_text}]({url_target})"
        except requests.exceptions.RequestException:
            print(f"Warning: problem with {raw_text} URL ({url_target}), check link...")
            md_str_dict[raw_text] = f"[{raw_text}]({url_target})"
    return md_str_dict


def replace_char_list(input_str, change_chars_list, replacement_char):
    for c in change_chars_list:
        if c in input_str:
            input_str = input_str.replace(c, replacement_char)
    return input_str


def data_to_md_str(data, supporting_material_root_dir):
    """
    The data parameter is a series with three entries:
    1. String with one or more ORCIDs separated by semicolon, or NA.
    2. "Target Name / Protein Biomarker"
    3. "Conjugate"
    Together these define the path to the supporting material file:
    "Target Name / Protein Biomarker"_"Conjugate"/ORCID.md
    """
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
    if data[0].strip() == "NA":
        urls_str = "NA"
    else:
        urls_str = ""
        txt = [v.strip() for v in data[0].split(";") if v.strip() != ""]
        for v in txt[0:-1]:
            # Replace spaces, slashes and brackets with underscores assume that the
            # file exists, data validation happens prior to conversion of data to markdown.
            tc_subpath = replace_char_list(
                input_str=f"{data[1]}_{data[2]}",
                change_chars_list=invalid_chars,
                replacement_char="_",
            )
            urls_str += f"[{v}]({supporting_material_root_dir}/{tc_subpath}/{v}.md), "
        tc_subpath = replace_char_list(
            input_str=f"{data[1]}_{data[2]}",
            change_chars_list=invalid_chars,
            replacement_char="_",
        )
        urls_str += (
            f"[{txt[-1]}]({supporting_material_root_dir}/{tc_subpath}/{txt[-1]}.md)"
        )
    return urls_str


def uniprot_to_md_str(uniprot):
    if uniprot == "NA":
        return "NA"
    try:
        # See https://www.uniprot.org/help/api_retrieve_entries
        # We use the rest API url because trying to directly connect
        # to the fixed url always succeeds, return code 200,
        # even when it is an error, the 404 page is shown.
        rest_url_str = f"https://rest.uniprot.org/uniprotkb/{uniprot}.txt"
        res = requests.get(
            rest_url_str,
            timeout=request_timeout,
            headers=request_headers,
            allow_redirects=True,
        )
        # HTTP 200 status code for success
        if res.status_code == 200:
            # Linking to uniprot entries
            return f"[{uniprot}](https://www.uniprot.org/uniprotkb/{uniprot})"
        else:
            return uniprot
    except requests.exceptions.RequestException:
        print(
            f"Warning: problem with {uniprot} URL (https://www.uniprot.org/uniprotkb/{uniprot}), check link..."
        )
        return f"[{uniprot}](https://www.uniprot.org/uniprotkb/{uniprot})"


def uniprots_to_md(uniprots_str, uniprot_md_str):
    uniprots_list = [v.strip() for v in uniprots_str.split(";") if v.strip() != ""]
    urls_str = ""
    for uniprot in uniprots_list[0:-1]:
        urls_str += f"{uniprot_md_str[uniprot]}, "
    urls_str += f"{uniprot_md_str[uniprots_list[-1]]}"
    return urls_str


def csv_to_md_with_url(
    template_file_path,
    csv_file_path,
    supporting_material_root_dir,
    vendor_to_website_csv_file_path,
):
    """
    Convert the IBEX knowledge-base reagent resources csv file to markdown and add links to the supporting
    material files. Output is written to a file named markdown.md in the parent directory
    of the supporting_material_root_dir. The md_template_path file is expected to contain the
    string {reagent_resources_table} which is replaced with the contents of the actual table.
    """
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(csv_file_path, dtype=str, keep_default_na=False)
    # Sort dataframe according to target, ignoring case.
    df.sort_values(
        by=["Target Name / Protein Biomarker"],
        inplace=True,
        key=lambda x: x.str.lower(),
    )
    supporting_material_path = pathlib.PurePath(supporting_material_root_dir).name
    if not df.empty:
        print("Start linking to supporting material...")
        df["Agree"] = df[
            ["Agree", "Target Name / Protein Biomarker", "Conjugate"]
        ].apply(lambda x: data_to_md_str(x, supporting_material_path), axis=1)
        df["Disagree"] = df[
            ["Disagree", "Target Name / Protein Biomarker", "Conjugate"]
        ].apply(
            lambda x: data_to_md_str(
                x, pathlib.PurePath(supporting_material_root_dir).name
            ),
            axis=1,
        )
        print("Finished linking to supporting material...")
        print("Start linking to UniProt...")
        # Link to the UniProt Knowledgebase. Get the unique uniprots and the corresponding
        # hyperlinked markdown string.
        unique_uniports = set(
            chain(
                *df["UniProt Accession Number"].apply(
                    lambda x: [v.strip() for v in x.split(";")]
                )
            )
        )
        uniprot_md_str = {}
        for uniprot in unique_uniports:
            uniprot_md_str[uniprot] = uniprot_to_md_str(uniprot)
        df["UniProt Accession Number"] = df["UniProt Accession Number"].apply(
            lambda x: uniprots_to_md(x, uniprot_md_str)
        )
        print("Finished linking to UniProt...")
        print("Start linking to vendor websites...")
        vendor_to_website = csv_to_md_str_dict(vendor_to_website_csv_file_path)
        try:
            df["Vendor"] = df["Vendor"].apply(lambda x: vendor_to_website[x])
        except KeyError as k:
            print(f"Vendor ({k}) not found in {vendor_to_website_csv_file_path}.")
            return 1
        print("Finished linking to vendor websites...")

    with open(template_file_path, "r") as fp:
        input_md_str = fp.read()
    with open(supporting_material_root_dir.parent / template_file_path.stem, "w") as fp:
        fp.write(
            input_md_str.replace(
                "{reagent_resources_table}", df.to_markdown(index=False)
            )
        )
    return 0


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Convert knowledge-base reagent resources file from csv to md and add hyperlinks."
    )
    parser.add_argument(
        "md_template_file",
        type=file_path_endswith_md_in,
        help='Path to template markdown file which contains the string "{reagent_resources_table}".',
    )
    parser.add_argument(
        "csv_file", type=file_path, help="Path to the reagent_resources.csv file."
    )
    parser.add_argument(
        "vendor_to_website",
        type=file_path,
        help="Path to csv file mapping between vendor name and website/URL, column headers are Vendor, URL.",
    )
    parser.add_argument(
        "supporting_material_root_dir",
        type=dir_path,
        help="Path to the directory containing the supporting materials files.",
    )
    parser.add_argument(
        "--skip_url_validation",
        action="store_true",
        help="Skip validation of vendor and UniProt urls.",
    )
    args = parser.parse_args(argv)

    try:
        if args.skip_url_validation:
            requests.get = short_circuit_requests_get
        return csv_to_md_with_url(
            template_file_path=args.md_template_file,
            csv_file_path=args.csv_file,
            supporting_material_root_dir=args.supporting_material_root_dir,
            vendor_to_website_csv_file_path=args.vendor_to_website,
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
