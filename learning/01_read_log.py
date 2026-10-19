#!/usr/bin/env python3
"""Step 1: read the file path from argv and print one line at a time."""

import sys

if len(sys.argv) != 2:
    print("Usage: python3 learning/01_read_log.py data/sample_system.log", file=sys.stderr)
    sys.exit(2)

logfile = sys.argv[1]
with open(logfile, encoding="utf-8") as log_stream:
    for line in log_stream:
        print(line.rstrip("\r\n"))
