import os
import logging
from functools import partial

from utils.color import color_text, GREEN
from utils.filesystem import is_text_file, read_file_content
from filters.exclude import should_exclude
from filters.include import should_include


def build_directory_tree_lines(dir_path: str, prefix: str = ""):
    """
    Recursively create lines for a directory tree.
    """
    try:
        entries = sorted(e for e in os.listdir(dir_path) if e != ".git")
    except PermissionError:
        return [prefix + "[Permission Denied]"]

    lines = []
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        full_path = os.path.join(dir_path, entry)
        lines.append(prefix + connector + entry)

        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
            lines.extend(build_directory_tree_lines(full_path, new_prefix))

    return lines

def create_directory_tree(path: str) -> str:
    """
    Creates a human-readable directory tree as a single string.
    """
    lines = build_directory_tree_lines(path)
    return "Directory structure:\n" + "\n".join(lines)

def scan_directory(
    path: str,
    exclude_patterns,
    include_patterns,
    verbose: bool,
    ignore_hidden: bool
):
    """
    Walk through the directory, collecting valid text files.
    """
    all_files = []
    for root, dirs, files in os.walk(path):
        exclude_fn = partial(
            should_exclude,
            base_path=path,
            exclude_patterns=exclude_patterns,
            verbose=verbose
        )

        # Filter out hidden dirs if needed
        if ignore_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
        # Remove excluded dirs
        dirs[:] = [d for d in dirs if not exclude_fn(os.path.join(root, d))]

        # Filter out hidden files if requested
        if ignore_hidden:
            files = [f for f in files if not f.startswith('.')]

        for fname in files:
            file_path = os.path.join(root, fname)
            if (
                not exclude_fn(file_path)
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
                all_files.append(file_info)

                if verbose:
                    logging.debug(color_text(f"Processed file: {file_path}", GREEN))

    return all_files
