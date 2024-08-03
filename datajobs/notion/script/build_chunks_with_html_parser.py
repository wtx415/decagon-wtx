# native Python packages
import os

# third-party packages
from dotenv import load_dotenv

# custom packages
from datajobs.notion.transform import parse_into_chunks_with_html_parser
from utils.parser.html_parser import HtmlParser

if __name__ == "__main__":
    load_dotenv()

    project_root = os.getenv("PROJECT_ROOT")
    input_dir = os.path.join(project_root, "datasets", "notion", "raw")
    input_file_path = os.path.join(input_dir, "data.json")
    output_dir = os.path.join(
        project_root, "datasets", "notion", "processed", "html_parser"
    )

    html_parser = HtmlParser(
        tags=["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"],
        inseparable_tags=["li"],
        chunk_size=750,
        chunk_size_buffer=30,
    )
    parse_into_chunks_with_html_parser(input_file_path, output_dir)
