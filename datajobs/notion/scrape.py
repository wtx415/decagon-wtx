# native Python packages
import hashlib
import os
import time
from typing import Optional
from collections import OrderedDict
from datetime import datetime, timezone
from urllib.parse import urlparse

# third-party packages
import requests
from bs4 import BeautifulSoup

# custom packages
from utils.file_io import write_to_json
from utils.logger import get_console_logger


NOTION_DOMAIN = "notion.so"


def is_valid_url(url: str) -> bool:
    """
    Check if the URL is a valid Notion Help URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a valid Notion Help URL, False otherwise.
    """
    if not isinstance(url, str):
        raise ValueError("The URL must be a string")

    parsed_url = urlparse(url)

    return (
        parsed_url.path.startswith("/help") and "notion-academy" not in parsed_url.path
    )


def get_canonical_url(url: str) -> str:
    """
    Get the canonical URL of a given URL.

    Canonical URL is the URL composed of only https protocol, domain, and URL path.
    It ignores query parameters and fragments.

    This is useful to
    Args:
        url (str): The URL to parse.

    Returns:
        str: The canonical URL.
    """
    parsed_url = urlparse(url)

    return f"https://{NOTION_DOMAIN}{parsed_url.path}"


def make_request(
    url: str, timeout: int = 10, max_attempts: int = 3, backoff_factor: int = 1
) -> Optional[requests.Response]:
    """
    Makes an HTTP GET request with retry logic.

    Args:
        url (str): The URL to request.
        timeout (int): The number of seconds to wait for a response. Default is 10.
        max_attempts (int): Maximum number of retry attempts. Default is 3.
        backoff_factor (int): Factor to multiply the delay between retries. Default is 1.

    Returns:
        Optional[requests.Response]: The response object if the request is successful,
                                     or None if all retry attempts fail.
    """
    logger = get_console_logger(__name__)
    attempt = 1
    while attempt <= max_attempts:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_attempts:
                raise e
            delay = backoff_factor * 2 ** (attempt - 1)  # Exponential backoff
            logger.error(
                f"Failed to fetch a webpage. URL: {url}. Attempt: {attempt}. Reason: {e}. Retrying in {delay} sec."
            )
            time.sleep(delay)

        attempt += 1


def scrape(root_url: str, output_dir: Optional[str] = None) -> None:
    start_time = time.time()
    logger = get_console_logger(__name__)

    logger.info("Scrape Notion's Help articles")

    if not is_valid_url(root_url):
        raise ValueError("The URL is not a valid Notion Help URL")

    queue = OrderedDict()
    queue[root_url] = None
    visited_urls = set()
    failed_urls = set()
    skipped_urls = set()
    valid_results = {}

    while queue:
        url, _ = queue.popitem(last=False)
        logger.info(f"Visiting a webpage. URL: {url}")
        visited_urls.add(url)

        try:
            response = make_request(url)
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to fetch a webpage. Will stop the attempt. URL: {url}: Reason: {e}"
            )
            failed_urls.add(url)
            continue

        valid_results[url] = {
            "status_code": response.status_code,
            "checksum": hashlib.md5(response.text.encode()).hexdigest(),
            "html_body": response.text,
        }

        html_body = response.text
        soup = BeautifulSoup(html_body, "html.parser")

        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            canonical_url = get_canonical_url(href)
            if canonical_url:
                if (
                    canonical_url not in visited_urls
                    and canonical_url not in skipped_urls
                    and canonical_url not in queue
                ):
                    if is_valid_url(canonical_url):
                        queue[canonical_url] = None
                    else:
                        skipped_urls.add(canonical_url)
            else:
                skipped_urls.add(href)
                logger.warning(f"Failed to extract a canonical URL. URL: {href}")

    logger.info(
        "Scraping for Notion's Help articles completed. Start the data write process."
    )

    if not output_dir:
        project_root = os.getenv("PROJECT_ROOT")
        output_dir = os.path.join(project_root, "datasets", "notion", "raw")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    end_time = time.time()
    elapsed_time = round((end_time - start_time), 2)
    metadata = {
        "root_url": root_url,
        "visited_count": len(visited_urls),
        "skipped_count": len(skipped_urls),
        "success_count": len(valid_results),
        "failed_count": len(failed_urls),
        "visited_urls": sorted(visited_urls),
        "skipped_urls": sorted(skipped_urls),
        "failed_urls": sorted(failed_urls),
        "elapsed_time": elapsed_time,
        "start_time": datetime.fromtimestamp(start_time, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        "end_time": datetime.fromtimestamp(end_time, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        ),
    }
    data = {
        "metadata": metadata,
        "results": valid_results,
    }

    metadata_filepath = os.path.join(output_dir, "metadata.json")
    write_to_json(metadata_filepath, metadata)

    data_filepath = os.path.join(output_dir, "data.json")
    write_to_json(data_filepath, data)
