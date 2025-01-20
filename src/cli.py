import argparse

def parse_arguments():
    """
    Parse command-line arguments.
    """
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

    return parser.parse_args()

