# core/code_analysis.py

import subprocess

import json

from typing import Dict, Any, List, Tuple


def run_flake8(file_path: str) -> List[Dict[str, Any]]:
    """

    Runs flake8 on the provided file and returns a list of issues.

    Each issue is a dict: {line, col, code, message}

    """

    try:

        # Using flake8 CLI for predictable output

        proc = subprocess.run(
            ["flake8", "--format=%(row)d:%(col)d:%(code)s:%(text)s", file_path],
            capture_output=True,
            text=True,
            check=False,
        )

        text = proc.stdout.strip()

        issues = []

        if text:

            for line in text.splitlines():

                # format was row:col:CODE:message

                parts = line.split(":", 3)

                if len(parts) == 4:

                    row, col, code, message = parts

                    issues.append(
                        {
                            "line": int(row),
                            "col": int(col),
                            "code": code,
                            "message": message.strip(),
                        }
                    )

        return issues

    except FileNotFoundError:

        return [{"error": "flake8 not installed or not found in PATH."}]

    except Exception as e:

        return [{"error": str(e)}]


def run_radon_cc(file_path: str) -> Dict[str, Any]:
    """

    Runs radon cc in JSON mode to get cyclomatic complexity per block.

    Returns parsed JSON or an error dict.

    """

    try:

        proc = subprocess.run(
            ["radon", "cc", "-s", "-j", file_path],
            capture_output=True,
            text=True,
            check=False,
        )

        if proc.stdout:

            parsed = json.loads(proc.stdout)

            return parsed

        else:

            # radon may write to stderr on errors

            out = proc.stderr.strip() or proc.stdout.strip()

            if out:

                return {"error": out}

            return {}

    except FileNotFoundError:

        return {"error": "radon not installed or not found in PATH."}

    except Exception as e:

        return {"error": str(e)}


def run_radon_mi(file_path: str) -> Dict[str, Any]:
    """

    Gets maintainability index from radon mi with JSON output (if supported) otherwise parse text.

    """

    try:

        proc = subprocess.run(
            ["radon", "mi", "-j", file_path],
            capture_output=True,
            text=True,
            check=False,
        )

        if proc.stdout:

            parsed = json.loads(proc.stdout)

            return parsed

        else:

            out = proc.stderr.strip() or proc.stdout.strip()

            if out:

                return {"error": out}

            return {}

    except FileNotFoundError:

        return {"error": "radon not installed or not found in PATH."}

    except Exception as e:

        return {"error": str(e)}


def analyze_file(file_path: str) -> Dict[str, Any]:
    """

    Combined analysis: flake8 issues + radon complexity + maintainability index

    """

    report = {}

    report["flake8_issues"] = run_flake8(file_path)

    report["radon_cc"] = run_radon_cc(file_path)

    report["radon_mi"] = run_radon_mi(file_path)

    return report
