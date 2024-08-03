# native Python packages
import os
import time
from datetime import datetime, timezone
from typing import Optional, List

# third-party packages
from bs4 import BeautifulSoup

# custom packages
from utils.file_io import read_json, write_to_json
from utils.logger import get_console_logger
from utils.parser.html_parser import HtmlParser
from utils.parser.openai_parser import OpenAIParser


def extract_articles(text: str) -> List[str]:
    """
    Extracts the articles from the Notion help article.

    Moreover, it removes asides which are used to organize the table of contents on Notion help articles.

    Args:
        text (str): HTML text of the Notion help article.

    Returns:
        List[str]: An array of HTML text of the articles.
    """
    soup = BeautifulSoup(text, "html.parser")
    main_section = soup.find("main")

    if not main_section:
        raise RuntimeError("Main section not found in the HTML text.")

    # This is assuming that each page has only one main article
    articles = main_section.find_all("article")

    if not articles:
        raise RuntimeError("Article not found in the HTML text.")

    for article in articles:
        for aside in article.find_all("aside"):
            aside.decompose()

    return [str(article) for article in articles]


def parse_into_chunks_with_html_parser(
    input_file_path: str, output_dir: str, html_parser: Optional[HtmlParser] = None
):
    if html_parser is None:
        html_parser = HtmlParser()

    start_time = time.time()
    logger = get_console_logger(__name__)

    # Read raw data
    url_to_chunks = {}
    skipped_urls = []
    raw_data = read_json(input_file_path)

    for url, result in raw_data["results"].items():
        html_body = result["html_body"]
        try:
            articles = extract_articles(html_body)
        except RuntimeError as e:
            logger.warning(f"Error in extracting articles. Skipping. URL: {url}")
            skipped_urls.append(url)
            continue

        page_chunks = []
        for article in articles:
            article_chunks = html_parser.parse(article, url)
            page_chunks.extend(article_chunks)

        url_to_chunks[url] = page_chunks

    # Turn chunks into string for the data write process
    url_to_chunks = {
        url: [str(chunk) for chunk in chunks] for url, chunks in url_to_chunks.items()
    }

    end_time = time.time()
    elapsed_time = round((end_time - start_time), 2)
    metadata = {
        "total_count": len(raw_data["results"]),
        "success_count": len(url_to_chunks),
        "skipped_count": len(skipped_urls),
        "success_urls": list(url_to_chunks.keys()),
        "skipped_urls": skipped_urls,
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
        "results": url_to_chunks,
    }

    logger.info("Data transformation completed. Start the data write process.")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata_filepath = os.path.join(output_dir, "metadata.json")
    write_to_json(metadata_filepath, metadata)

    data_filepath = os.path.join(output_dir, "data.json")
    write_to_json(data_filepath, data)


def parse_into_chunks_with_openai_parser(
    input_file_path: str,
    output_dir: str,
    openai_parser: Optional[OpenAIParser] = None,
    target_urls: Optional[List[str]] = None,
):
    if openai_parser is None:
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY could not be found in the environment variables."
            )
        openai_parser = OpenAIParser(api_key=api_key)

    start_time = time.time()
    logger = get_console_logger(__name__)

    # Read raw data
    url_to_chunks = {}
    skipped_urls = []
    raw_data = read_json(input_file_path)

    # If target_urls are provided, only process the target URLs
    if target_urls:
        target_results = {}
        for url in target_urls:
            if url in raw_data["results"]:
                target_results[url] = raw_data["results"][url]
        raw_data["results"] = target_results

    for url, result in raw_data["results"].items():
        logger.info(f"Parsing and building chunks for the url: {url}")

        html_body = result["html_body"]
        try:
            articles = extract_articles(html_body)
        except RuntimeError as e:
            logger.warning(f"Error in extracting articles. Skipping. URL: {url}")
            skipped_urls.append(url)
            continue

        page_chunks = []
        for article in articles:
            article_chunks = openai_parser.parse(article, url)
            page_chunks.extend(article_chunks)

        url_to_chunks[url] = page_chunks

    # Turn chunks into string for the data write process
    url_to_chunks = {
        url: [str(chunk) for chunk in chunks] for url, chunks in url_to_chunks.items()
    }

    end_time = time.time()
    elapsed_time = round((end_time - start_time), 2)
    metadata = {
        "total_count": len(raw_data["results"]),
        "success_count": len(url_to_chunks),
        "skipped_count": len(skipped_urls),
        "success_urls": list(url_to_chunks.keys()),
        "skipped_urls": skipped_urls,
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
        "results": url_to_chunks,
    }

    logger.info("Data transformation completed. Start the data write process.")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata_filepath = os.path.join(output_dir, "metadata.json")
    write_to_json(metadata_filepath, metadata)

    data_filepath = os.path.join(output_dir, "data.json")
    write_to_json(data_filepath, data)
