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

import requests
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import sys
import pandas as pd


def url_exists(
    url,
    request_timeout=2,
    allow_redirects=True,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
    },
    **kwargs,
):
    """
    Check if a url exists. All parameters supported by requests.head are available. Those not explicitly
    listed are forwarded as is to requests.head. Timeout exceptions are considered a success. Also,
    the 403 "forbidden" code (server understands the request but refuses to authorize it) is considered
    success too.
    """
    try:
        # Using requests.head and not requests.get because
        # we don't need the webpage content.
        res = requests.head(
            url,
            timeout=request_timeout,
            headers=request_headers,
            allow_redirects=allow_redirects,
            **kwargs,
        )
        if res.status_code == 403:
            print(f"{url}: 403 forbidden code, server refused to authorize request")
        # HTTP 200 status code for success
        return res.status_code in [200, 403]
    except requests.exceptions.Timeout:
        print(f"{url}: timed out ({request_timeout}sec)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{url}: {e}")
        return False


def url_exists_with_retries(
    url,
    retry_num=0,
    request_timeout=2,
    allow_redirects=True,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
    },
    **kwargs,
):
    if url_exists(url, request_timeout, allow_redirects, request_headers, **kwargs):
        return True
    # Retry using exponential backoff + some randomness so that we don't get a bunch of
    # threads or processes all performing queries in a synchronized fashion.
    # We could have used the Retry built in strategy
    # (https://requests.readthedocs.io/en/latest/user/advanced/#example-automatic-retries,
    # https://www.zenrows.com/blog/python-requests-retry#best-methods-to-retry)
    # but it isn't more succinct or efficient than what is implemented here.
    for i in range(retry_num):
        time.sleep(pow(base=2, exp=i) + np.random.random())
        if url_exists(url, request_timeout, allow_redirects, request_headers, **kwargs):
            return True
    return False


def check_urls(
    urls_container,
    num_threads=2,
    retry_num=0,
    request_timeout=10,
    allow_redirects=True,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
    },
    **kwargs,
):
    """
    Check url existence for a number of urls in a container. It is assumed that the urls
    are for different hosts (if they are on the same host then better to use a
    requests.Session object).
    """
    with ThreadPoolExecutor(num_threads) as executor:
        return list(
            executor.map(
                lambda x: url_exists_with_retries(
                    url=x,
                    retry_num=retry_num,
                    request_timeout=request_timeout,
                    allow_redirects=allow_redirects,
                    request_headers=request_headers,
                    **kwargs,
                ),
                urls_container,
            )
        )


def duplicated_entries_single_value_columns(df, column_names):
    """
    Given a dataframe and a container with column names, return a dictionary listing
    columns that have duplicates and a string listing the value and the duplicated
    rows for that value. For example,
    {'Fluorescent Probe': 'AF700 rows [62, 70], BV421 rows [8, 69, 71, 72]'}
    If there are no duplicates for any of the columns, return an empty dictionary.
    """
    # shift the index number which is zero based and ignores the header so that the returned
    # row numbers match what you would see in a spreadsheet editor (e.g. excell, google docs)
    shift_index = 2

    duplicate_information = {}
    for col in column_names:
        duplicated_entries = df[col][df[col].duplicated()]
        duplicate_set = set(duplicated_entries)
        if duplicate_set:
            duplicate_information[col] = ", ".join(
                [
                    f"{dup} rows {[i + shift_index for i in df.index[df[col] == dup].to_list()]}"
                    for dup in duplicate_set
                ]
            )
    return duplicate_information


def duplicated_entries_multi_value_columns(df, column_names):
    # shift the index number which is zero based and ignores the header so that the returned
    # row numbers match what you would see in a spreadsheet editor (e.g. excell, google docs)
    shift_index = 2

    duplicate_information = {}
    for col in column_names:
        problem_rows = []
        for i, x in enumerate(df[col].to_numpy().flatten()):
            current_data = [v.strip() for v in x.split(";") if v.strip() != ""]
            if len(current_data) != len(set(current_data)):
                problem_rows += [i + shift_index]
            if problem_rows:
                duplicate_information[col] = ", ".join(problem_rows)
    return duplicate_information


