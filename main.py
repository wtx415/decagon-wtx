from dotenv import load_dotenv
import os
import sys

load_dotenv()
project_root = os.getenv("PROJECT_ROOT")
if project_root and project_root not in sys.path:
    sys.path.append(project_root)
