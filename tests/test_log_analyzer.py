"""Acceptance checks with hand-counted expectations and real CLI invocations."""

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import log_analyzer

SAMPLE = ROOT / "data" / "sample_system.log"
EXPECTED = json.loads((ROOT / "data" / "expected_results.json").read_text(encoding="utf-8"))


def run_cli(*arguments, env=None):
    return subprocess.run(
        [sys.executable, str(ROOT / "src" / "log_analyzer.py"), *map(str, arguments)],
        capture_output=True, text=True, env=env,
    )


class AnalysisAcceptanceTests(unittest.TestCase):
    def test_full_sample_matches_hand_counted_totals(self):
        result = log_analyzer.analyze_log(SAMPLE)
        expected = EXPECTED["all"]
        for metric in result["totals"]:
            self.assertEqual(result["totals"][metric], expected[metric])
        self.assertEqual(result["levels"], expected["levels"])
        self.assertEqual(result["services"], expected["services"])

    def test_network_failures_include_warn_and_error(self):
        expected = EXPECTED["network_failures"]
        result = log_analyzer.analyze_log(SAMPLE, keywords=expected["keywords"])
        self.assertEqual(result["totals"]["matched_lines"], expected["matched_lines"])
        for dimension in ("levels", "services", "messages"):
            self.assertEqual(result[dimension], expected[dimension])

    def test_warn_network_failures_are_not_lost(self):
        result = log_analyzer.analyze_log(SAMPLE, ["WARN"], ["network", "failed"])
        self.assertEqual(result["totals"]["matched_lines"], 4)
        self.assertEqual(result["levels"], {"WARN": 4})

    def test_errors_only(self):
        result = log_analyzer.analyze_log(SAMPLE, ["ERROR"])
        self.assertEqual(result["totals"]["matched_lines"], 12)
        self.assertEqual(result["levels"], {"ERROR": 12})

    def test_level_and_keyword_search_are_case_insensitive(self):
        result = log_analyzer.analyze_log(SAMPLE, ["warn"], ["NETWORK", "FaIlEd"])
        self.assertEqual(result["totals"]["matched_lines"], 4)

    def test_all_keywords_are_required(self):
        result = log_analyzer.analyze_log(SAMPLE, keywords=["network", "failed", "updater"])
        self.assertEqual(result["totals"]["matched_lines"], 1)
        self.assertEqual(result["services"], {"updater": 1})

    def test_keyword_order_is_not_phrase_order(self):
        result = log_analyzer.analyze_log(SAMPLE, keywords=["failed", "network"])
        self.assertEqual(result["totals"]["matched_lines"], 9)

    def test_dot_keyword_is_literal_not_a_wildcard(self):
        result = log_analyzer.analyze_log(SAMPLE, keywords=["."])
        self.assertEqual(result["totals"]["matched_lines"], 0)

    def test_bracket_keyword_does_not_raise_a_regex_error(self):
        result = log_analyzer.analyze_log(SAMPLE, keywords=["["])
        self.assertEqual(result["totals"]["matched_lines"], 40)

    def test_unsupported_line_is_not_parsed(self):
        self.assertIsNone(log_analyzer.parse_log_line("Not a supported log line\n"))

    def test_parser_keeps_fields_and_normalizes_level(self):
        record = log_analyzer.parse_log_line(
            "July 31 00:06:21 lab-host worker-agent[42]: warn Netzwerkprüfung failed\n"
        )
        self.assertEqual(record["timestamp"], "July 31 00:06:21")
        self.assertEqual(record["service"], "worker-agent")
        self.assertEqual(record["pid"], "42")
        self.assertEqual(record["level"], "WARN")
        self.assertEqual(record["message"], "Netzwerkprüfung failed")


class CommandLineAcceptanceTests(unittest.TestCase):
    def test_exports_filtered_log_csv_and_markdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "reports"
            result = run_cli(SAMPLE, "--keyword", "network", "--keyword", "failed", "--output-dir", output_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn("Matched lines: 9", result.stdout)
            lines = (output_dir / "filtered.log").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 9)
            self.assertTrue(all("network" in line.casefold() and "failed" in line.casefold() for line in lines))
            with open(output_dir / "summary.csv", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertIn({"dimension": "level", "value": "WARN", "count": "4"}, rows)
            self.assertIn({"dimension": "service", "value": "NetworkManager", "count": "6"}, rows)
            self.assertIn("| matched_lines | 9 |", (output_dir / "analysis_report.md").read_text(encoding="utf-8"))

    def test_no_matches_is_a_successful_search(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run_cli(SAMPLE, "--keyword", "no-such-event", "--output-dir", temporary)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Matched lines: 0", result.stdout)
            self.assertEqual((Path(temporary) / "filtered.log").read_text(encoding="utf-8"), "")

    def test_missing_input_returns_one_and_writes_error_to_stderr(self):
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "reports"
            result = run_cli(Path(temporary) / "missing.log", "--output-dir", output_dir)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("Error:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(output_dir.exists())

    def test_invalid_level_returns_two(self):
        result = run_cli(SAMPLE, "--level", "DEBUG")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)

    def test_blank_keyword_returns_two(self):
        result = run_cli(SAMPLE, "--keyword", "   ")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--keyword", result.stderr)

    def test_input_cannot_be_overwritten_by_an_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "filtered.log"
            original = "Oct 19 08:00:01 lab-host worker[1]: INFO Training message\n"
            source.write_text(original, encoding="utf-8")
            result = run_cli(source, "--output-dir", temporary)
            self.assertEqual(result.returncode, 1)
            self.assertIn("overwrite the input", result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_invalid_utf8_returns_one(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "invalid.log"
            source.write_bytes(b"\xff\xfe invalid UTF-8")
            result = run_cli(source, "--output-dir", Path(temporary) / "reports")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Error:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_output_path_that_is_a_file_returns_one(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "not-a-directory"
            destination.write_text("Keep this file", encoding="utf-8")
            result = run_cli(SAMPLE, "--output-dir", destination)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(destination.read_text(encoding="utf-8"), "Keep this file")

    def test_environment_variable_sets_default_output_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = os.environ.copy()
            environment["LOG_LAB_OUTPUT"] = str(Path(temporary) / "from-environment")
            result = run_cli(SAMPLE, "--keyword", "network", env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(environment["LOG_LAB_OUTPUT"]) / "summary.csv").is_file())

    def test_explicit_output_folder_overrides_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = os.environ.copy()
            environment["LOG_LAB_OUTPUT"] = str(Path(temporary) / "not-selected")
            explicit = Path(temporary) / "selected"
            result = run_cli(SAMPLE, "--output-dir", explicit, env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((explicit / "summary.csv").is_file())
            self.assertFalse(Path(environment["LOG_LAB_OUTPUT"]).exists())

    def test_empty_file_is_successful_with_zero_counts(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "empty.log"
            source.write_text("", encoding="utf-8")
            result = run_cli(source, "--output-dir", Path(temporary) / "reports")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Total lines: 0", result.stdout)
            self.assertIn("Matched lines: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
