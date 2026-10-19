#!/usr/bin/env python3
"""Step 2: skip lines without the literal WARN text."""

import sys

if len(sys.argv) != 2:
    print("Usage: python3 learning/02_filter_warn.py data/sample_system.log", file=sys.stderr)
    sys.exit(2)

logfile = sys.argv[1]
with open(logfile, encoding="utf-8") as log_stream:
    for line in log_stream:
        if "WARN" not in line:
            continue
        print(line.rstrip("\r\n"))
