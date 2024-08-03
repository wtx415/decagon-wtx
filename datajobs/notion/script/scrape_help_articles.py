# native Python packages
import os

# third-party packages
from dotenv import load_dotenv

# custom packages
from datajobs.notion.scrape import scrape


if __name__ == "__main__":
    load_dotenv()

    project_root = os.getenv("PROJECT_ROOT")
    output_dir = os.path.join(project_root, "datasets", "notion", "raw")

    NOTION_HELP_PAGE_URL = "https://notion.so/help"
    scrape(NOTION_HELP_PAGE_URL, output_dir)
