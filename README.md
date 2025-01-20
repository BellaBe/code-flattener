# Code Extraction and Repository Flattening Tool

This tool extracts code and file content from either a GitHub repository or a local directory, generating a flattened text output alongside optional metadata. It’s designed for workflows that need an entire project’s text content, such as LLM ingestion or Retrieval-Augmented Generation (RAG) pipelines.

## Features

- **Flexible Input:** Provide a GitHub URL (e.g., https://github.com/user/repo) or local path (e.g., /path/to/your/local/repo).
- **Selective Extraction:** Use `--select` and `--exclude` patterns to include or ignore certain file types. For example, `--select '*.py'` to only include Python files, or `--exclude 'tests/*'`.
- **Metadata-Rich Output:** `code.txt` containing all extracted files (with file paths and basic stats), `metadata.json` (JSON) listing file-level metadata (number of lines, file size, etc.).
- **Directory Structure Generation:** Each extraction includes a directory tree snapshot for context.
- **Hidden Files & Folders:**  Optionally ignore hidden files/folders (`--ignore-hidden`).
- **Verbose Logging:** Add `--verbose` for detailed logs (excluded files, included files, etc.).

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
```
python3 src/main.py \
    --repo "https://github.com/user/repo" \
    --exclude "*.md" "*.png" \
    --select "*.py" \
    --branch "main" \
    --verbose
    --ignore-hidden
```

## Examples:
- Clone a GitHub repo and extract only .py files:
  python extract_repo.py --repo "https://github.com/exampleuser/examplerepo" \
                         --select "*.py"

- Extract from a local repo and include everything:
  python extract_repo.py --repo "/path/to/local/repo" \
                         --verbose --ingnore-hidden


## Options:
- input_path: (positional) A GitHub URL or local directory path.
- `--exclude` [PATTERNS]: Space-separated file patterns to exclude. (e.g., --exclude "*.md" "tests/*")
- `--select` [PATTERNS]: Space-separated file patterns to include. If omitted, all text files are included by default.
- `--branch` [BRANCH]: Branch to checkout if cloning a repository.
- `--ignore-hidden`: Ignore hidden files/directories (names starting with a dot).
- `--verbose`: Prints detailed logs (e.g., which files are excluded, included, etc.).
- `--dry-run`: Simulate processing without actually writing any files.
   
## Future Enhancements
- **RAG Integration:** Utilize the flattened output as a knowledge base for retrieval-augmented question answering.
- **Embeddings & Semantic Search:** Convert the flattened text into embeddings for vector databases (e.g., FAISS, Pinecone, Chroma).
- **Service Wrapper:** Deploy as a microservice for on-demand repository flattening and processing.
