import sys
import logging
from cli import parse_arguments
from utils.color import color_text, RED
from extraction import extract_repo_content

def main():
    """
    IMPURE (sets up logging, orchestrates the program).
    """
    args = parse_arguments()

    # --- Setup Logging ---
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # --- Perform Extraction ---
    try:
        extract_repo_content(
            input_path=args.input_path,
            exclude=args.exclude,
            select=args.select,
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