def get_multi_column_data(df, single_data_columns, multi_data_columns):
    """
    Return a set containing the unique data elements found in the single_data_columns and multi_data_columns.
    multi_data_columns contain multiple data elements separated by semicolons.
    """
    if single_data_columns:
        data_list = [
            data
            for data in df[single_data_columns].to_numpy().flatten()
            if data.strip() != ""
        ]
    else:
        data_list = []
    if multi_data_columns:
        multi_data = df[multi_data_columns].to_numpy().flatten()
        for x in multi_data:
            data_list += [v.strip() for v in x.split(";") if v.strip() != ""]
    return set(data_list)


def validate_df(
    df,
    data_required_column_names,
    data_optional_column_names=None,
    unique_single_value_columns=None,
    unique_multi_value_columns=None,
    url_columns=None,
    multi_url_columns=None,
    doi_columns=None,
    multi_doi_columns=None,
    allow_redirects=True,
    column_is_in=None,
    multi_value_column_is_in=None,
):
    """
    Given a dataframe validate that:
    1. The data_required + data_optional column names match all the dataframe column names.
    2. There is no leading or trailing whitespace in all dataframe entries.
    3. The columns in data_required_column_names all have content.
    4. There are no duplicate entries in the columns which are listed as unique_entry_columns
    5. Check that urls listed in the url_columns and multi_url_columns (several urls in single
       cell separated by semicolons) all exist, no 404 errors.
    6. Check that the dois listed in the doi_columns and multi_doi_columns (several DOIs in single
       cell separated by semicolons) all exist, no 404 errors.
    7. The content of the columns listed in the column_is_in/multi_value_column_is_in dictionary keys
       is in the list of values provided for them (e.g. "Yes", "No" in the "Recommend" column of the
       reagent_resources.csv or ORCIDS from .zenodo.json in the "Agree" column).
    """
    # shift the index number which is zero based and ignores the header so that the returned
    # row numbers match what you would see in a spreadsheet editor (e.g. excell, google docs)
    shift_index = 2

    # check that the data_required_column_names and data_optional_column_names have no common column (error in
    # JSON configuration file)
    # check that the column names match the expected ones
    data_required = set(
        [] if not data_required_column_names else data_required_column_names
    )
    data_optional = set(
        [] if not data_optional_column_names else data_optional_column_names
    )
    data_required_optional_intersection = data_required.intersection(data_optional)
    if data_required_optional_intersection:
        print(
            "Problem with JSON configuration file. The following columns appear in both required and optional "
            + f"data columns: {data_required_optional_intersection}",
            file=sys.stderr,
        )
        return 1
    expected_column_names = data_required.union(data_optional)
    actual_column_names = set(df.columns)
    unexpected_columns = actual_column_names.difference(expected_column_names)
    if unexpected_columns:
        print(
            "The following columns are not part of the expected column headings "
            + f"({expected_column_names}): {unexpected_columns}.",
            file=sys.stderr,
        )
        return 1
    missing_columns = expected_column_names.difference(actual_column_names)
    if missing_columns:
        print(
            f"The following columns are missing (expected column headings {expected_column_names}): {missing_columns}.",
            file=sys.stderr,
        )
        return 1

    # check for leading/trailing whitespace in dataframe entries
    leading_trailing = df.map(lambda x: x != x.strip())
    leading_trailing_rows = df.index[leading_trailing.any(axis=1)].to_list()
    if leading_trailing_rows:
        print(
            "The following rows have entries with leading/trailing whitespace (please remove): "
            + f"{[str(i + shift_index) for i in leading_trailing_rows]}.",
            file=sys.stderr,
        )
        return 1

    # check columns in data_required_column_names all have content
    sub_df = df[data_required_column_names]
    empty_entries = sub_df == ""
    empty_rows = sub_df.index[empty_entries.any(axis=1)].to_list()
    if empty_rows:
        print(
            f"The following rows have cells that are required to have data but don't ({data_required_column_names}): "
            + f"{[str(i + shift_index) for i in empty_rows]}.",
            file=sys.stderr,
        )
        return 1

    # get duplicated entries in columns that are required to have unique ones
    if unique_single_value_columns:
        duplicates = duplicated_entries_single_value_columns(
            df, unique_single_value_columns
        )
        if duplicates:
            for c_name, info in duplicates.items():
                print(
                    f"Duplicate information in column {c_name} not allowed: {duplicates[c_name]}.",
                    file=sys.stderr,
                )
            return 1
    # check if a multi-value column contains the same value multiple times in the same cell
    if unique_multi_value_columns:
        duplicates = duplicated_entries_multi_value_columns(
            df, unique_multi_value_columns
        )
        if duplicates:
            for c_name, info in duplicates.items():
                print(
                    f"Duplicate information in column {c_name} not allowed: {duplicates[c_name]}.",
                    file=sys.stderr,
                )
            return 1

    # check that the urls exist (no "not found" 404 errors)
    unique_urls = get_multi_column_data(df, url_columns, multi_url_columns)
    if unique_urls:
        url_exists = check_urls(unique_urls, allow_redirects=allow_redirects)
        invalid_urls = [
            url for url, url_exists in zip(unique_urls, url_exists) if not url_exists
        ]
        if invalid_urls:
            print(
                f"Problematic or incorrect urls: {', '.join(invalid_urls)}",
                file=sys.stderr,
            )
            return 1

    # check that the DOIs exist (no "not found" 404 errors)
    unique_dois = get_multi_column_data(df, doi_columns, multi_doi_columns)
    if unique_dois:
        unique_dois_url = [f"https://doi.org/{doi}" for doi in unique_dois]
        url_exists = check_urls(unique_dois_url, allow_redirects=allow_redirects)
        invalid_dois = [
            doi for doi, url_exists in zip(unique_dois, url_exists) if not url_exists
        ]
        if invalid_dois:
            print(
                f"Problematic or incorrect dois: {', '.join(invalid_dois)}",
                file=sys.stderr,
            )
            return 1

    # check that the contents of the single value columns are limited to the expected values.
    if column_is_in:
        found_unexpected_values = False
        for column_name, expected_values in column_is_in.items():
            current_series = df[column_name]
            unexpected_values = set(
                current_series[~current_series.isin(expected_values)]
            )
            if unexpected_values:
                found_unexpected_values = True
                print(
                    f"Unexpected entry values in column '{column_name}': {', '.join(unexpected_values)}",
                    file=sys.stderr,
                )
                print(
                    f"Values can only be one of the following: {', '.join(expected_values)}",
                    file=sys.stderr,
                )
        if found_unexpected_values:
            return 1
    # check that the contents of the multi value columns (semicolon separator) are limited to the expected values.
    if multi_value_column_is_in:
        found_unexpected_values = False
        for column_name, expected_values in multi_value_column_is_in.items():
            current_column_values = (
                df[column_name].str.split(";", expand=True).to_numpy().flatten()
            )
            # Get all the values that are not NaN, None and empty string
            current_column_values = pd.Series(
                current_column_values[
                    np.logical_and(
                        current_column_values != "", ~pd.isna(current_column_values)
                    )
                ]
            )
            unexpected_values = set(
                current_column_values[~current_column_values.isin(expected_values)]
            )
            if unexpected_values:
                found_unexpected_values = True
                print(
                    f"Unexpected entry values in column '{column_name}': {', '.join(unexpected_values)}",
                    file=sys.stderr,
                )
                print(
                    f"Values can only be one of the following: {', '.join(expected_values)}",
                    file=sys.stderr,
                )
        if found_unexpected_values:
            return 1

    return 0
