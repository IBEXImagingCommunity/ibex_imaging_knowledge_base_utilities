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


def _description_2_md(description, num_words=3):
    """
    Convert the description markdown formatted string to html using the "details"
    tag which results in a dropdown/accordion display of the information.
    The num_words parameter indicates how many words to display in the accordion
    summary.
    """
    if not description.strip():
        return ""
    # Because the html code will go inside a markdown table and we are using kramdown,
    # default markdown renderer for jekyll, we need to wrap it with nomarkdown to tell kramdown to leave it
    # as is.
    return (
        "{::nomarkdown}"
        + f"<details ><summary>{' '.join(description.split()[0:num_words])}...</summary><p>{description}</p></details>"
        + "{:/}"
    )


def _dataframe_2_md(df, *args, **kwargs):
    """
    Convert a dataframe to markdown. This function addresses an issue with
    the input which will be displayed in a markdown table containing newlines.
    A markdown table entry cannot include newlines we therefor
    replace all '\n' characters with the html tag <br> which works with the
    markdown table.
    """
    return df.replace("\n", "<br>", regex=True).to_markdown(*args, **kwargs)
