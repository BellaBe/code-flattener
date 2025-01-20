import subprocess
import logging
from utils.color import color_text, RED

def clone_repo(url: str, target_dir: str, branch: str = None):
    """
    Clone a remote Git repository into target_dir using a shallow clone.
    """
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
