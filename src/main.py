import argparse
import os
import subprocess
import sys
import tempfile
import json
import logging
from fnmatch import fnmatchcase
from typing import List, Dict, Optional

# --- Optional: Colored Console Output ---

def color_text(text: str, color_code: str) -> str:
    """Return colorized text if terminal supports it."""
    return f"{color_code}{text}\033[0m"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# --- Utility Functions ---

def is_github_url(path: str) -> bool:
    return path.startswith(("http://", "https://"))

def get_repo_name(path_or_url: str) -> str:
    """
    Extract the repository name from either a GitHub URL
    or a local directory path.
    Examples:
      - https://github.com/user/repo     -> repo
      - https://github.com/user/repo.git -> repo
      - /home/user/my_local_repo         -> my_local_repo
    """
    if is_github_url(path_or_url):
        # Split on '/' and take the last part, remove .git if present
        parts = path_or_url.rstrip('/').split('/')
        repo = parts[-1]
        if repo.endswith('.git'):
            repo = repo[:-4]
        return repo
    else:
        # Local path: basename
        return os.path.basename(os.path.normpath(path_or_url))

def is_text_file(file_path: str) -> bool:
    """Heuristic check: detect if a file is binary by searching for null bytes in the first chunk."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
        return b'\x00' not in chunk
    except Exception:
        return False

def read_file_content(file_path: str) -> str:
    """Safely read file content with a fallback if there's an error."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def create_directory_tree(path: str) -> str:
    """Generate a tree-like structure (in text) from the given directory."""
    tree = []
    
    def build_tree(dir_path, prefix=""):
        try:
            entries = sorted(e for e in os.listdir(dir_path) if e != ".git")
        except PermissionError:
            # Handle potential permission issues
            tree.append(prefix + "[Permission Denied]")
            return

        for i, entry in enumerate(entries):
            full_path = os.path.join(dir_path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            tree.append(prefix + connector + entry)

            if os.path.isdir(full_path):
                new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
                build_tree(full_path, new_prefix)
    
    build_tree(path)
    return "Directory structure:\n" + "\n".join(tree)

def create_file_content_string(files: List[Dict], directory_tree: str) -> str:
    """Create a combined string of the directory tree + file contents."""
    separator = "=" * 48 + "\n"
    content_sections = [
        f"{separator}File: {f['path']} "
        f"({f['lines']} lines, {f['size']} bytes)\n"
        f"{separator}{f['content']}\n"
        for f in files
    ]
    return directory_tree + "\n\n" + "\n".join(content_sections)

# --- Exclusion/Inclusion Logic ---

def should_exclude(
    path: str,
    base_path: str,
    exclude_patterns: List[str],
    verbose: bool = False
) -> bool:
    """Return True if the path matches any exclude pattern."""
    rel_path = os.path.relpath(path, start=base_path)
    for pattern in exclude_patterns:
        if fnmatchcase(rel_path, pattern):
            if verbose:
                logging.debug(
                    color_text(f"Excluded: {rel_path} (matches pattern '{pattern}')", YELLOW)
                )
            return True
    return False

def should_include(
    path: str,
    base_path: str,
    include_patterns: List[str],
    verbose: bool = False
) -> bool:
    """Return True if the path matches any include pattern (or if no patterns provided)."""
    if not include_patterns:  # Include everything by default if no patterns are provided
        return True
    rel_path = os.path.relpath(path, start=base_path)
    for pattern in include_patterns:
        if fnmatchcase(rel_path, pattern):
            if verbose:
                logging.debug(
                    color_text(f"Included: {rel_path} (matches pattern '{pattern}')", GREEN)
                )
            return True
    return False

def scan_directory(
    path: str,
    exclude_patterns: List[str],
    include_patterns: List[str],
    verbose: bool,
    ignore_hidden: bool
) -> List[Dict]:
    """
    Walk through the directory, collecting valid files based on
    exclusion and inclusion patterns, ignoring hidden files if required.
    """
    collected_files = []

    for root, dirs, files in os.walk(path):
        # Optionally remove hidden directories
        if ignore_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            files = [f for f in files if not f.startswith(".")]

        # Remove excluded directories
        dirs[:] = [
            d for d in dirs
            if not should_exclude(os.path.join(root, d), path, exclude_patterns, verbose)
        ]

        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Apply file exclusion and inclusion checks
            if (
                not should_exclude(file_path, path, exclude_patterns, verbose)
                and should_include(file_path, path, include_patterns, verbose)
                and is_text_file(file_path)
            ):
                content = read_file_content(file_path)
                file_info = {
                    "path": os.path.relpath(file_path, start=path),
                    "content": content,
                    "size": os.path.getsize(file_path),
                    "lines": len(content.splitlines()),
                }
                collected_files.append(file_info)
                
                if verbose:
                    logging.debug(
                        color_text(f"Processed file: {file_path}", GREEN)
                    )

    return collected_files

# --- Git-Related Functions ---

def clone_repo(url: str, target_dir: str, branch: Optional[str] = None):
    """Clone a remote Git repository into target_dir using a shallow clone."""
    cmd = ["git", "clone", "--depth=1"]
    if branch:
        cmd += ["--branch", branch]
    cmd += [url, target_dir]
    logging.info(f"Cloning repository: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(color_text(f"Git clone failed: {e.stderr}", RED))
        raise

def extract_repo_content(
    input_path: str,
    exclude: List[str],
    select: List[str],
    branch: Optional[str],
    verbose: bool,
    dry_run: bool,
    ignore_hidden: bool
):
    """
    Extract content from either a GitHub repo or local directory.
    If dry_run is True, we only simulate the process (no files written).
    """
    # Determine the repository name, e.g., "repo" from "https://github.com/user/repo"
    # or the basename of a local directory.
    repo_name = get_repo_name(input_path)
    output_folder = os.path.join("output", repo_name)

    # If this is a real run, create the output folder
    if not dry_run:
        os.makedirs(output_folder, exist_ok=True)

    if is_github_url(input_path):
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
        # If local repositories are allowed
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

def process_directory(
    path: str,
    exclude: List[str],
    select: List[str],
    verbose: bool,
    dry_run: bool,
    ignore_hidden: bool,
    output_folder: str
):
    """Scan a local directory, create directory tree, and optionally write outputs."""
    logging.info(f"Scanning directory: {path}")
    files = scan_directory(path, exclude, select, verbose, ignore_hidden)
    directory_tree = create_directory_tree(path)
    final_content = create_file_content_string(files, directory_tree)

    # Prepare final file paths
    code_file = os.path.join(output_folder, "code.txt")
    metadata_file = os.path.join(output_folder, "metadata.txt")

    if not dry_run:
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
    else:
        logging.info(color_text("[DRY RUN] Files processed but no output written.", YELLOW))

# --- Main CLI Entry Point ---

def main():
    parser = argparse.ArgumentParser(
        description="Extract repository or directory content into code + metadata outputs."
    )
    parser.add_argument("input_path", help="GitHub repository URL or local directory")
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Patterns to exclude (e.g., '*.md', 'test/*')"
    )
    parser.add_argument(
        "--select",
        nargs="*",
        default=[],
        help="Patterns to include (default: all text files)"
    )
    parser.add_argument("--branch", help="Branch to checkout if cloning a repository")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--dry-run", action="store_true", help="Simulate processing without writing files")
    parser.add_argument(
        "--ignore-hidden",
        action="store_true",
        help="Ignore hidden files and directories (those starting with a dot)"
    )
    # Optional: read exclude patterns from file
    parser.add_argument(
        "--exclude-from",
        help="File containing exclusion patterns (one pattern per line)"
    )
    # Optional: read select patterns from file
    parser.add_argument(
        "--select-from",
        help="File containing selection patterns (one pattern per line)"
    )

    args = parser.parse_args()

    # --- Setup Logging ---
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # --- Load patterns from files if provided ---
    exclude_patterns = args.exclude
    if args.exclude_from:
        try:
            with open(args.exclude_from, "r", encoding="utf-8") as f:
                file_excludes = [line.strip() for line in f if line.strip()]
            exclude_patterns += file_excludes
        except Exception as e:
            logging.error(f"Failed to read exclude-from file: {e}")
            sys.exit(1)

    select_patterns = args.select
    if args.select_from:
        try:
            with open(args.select_from, "r", encoding="utf-8") as f:
                file_selects = [line.strip() for line in f if line.strip()]
            select_patterns += file_selects
        except Exception as e:
            logging.error(f"Failed to read select-from file: {e}")
            sys.exit(1)

    # --- Perform Extraction ---
    try:
        extract_repo_content(
            input_path=args.input_path,
            exclude=exclude_patterns,
            select=select_patterns,
            branch=args.branch,
            verbose=args.verbose,
            dry_run=args.dry_run,
            ignore_hidden=args.ignore_hidden,
        )
    except Exception as e:
        logging.error(color_text(f"Error: {e}", RED))
        sys.exit(1)


if __name__ == "__main__":
    main()
