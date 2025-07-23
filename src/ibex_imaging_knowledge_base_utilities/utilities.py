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

import hashlib


def md5sum(filename):
    """
    Compute the md5 hashsum value for the given file. We don't use SimpleITK's hash function
    because that takes the image in memory as input which is different from the content on disk.
    Using the image in memory hashsum is more flexible because different file contents can represent
    the same image (a.jpg and b.png can have exactly the same intensity information but the files on
    disk are different). This isn't easily accessible to users who can compute the hash for a file on
    disk.
    """
    md5 = hashlib.md5()
    with open(filename, "rb") as fp:
        for chunk in iter(lambda: fp.read(128 * md5.block_size), b""):
            md5.update(chunk)
        return md5.hexdigest()
