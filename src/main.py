import argparse
import os
import subprocess
import sys
import tempfile
import json
from fnmatch import fnmatch
from typing import List, Dict, Optional

# Functional helpers
def compose(*functions):
    """Compose multiple functions into a single pipeline."""
    def composed(arg):
        for f in functions[::-1]:
            arg = f(arg)
        return arg
    return composed

# Pure utility functions
def is_github_url(path: str) -> bool:
    return path.startswith("http://") or path.startswith("https://")

def is_text_file(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
        return b'\x00' not in chunk
    except Exception:
        return False

def read_file_content(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def should_exclude(path: str, base_path: str, exclude_patterns: List[str]) -> bool:
    rel_path = os.path.relpath(path, start=base_path)
    return any(fnmatch(rel_path, pattern) for pattern in exclude_patterns)

def should_include(path: str, base_path: str, select_patterns: List[str]) -> bool:
    if not select_patterns:
        return True
    rel_path = os.path.relpath(path, start=base_path)
    return any(fnmatch(rel_path, pattern) for pattern in select_patterns)

def create_directory_tree(path: str) -> str:
    tree = []
    def build_tree(dir_path, prefix=""):
        entries = sorted(e for e in os.listdir(dir_path) if e != '.git')
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
    separator = "=" * 48 + "\n"
    content_sections = [
        f"{separator}File: {f['path']} ({f['lines']} lines, {f['size']} bytes)\n{separator}{f['content']}\n"
        for f in files
    ]
    return directory_tree + "\n\n" + "\n".join(content_sections)

def scan_directory(path: str, exclude_patterns: List[str], select_patterns: List[str], verbose: bool) -> List[Dict]:
    def collect_file_info(file_path: str):
        content = read_file_content(file_path)
        return {
            "path": os.path.relpath(file_path, start=path),
            "content": content,
            "size": os.path.getsize(file_path),
            "lines": len(content.splitlines()),
        }

    def is_valid_file(file_path: str) -> bool:
        return (
            not should_exclude(file_path, path, exclude_patterns)
            and is_text_file(file_path)
            and should_include(file_path, path, select_patterns)
        )

    collected_files = []
    for root, dirs, files in os.walk(path):
        if '.git' in dirs:
            dirs.remove('.git')
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if is_valid_file(file_path):
                collected_files.append(collect_file_info(file_path))
                if verbose:
                    print(f"[VERBOSE] Included {file_path}")
    return collected_files

def clone_repo(url: str, target_dir: str, branch: Optional[str] = None):
    cmd = ["git", "clone", "--depth=1"]
    if branch:
        cmd += ["--branch", branch]
    cmd += [url, target_dir]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

def extract_repo_content(input_path: str, exclude: List[str], select: List[str], branch: Optional[str], verbose: bool, output: str):
    if is_github_url(input_path):
        if verbose:
            print(f"[VERBOSE] Cloning remote repository: {input_path}")
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = os.path.join(tmpdir, "repo")
            clone_repo(input_path, repo_dir, branch)
            process_directory(repo_dir, exclude, select, verbose, output)
    else:
        if not os.path.isdir(input_path):
            raise ValueError(f"Provided path {input_path} is not a valid directory.")
        process_directory(input_path, exclude, select, verbose, output)

def process_directory(path: str, exclude: List[str], select: List[str], verbose: bool, output: str):
    files = scan_directory(path, exclude, select, verbose)
    directory_tree = create_directory_tree(path)
    final_content = create_file_content_string(files, directory_tree)
    
    with open(output, "w", encoding="utf-8") as f:
        f.write(final_content)
    with open("output.json", "w", encoding="utf-8") as jf:
        json.dump({"files": files}, jf, indent=2)
    print(f"Content extracted to {output} and output.json")

def main():
    parser = argparse.ArgumentParser(description="Extract repository content into a single text file and JSON.")
    parser.add_argument("input_path", help="GitHub repository URL or local directory")
    parser.add_argument("--exclude", nargs="*", default=[], help="Patterns to exclude (e.g., '*.md', '*.png')")
    parser.add_argument("--select", nargs="*", default=[], help="Patterns to include (default: all text files)")
    parser.add_argument("--branch", help="Branch to checkout if cloning a repository")
    parser.add_argument("--output", default="output.txt", help="Output file name (default: output.txt)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    try:
        extract_repo_content(args.input_path, args.exclude, args.select, args.branch, args.verbose, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
