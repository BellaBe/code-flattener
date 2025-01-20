import os
import logging
from fnmatch import fnmatchcase
from utils.color import color_text, YELLOW

def should_exclude(
    path: str,
    base_path: str,
    exclude_patterns,
    verbose: bool = False
) -> bool:
    """
    Check if a file should be excluded based on patterns.
    """
    rel_path = os.path.relpath(path, start=base_path)
    for pattern in exclude_patterns:
        if fnmatchcase(rel_path, pattern):
            if verbose:
                logging.debug(color_text(
                    f"Excluded: {rel_path} (matches pattern '{pattern}')",
                    YELLOW
                ))
            return True
    return False


