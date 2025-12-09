# core/formatter.py
import subprocess
from pathlib import Path
from typing import Tuple

def run_black(file_path: str) -> Tuple[bool, str]:
    """
    Run black on the file in place. Returns (success, output_text).
    If black is not installed or fails, returns False with error text.
    """
    try:
        # --quiet to minimize output, --fast to skip safety checks for speed
        res = subprocess.run(
            ["black", "--quiet", "--fast", file_path],
            capture_output=True,
            text=True,
            check=False,
        )
        out = res.stdout + res.stderr
        success = res.returncode == 0
        return success, out.strip()
    except FileNotFoundError as e:
        return False, f"black not found: {e}"
    except Exception as e:
        return False, str(e)

def get_formatted_copy(src_path: str, dest_path: str) -> Tuple[bool, str]:
    """
    Format src_path with black and copy result to dest_path.
    Returns (success, message)
    """
    success, out = run_black(src_path)
    if not success and "not found" in out.lower():
        return False, out
    try:
        content = Path(src_path).read_text(encoding="utf-8")
        Path(dest_path).write_text(content, encoding="utf-8")
        return True, "Formatted file written to " + dest_path
    except Exception as e:
        return False, str(e)
