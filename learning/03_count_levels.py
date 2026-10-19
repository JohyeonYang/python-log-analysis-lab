#!/usr/bin/env python3
"""Step 3: extract the level with regex, then count with a dictionary."""

import re
import sys

if len(sys.argv) != 2:
    print("Usage: python3 learning/03_count_levels.py data/sample_system.log", file=sys.stderr)
    sys.exit(2)

level_counts = {}
with open(sys.argv[1], encoding="utf-8") as log_stream:
    for line in log_stream:
        result = re.search(r": (INFO|WARN|ERROR) ", line)
        if result is None:
            continue
        level = result[1]
        level_counts[level] = level_counts.get(level, 0) + 1

print(level_counts)
