import os
import tempfile
import logging
import json

from utils.color import color_text, YELLOW, GREEN
from utils.filesystem import get_repo_name
from utils.directory import create_directory_tree, scan_directory
from git_utils.clone import clone_repo

def process_directory(
    path: str,
    exclude,
    select,
    verbose: bool,
    dry_run: bool,
    ignore_hidden: bool,
    output_folder: str,
) -> None:
    """
    Scans a local directory, creates a directory tree, and optionally writes outputs.
    """
    logging.info(f"Scanning directory: {path}")
    files = scan_directory(path, exclude, select, verbose, ignore_hidden)
    directory_tree = create_directory_tree(path)

    # Combine directory tree + file contents
    separator = "=" * 48 + "\n"
    content_sections = []
    for f in files:
        section = (
            f"{separator}File: {f['path']} "
            f"({f['lines']} lines, {f['size']} bytes)\n"
            f"{separator}{f['content']}\n"
        )
        content_sections.append(section)

    final_content = directory_tree + "\n\n" + "\n".join(content_sections)

    code_file = os.path.join(output_folder, "code.txt")
    metadata_file = os.path.join(output_folder, "metadata.json")

    if dry_run:
        logging.info(color_text("[DRY RUN] Files processed but no output written.", YELLOW))
        return

    # Write combined code tree + file contents
    with open(code_file, "w", encoding="utf-8") as f:
        f.write(final_content)

    # Write metadata (in JSON format, but the file is named metadata.txt)
    metadata = {"files": files}
    with open(metadata_file, "w", encoding="utf-8") as mf:
        mf.write(json.dumps(metadata, indent=2))

    logging.info(color_text(
        f"Content extracted:\n  {code_file}\n  {metadata_file}",
        GREEN
    ))

def extract_repo_content(
    input_path: str,
    exclude,
    select,
    branch,
    verbose: bool,
    dry_run: bool,
    ignore_hidden: bool,
) -> None:
    """
    Extract content from either a GitHub repo or a local directory.
    """
    repo_name = get_repo_name(input_path)
    output_folder = os.path.join("output", repo_name)

    if not dry_run:
        os.makedirs(output_folder, exist_ok=True)

    if input_path.startswith(("http://", "https://")):
        # It's a remote repo
        logging.info(color_text(f"Detected remote repository: {input_path}", YELLOW))
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = os.path.join(tmpdir, "repo")
            clone_repo(input_path, repo_dir, branch)
            process_directory(
                repo_dir,
                exclude,
                select,
                verbose,
                dry_run,
                ignore_hidden,
                output_folder
            )
    else:
        # It's a local directory
        if not os.path.isdir(input_path):
            raise ValueError(f"Provided path '{input_path}' is not a valid directory.")
        process_directory(
            input_path,
            exclude,
            select,
            verbose,
            dry_run,
            ignore_hidden,
            output_folder
        )
