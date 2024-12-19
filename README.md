# Code Extraction and Repository Flattening Tool

This tool extracts code and file content from a GitHub repository or a local repository, flattening it into a single large text file. Each extracted file is preceded by its file path and metadata, and a directory structure overview is provided at the start. This format makes it ideal for passing into an LLM or integrating into a Retrieval Augmented Generation (RAG) pipeline.

## Features

- **Flexible Input:** Accepts either a GitHub repository URL or a local repository path.
- **Selective Extraction:** Supports `--select` and `--exclude` patterns so you can specify which files to include or ignore (e.g. only `.py` files or a single `ingest.py`).
- **Metadata-Rich Output:** Outputs file paths, line counts, and byte sizes before each file’s content.
- **Directory Structure Generation:** Provides a hierarchical directory tree snapshot for context.
- **Automatic Exclusion of `.git`:** The `.git` directory is skipped by default.
- **JSON Support:** Optionally output metadata in JSON format for programmatic use.

## Example Output

```text
Directory structure:
├── README.md
├── components
│   └── index.js
└── utils
    └── fetch.js

================================================
File: components/index.js (30 lines, 693 bytes)
================================================
<content of index.js>

================================================
File: utils/fetch.js (113 lines, 3025 bytes)
================================================
<content of fetch.js>

```

## Usage

1. Install Dependencies:
   `pip install -r requirements.txt`
   
2. Run the Script:
   `python extract_repo.py --repo <GitHub URL or local path> --output <output_file> [--exclude pattern] [--select pattern] [--json]`

## Examples:
- Clone a GitHub repo and extract only .py files:
  python extract_repo.py --repo "https://github.com/exampleuser/examplerepo" \
                         --output "flattened.txt" \
                         --exclude "*.md" \
                         --select "*.py"

- Extract from a local repo and include everything:
  python extract_repo.py --repo "/path/to/local/repo" \
                         --output "flattened.txt"

## Options:
`--repo`: GitHub repository URL or local repository path.
`--output`: Path to the resulting flattened text file.
`--select`: File patterns to include (e.g., --select "*.py").
`--exclude`: File patterns to exclude (e.g., --exclude "tests/*").
`--json`: (Optional) Outputs metadata in JSON format.
   
## Future Enhancements
- **RAG Integration:** Utilize the flattened output as a knowledge base for retrieval-augmented question answering.
- **Embeddings & Semantic Search:** Convert the flattened text into embeddings for vector databases (e.g., FAISS, Pinecone, Chroma).
- **Service Wrapper:** Deploy as a microservice for on-demand repository flattening and processing.
