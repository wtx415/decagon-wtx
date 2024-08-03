# RAG Pipeline

## Overview
This repository contains the code to run the RAG pipeline for Notion help articles.

## Requirements
- This repository uses `git lfs` to store JSON files that contain scraped and processed data.

## Quickstart
1. Set up the environment with the following steps:
* Create a virtual env `python -m venv venv`
* Activate the virtual env `source venv/bin/activate`
* Install the required packages `pip install -r requirements.txt`
* Initialize git lfs (large file storage) `git lfs install`
  - Note: If git lfs is not installed yet, install the extension from the official website ([link](https://git-lfs.com/))
* Add the project root directory to `PYTHONPATH` to enable appropriate import path `export PYTHONPATH=$PYTHONPATH:/path/to/project/root`
  - Note: Replace `/path/to/project/root` with the actual path to the project root directory

2. To run scripts:
* To scrape Notion help articles - `python datajobs/notion/script/scrape_help_articles.py`
* To build chunks with HTML parser (BeautifulSoup) - `python datajobs/notion/script/build_chunks_with_html_pareser.py`
* To build chunks with OpenAI parser (requires OpenAI API key) - `python datajobs/notion/script/build_chunks_with_openai_parser.py`
  - Note: Set the `OPENAI_API_KEY` environment variable in the `.env` file

3. To see the resulting datasets, please check the `datasets` folder.