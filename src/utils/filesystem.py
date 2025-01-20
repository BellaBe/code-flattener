import os

def is_text_file(file_path: str) -> bool:
    """
    Checks if a file is likely text by looking for null bytes in the first 1KB.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
        return b'\x00' not in chunk
    except Exception:
        return False

def read_file_content(file_path: str) -> str:
    """
    Safely read file content, ignoring errors, returns a placeholder on failure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def get_repo_name(path_or_url: str) -> str:
    """
    Extract repository name from a GitHub URL or local path.
    """
    if path_or_url.startswith(("http://", "https://")):
        trimmed = path_or_url.rstrip("/")
        parts = trimmed.split("/")
        repo = parts[-1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return repo
    return os.path.basename(os.path.normpath(path_or_url))
