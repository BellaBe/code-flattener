import os
import logging
from fnmatch import fnmatchcase
from utils.color import color_text, GREEN


def should_include(
    path: str,
    base_path: str,
    include_patterns,
    verbose: bool = False
) -> bool:
    """
    Check if a file should be included based on patterns.
    """
    if not include_patterns:
        return True

    rel_path = os.path.relpath(path, start=base_path)
    for pattern in include_patterns:
        if fnmatchcase(rel_path, pattern):
            if verbose:
                logging.debug(color_text(
                    f"Included: {rel_path} (matches pattern '{pattern}')",
                    GREEN
                ))
            return True
    return False