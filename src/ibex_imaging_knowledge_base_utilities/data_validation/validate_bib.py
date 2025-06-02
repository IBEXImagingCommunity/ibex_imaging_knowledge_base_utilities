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

import bibtexparser
import sys
import argparse
from ibex_imaging_knowledge_base_utilities.argparse_types import file_path_endswith

"""
This script validates the contents of the publications.bib file, a bibliography file in bibtex format.
1. Check that there are no duplicate citation keys.
2. Check that the required fields ("author", "title", "year", "doi", "note") exist. An entry without doi and note
   fields is a valid bibtex entry in terms of format but the IBEX imaging knowledge-base requires them.

Note that incorrectly formatted entries in terms of syntax are skipped and no error is reported. This is due to the
usage of bibtexparser v1. The incorrectly formatted entries are listed as comments by the v1 implementation. This is
expected to change in v2 but it has not been released yet. Will require updating the code once released.
"""


def validate_bib_file_data(publications_bib_filename):

    # load the bibliography data, entries that are incorrect syntactically (e.g. missing ID or comma etc.)
    # are ignored
    with open(publications_bib_filename) as biblatex_file:
        bib_database = bibtexparser.load(biblatex_file)

    # bibtexparser v1 does not report errors for entries with syntax errors, they are listed as comments.
    # We assume no comments in the file.
    # v2 which is still under development explicitly lists them as errors bib_database.failed_blocks
    # the following code will need to be updated once v2 is officially released.
    if bib_database.comments:
        print(
            f"Malformed bibtex entries, syntax error\n:{bib_database.comments}",
            file=sys.stderr,
        )
        return 1

    # list all the required bibtex keys using lowercase (bibtex isn't case sensitive so we convert everything to
    # lower case).
    required_entry_keys = {"id", "author", "title", "year", "doi", "note"}

    # check that the bib IDs are unique
    bib_database_ids = dict()
    for entry in bib_database.entries:
        current_id = entry["ID"]
        if current_id in bib_database_ids:
            bib_database_ids[current_id] = bib_database_ids[current_id] + 1
        else:
            bib_database_ids[current_id] = 1
        # using casefold() is preferred over lower() as it deals correctly with non-ascii characters
        entry_keys = {k.casefold() for k in entry.keys()}
        if not required_entry_keys.issubset(entry_keys):
            print(
                f"One or more missing required fields ({', '.join(required_entry_keys)}) from entry {current_id}.",
                file=sys.stderr,
            )
            return 1
    duplicate_keys = [k for k, count in bib_database_ids.items() if count > 1]
    if duplicate_keys:
        print(
            f"Duplicate keys in bib file ({publications_bib_filename}): {', '.join(duplicate_keys)}.",
            file=sys.stderr,
        )
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate bibtex file content.")
    parser.add_argument(
        "bibfile",
        type=lambda x: file_path_endswith(x, ".bib"),
        help="A bibliography file in bibtex format. Entries must contain the following fields: "
        + "author, title, year, doi, and note.",
    )
    args = parser.parse_args(argv)

    return validate_bib_file_data(args.bibfile)


if __name__ == "__main__":
    sys.exit(main())
