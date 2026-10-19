#!/usr/bin/env python3
"""Filter and summarize a small, documented Linux-style log format.

Only the Python standard library is used. Run with --help for examples.
"""

import argparse
import csv
import os
from pathlib import Path
import re
import sys


LOG_PATTERN = (
    r"^(?P<timestamp>[A-Za-z]{3,9}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<service>[A-Za-z0-9_.-]+)\[(?P<pid>\d+)\]:\s+"
    r"(?P<level>INFO|WARN|ERROR)\s+(?P<message>.+)$"
)
OUTPUT_FILENAMES = ("filtered.log", "summary.csv", "analysis_report.md")


def parse_log_line(line):
    """Return parsed fields, or None when a nonblank line is unsupported."""
    raw = line.rstrip("\r\n")
    result = re.search(LOG_PATTERN, raw, flags=re.IGNORECASE)
    if result is None:
        return None

    record = result.groupdict()
    record["level"] = record["level"].upper()
    record["raw"] = raw
    return record


def matches_filters(record, levels, keywords):
    """Require the selected level and every literal, case-insensitive keyword."""
    if levels and record["level"] not in levels:
        return False

    searchable_text = record["raw"].casefold()
    for keyword in keywords:
        if keyword.casefold() not in searchable_text:
            return False
    return True


def analyze_log(log_file, levels=None, keywords=None):
    """Read one line at a time, retaining matching records and their counts."""
    levels = {level.upper() for level in (levels or [])}
    keywords = keywords or []
    totals = {
        "total_lines": 0,
        "parsed_lines": 0,
        "blank_lines": 0,
        "malformed_lines": 0,
        "matched_lines": 0,
    }
    matched_records = []
    level_counts = {}
    service_counts = {}
    message_counts = {}

    with open(log_file, mode="r", encoding="utf-8") as log_stream:
        for line in log_stream:
            totals["total_lines"] += 1
            if not line.strip():
                totals["blank_lines"] += 1
                continue

            record = parse_log_line(line)
            if record is None:
                totals["malformed_lines"] += 1
                continue

            totals["parsed_lines"] += 1
            if not matches_filters(record, levels, keywords):
                continue

            matched_records.append(record)
            totals["matched_lines"] += 1

            # The same dictionary-counting pattern learned in the course.
            level = record["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
            service = record["service"]
            service_counts[service] = service_counts.get(service, 0) + 1
            message = record["message"]
            message_counts[message] = message_counts.get(message, 0) + 1

    return {
        "totals": totals,
        "records": matched_records,
        "levels": level_counts,
        "services": service_counts,
        "messages": message_counts,
    }


def ranked_items(counts):
    """Sort by descending frequency, breaking ties alphabetically."""
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def markdown_text(value):
    """Keep user-supplied text readable inside Markdown table cells."""
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def write_outputs(analysis, log_file, output_dir, levels=None, keywords=None):
    """Create the three reports, refusing any output that aliases the input."""
    source = Path(log_file).expanduser().resolve()
    destination = Path(output_dir).expanduser()
    output_paths = [destination / name for name in OUTPUT_FILENAMES]

    for output_path in output_paths:
        if output_path.resolve() == source:
            raise ValueError("The output would overwrite the input log; choose another --output-dir.")
        if output_path.exists() and output_path.samefile(source):
            raise ValueError("An output is linked to the input log; choose another --output-dir.")

    destination.mkdir(parents=True, exist_ok=True)

    with open(output_paths[0], "w", encoding="utf-8", newline="\n") as output:
        for record in analysis["records"]:
            output.write(record["raw"] + "\n")

    with open(output_paths[1], "w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["dimension", "value", "count"])
        for metric, count in analysis["totals"].items():
            writer.writerow(["processing", metric, count])
        for dimension, key in (("level", "levels"), ("service", "services"), ("message", "messages")):
            for value, count in ranked_items(analysis[key]):
                writer.writerow([dimension, value, count])

    report_lines = [
        "# Log analysis report",
        "",
        "Source: " + markdown_text(log_file),
        "",
        "Levels: " + (", ".join(levels) if levels else "ALL (INFO, WARN, ERROR)"),
        "",
        "Required keywords (literal AND search, case-insensitive): "
        + (", ".join(markdown_text(word) for word in (keywords or [])) or "none"),
        "",
        "## Processing",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
    ]
    for metric, count in analysis["totals"].items():
        report_lines.append("| " + metric + " | " + str(count) + " |")

    for title, key in (("Matched levels", "levels"), ("Matched services", "services"), ("Exact matched messages", "messages")):
        report_lines.extend(["", "## " + title, "", "| Value | Count |", "| --- | ---: |"])
        if analysis[key]:
            for value, count in ranked_items(analysis[key]):
                report_lines.append("| " + markdown_text(value) + " | " + str(count) + " |")
        else:
            report_lines.append("| No matches | 0 |")

    report_lines.extend([
        "",
        "Counts describe matching log lines, not confirmed incidents or root causes.",
        "The bundled sample is fictional. Review the source lines before drawing operational conclusions.",
        "",
    ])
    output_paths[2].write_text("\n".join(report_lines), encoding="utf-8")
    return output_paths


def build_parser():
    parser = argparse.ArgumentParser(
        description="Filter and count INFO/WARN/ERROR lines in the documented sample log format."
    )
    parser.add_argument("log_file", help="Input UTF-8 log file, for example data/sample_system.log")
    parser.add_argument(
        "--level", nargs="+", type=str.upper, choices=["INFO", "WARN", "ERROR"],
        help="Optional allowed levels. The default includes all three."
    )
    parser.add_argument(
        "--keyword", action="append", default=[],
        help="Required literal text in the whole log line; repeat for AND search. Case-insensitive."
    )
    parser.add_argument(
        "--output-dir", default=os.environ.get("LOG_LAB_OUTPUT") or "output",
        help="Report folder. Default: LOG_LAB_OUTPUT environment variable, otherwise output."
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if any(not keyword.strip() for keyword in args.keyword):
        parser.error("--keyword must contain at least one non-whitespace character")

    source = Path(args.log_file).expanduser()
    try:
        analysis = analyze_log(source, args.level, args.keyword)
        outputs = write_outputs(analysis, source, args.output_dir, args.level, args.keyword)
    except (OSError, UnicodeError, ValueError) as error:
        print("Error: " + str(error), file=sys.stderr)
        return 1

    totals = analysis["totals"]
    print("Read: " + str(source))
    print("Total lines: " + str(totals["total_lines"]))
    print("Parsed lines: " + str(totals["parsed_lines"]))
    print("Skipped blank lines: " + str(totals["blank_lines"]))
    print("Skipped malformed lines: " + str(totals["malformed_lines"]))
    print("Matched lines: " + str(totals["matched_lines"]))
    for level, count in ranked_items(analysis["levels"]):
        print("  " + level + ": " + str(count))
    for output in outputs:
        print("Saved: " + str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
