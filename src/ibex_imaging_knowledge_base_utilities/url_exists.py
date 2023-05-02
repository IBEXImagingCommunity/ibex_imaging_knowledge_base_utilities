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


def url_exists(
    url,
    request_timeout=2,
    allow_redirects=True,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
    },
    **kwargs
):
    """
    Check if a url exists. All parameters supported by requests.get are available. Those not explicitly
    listed are forwarded as is to requests.get.
    """
    try:
        # Using requests.get and not requests.head. Theoretically we should use requests.head because
        # we don't need the webpage content. Unfortunatly, some servers (e.g. https://www.novusbio.com/)
        # did not respond in a reasonable time to head, but do to get.
        res = requests.get(
            url,
            timeout=request_timeout,
            headers=request_headers,
            allow_redirects=allow_redirects,
            **kwargs
        )
        # HTTP 200 status code for success
        return res.status_code == 200
    except requests.exceptions.RequestException:
        return False


def url_exists_with_retries(
    url,
    retry_num=0,
    request_timeout=2,
    allow_redirects=True,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
    },
    **kwargs
):
    if url_exists(url, request_timeout, allow_redirects, request_headers, **kwargs):
        return True
    # Retry using exponential backoff + some randomness so that we don't get a bunch of
    # threads or processes all performing queries in a synchronized fashion.
    for i in range(retry_num):
        time.sleep(pow(base=2, exp=i) + np.random.random())
        if url_exists(url, request_timeout, allow_redirects, request_headers, **kwargs):
            return True
    return False


def check_urls(
    urls_container,
    num_threads=5,
    retry_num=0,
    request_timeout=2,
    allow_redirects=True,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"  # noqa E501
    },
    **kwargs
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
                    **kwargs
                ),
                urls_container,
            )
        )
