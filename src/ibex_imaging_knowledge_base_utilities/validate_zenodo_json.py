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
import json
import argparse
from .argparse_types import file_path
from .url_exists import check_urls

"""
This script validates the contents of the .zenodo.json file:
1. Check that the file complies with the JSON file format.
2. Check that the creators section has the three expected fields per creator, affiliation, name, ORCID.
3. Check that there are no duplicate ORCIDs in the creators section (copy paste).
4. Check that the order of entries is as expected:
   [Ziv Yaniv] [alphabetical order] [Ron Germain] [Andrea Radtke].
5. Check that there are no duplicate grant ids in the grants section (copy paste).

Possibly also validate compliance to a json schema. Unfortunately, not sure
what schema to use. The zenodo documentation on GitHub setup
(https://developers.zenodo.org/#add-metadata-to-your-github-repository-release) points to this
schema: https://zenodo.org/schemas/deposits/records/legacyrecord.json which is old and
does not match what zenodo actually checks for.
There is also this schema: https://zenodo.org/schemas/records/record-v1.0.0.json
which appears to be the updated one but doesn't include entries such as upload_type which is
accepted by zenodo, so really broken.

Relevant possible code:
import jsonschema
def validate_zenodo_schema_compliance(zenodo_json, zenodo_json_schema):
    with open(zenodo_json_schema) as fp:
        zenodo_schema = json.load(fp)
    with open(zenodo_json) as fp:
        zenodo_data = json.load(fp)
    jsonschema.validate(instance=zenodo_data, schema=zenodo_schema)
"""


def validate_zenodo_json(zenodo_json):
    """
    Validate the zenodo json. We require that contributors provide their ORCID which is optional in the
    general zenodo schema, we check for uniqueness and we have a specific order of contributors we enforce.

    returns 1 if invalid, 0 otherwise.
    """
    with open(zenodo_json) as fp:
        zenodo_dict = json.load(fp)
    # Check that all the expected entries are in the given json file, better done via schema validation, but
    # don't have an official zenodo schema (see issue above in script description)
    # expected entries in json file and their types
    json_key_types = {
        "title": str,
        "upload_type": str,
        "description": str,
        "creators": list,
        "grants": list,
        "keywords": list,
        "license": dict,
    }
    if zenodo_dict.keys() != json_key_types.keys():
        print(
            f"Unexpected or missing key types in file. Expected keys ({json_key_types.keys()}), actual keys ({zenodo_dict.keys()})."  # noqa E501
        )
        return 1
    for key in json_key_types.keys():
        if type(zenodo_dict[key]) != json_key_types[key]:
            print(
                f"Unexpected entry type for key ({key}). Expected {json_key_types[key]}, got ({type(zenodo_dict[key])})."  # noqa E501
            )
            return 1

    # Check that all creators provided affiliation, name and orcid
    orcids = []
    required_information = {"affiliation", "name", "orcid"}
    for data in zenodo_dict["creators"]:
        # short circuit evaluation, dictionary access only happens if all keys exist
        if (
            not required_information.issubset(data.keys())
            or data["affiliation"].strip() == ""
            or data["name"].strip() == ""
            or data["orcid"].strip() == ""
        ):
            print(f"Missing required information in creators section, entry {data}.")
            return 1
        orcids.append(data["orcid"])
    # Check creator uniqueness
    existing_orcids = set()
    duplicates = [o for o in orcids if o in existing_orcids or existing_orcids.add(o)]
    if duplicates:
        print(f"Duplicate entries in creators section: {duplicates}.")
        return 1
    # Check that the ORCID url exists. Do not allow redirects because the site forwards non existent urls to the
    # ORCID registration page, so even if the page doesn't exist there is no 404 error.
    orcid_urls_exist = check_urls([f"https://orcid.org/{c['orcid']}" for c in zenodo_dict["creators"]], allow_redirects=False)
    orcid_errors = [creator for url_exist, creator in zip(orcid_urls_exist,zenodo_dict["creators"]) if not url_exist]
    if orcid_errors:
        print("The ORCID for the following entries is incorrect:\n")
        print(orcid_errors)
        return 1
    # First ORCID and two last ORCIDs are fixed, the entries in between are according
    # to alphabetical order
    if (
        zenodo_dict["creators"][0]["orcid"] != "0000-0003-0315-7727"
        or zenodo_dict["creators"][-1]["orcid"] != "0000-0003-4379-8967"
        or zenodo_dict["creators"][-2]["orcid"] != "0000-0003-1495-9143"
        or zenodo_dict["creators"][1:-2]
        != sorted(
            zenodo_dict["creators"][1:-2],
            key=lambda creator_entry: creator_entry["name"],
        )
    ):
        print(
            "Order in creators list is not as expected. First entry and last two are fixed and those in between should be in alphabetical order."  # noqa E501
        )
        return 1

    # Check grant uniqueness
    grant_ids = []
    for data in zenodo_dict["grants"]:
        if data["id"].strip() == "":
            print(f"Missing required information in grants section, entry {data}.")
            return 1
        grant_ids.append(data["id"])
    existing_grants = set()
    duplicates = [
        g for g in grant_ids if g in existing_grants or existing_grants.add(g)
    ]
    if duplicates:
        print(f"Duplicate entries in grants section: {duplicates}.")
        return 1
    return 0


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Validate .zenodo.json file content.")
    parser.add_argument("zenodo_json", type=file_path, help=".zenodo.json file")
    args = parser.parse_args(argv)

    return validate_zenodo_json(args.zenodo_json)


if __name__ == "__main__":
    sys.exit(main())
