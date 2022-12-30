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

import re
import argparse
import pathlib
import sys

"""
This script creates the release notes for a given release. These are extracted from the
CHANGELOG.md file and written to release_notes.txt. If the given release does not exist
in the CHANGELOG.md file or there are no notes, the script returns a failure value,
otherwise it is considered a success.
"""


def create_release_notes(
    repository, package_name, release_tag, changelog_file_name, output_file_name
):
    release_notes_header = (
        "# Installing\n\n"
        + "```\n"
        + "pip install --upgrade pip\n"
        + f"pip install https://github.com/{repository}/releases/download/{release_tag}/{package_name}-{release_tag[1:]}-py3-none-any.whl\n"  # noqa E501
        + "```\n\n"
        + "# Release Notes\n\n"
    )

    current_release_pattern = re.compile(r"\s*##\s" + release_tag + r"\s*")
    release_pattern = re.compile(r"\s*##\sv\d+.\d+.\d+\s*")

    release_notes = []
    with open(changelog_file_name, "r") as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            if current_release_pattern.match(line):
                line = fp.readline()
                end_release_notes = False
                while line and not end_release_notes:
                    end_release_notes = release_pattern.match(line)
                    if not end_release_notes:
                        release_notes.append(line)
                    line = fp.readline()
    if release_notes:
        # Get rid of empty lines that may make sense in the CHANGELOG.md but not in the release notes.
        while release_notes and not release_notes[-1].strip():
            del release_notes[-1]
    if release_notes:
        with open(output_file_name, "w") as fp:
            fp.write(release_notes_header)
            fp.write("".join(release_notes))
            return 0
    return 1


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create release notes file from CHANGELOG.md."
    )
    parser.add_argument(
        "repository", help="repository on GitHub with the format OWNER/REPO"
    )
    parser.add_argument(
        "package_name", help="package name as defined in the pyproject.toml"
    )
    parser.add_argument(
        "release_tag", help="release tag with the format vMAJOR.MINOR.PATCH"
    )

    args = parser.parse_args(argv)

    try:
        create_release_notes(
            repository=args.repository,
            package_name=args.package_name,
            release_tag=args.release_tag,
            changelog_file_name=pathlib.Path(__file__).parent.absolute()
            / "CHANGELOG.md",
            output_file_name=pathlib.Path(__file__).parent.absolute()
            / "release_notes.txt",
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
