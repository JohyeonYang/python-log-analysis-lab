#!/usr/bin/env python3
"""Step 4: let a parent Python process run the analyzer and check its result."""

from pathlib import Path
import subprocess
import sys

project = Path(__file__).resolve().parents[1]
command = [
    sys.executable,
    str(project / "src" / "log_analyzer.py"),
    str(project / "data" / "sample_system.log"),
    "--keyword", "network",
    "--keyword", "failed",
    "--output-dir", str(project / "output" / "subprocess-run"),
]

result = subprocess.run(command, capture_output=True, text=True)
print("Child process exit code:", result.returncode)
if result.stdout:
    print(result.stdout, end="")
if result.stderr:
    print(result.stderr, end="", file=sys.stderr)

sys.exit(result.returncode)
