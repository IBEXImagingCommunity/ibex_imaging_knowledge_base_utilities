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

import pathlib
import argparse

# definitions of argparse types, enables argparse to validate the command line parameters


def file_path_endswith(path_str, ends_with_pattern=""):
    p = pathlib.Path(path_str)
    if p.is_file() and path_str.endswith(ends_with_pattern):
        return p
    else:
        raise argparse.ArgumentTypeError(
            f"Invalid argument ({path_str}), not a file path, file does not exist, or path does not"
            + f' end with "{ends_with_pattern}".'
        )


def dir_path(path):
    p = pathlib.Path(path)
    if p.is_dir():
        return p
    else:
        raise argparse.ArgumentTypeError(
            f"Invalid argument ({path}), not a directory path or directory does not exist."
        )
