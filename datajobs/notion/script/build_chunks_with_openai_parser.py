# native Python packages
import os

# third-party packages
from dotenv import load_dotenv

# custom packages
from datajobs.notion.transform import parse_into_chunks_with_openai_parser
from utils.parser.openai_parser import OpenAIParser


if __name__ == "__main__":
    load_dotenv()

    project_root = os.getenv("PROJECT_ROOT")
    input_dir = os.path.join(project_root, "datasets", "notion", "raw")
    input_file_path = os.path.join(input_dir, "data.json")
    output_dir = os.path.join(
        project_root, "datasets", "notion", "processed", "openai_parser"
    )

    # Because this is a demo, limit to just 3 sample help articles to save on OpenAI API usage.
    target_urls = [
        "https://notion.so/help/what-is-a-block",
        "https://notion.so/help/what-is-a-database",
        "https://notion.so/help/workspace-settings",
    ]

    openai_parser = OpenAIParser(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        chunk_size=750,
        chunk_size_buffer=30,
    )
    parse_into_chunks_with_openai_parser(
        input_file_path, output_dir, openai_parser, target_urls=target_urls
    )
