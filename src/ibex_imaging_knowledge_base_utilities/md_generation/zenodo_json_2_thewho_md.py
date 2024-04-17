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
from ibex_imaging_knowledge_base_utilities.argparse_types import (
    file_path_endswith,
    dir_path,
)


def zenodo_creators_to_md(template_file_path, zenodo_json_file_path, output_dir):
    # Read the json file and get creators list
    with open(zenodo_json_file_path) as fp:
        creators_list = json.load(fp)["creators"]
    contrib_list_md = "\n".join(
        [
            f"1. {cr['name']}, {cr['affiliation']}, [{cr['orcid']}](https://orcid.org/{cr['orcid']})."
            for cr in creators_list
        ]
    )
    with open(template_file_path, "r") as fp:
        input_md_str = fp.read()
    with open(output_dir / template_file_path.stem, "w") as fp:
        fp.write(input_md_str.format(contributor_list=contrib_list_md))


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Convert creators list from .zenodo.json to md."  # noqa E501
    )
    parser.add_argument(
        "md_template_file",
        type=lambda x: file_path_endswith(x, ".md.in"),
        help='Path to template markdown file which contains the string "{contributor_list}".',
    )
    parser.add_argument(
        "zenodo_json",
        type=lambda x: file_path_endswith(x, ".json"),
        help="Path to the .zenodo.json file.",
    )
    parser.add_argument(
        "output_dir",
        type=dir_path,
        help="Path to the output directory (the output markdown file is written to this directory).",
    )
    args = parser.parse_args(argv)

    try:
        return zenodo_creators_to_md(
            template_file_path=args.md_template_file,
            zenodo_json_file_path=args.zenodo_json,
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
