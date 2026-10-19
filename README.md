# Python Log Analysis Lab

A small Python command-line tool for filtering and summarizing fictional Linux-style logs. It connects file processing, regular expressions, dictionary counting, command-line arguments, environment variables, exit codes, and subprocesses to an IT support workflow.

**한국어로 처음 시작하기: [START_HERE_KO.md](START_HERE_KO.md)**

## The support problem

A search that always requires the word `error` can miss a failed operation logged at `WARN` level. In this lab, searching for both `network` and `failed` finds **9 lines: 5 ERROR and 4 WARN**. Requiring ERROR would retain only 5 of those lines.

The tool separates severity filtering from keyword filtering, counts the matching evidence, and exports results that can accompany a support ticket. It does not infer the root cause of a network incident.

## Quick start

Use Python 3.10 or newer. No third-party packages, account, network access, or administrator privileges are required to run this project. The supplied logs are fictional.

Run commands from the project root:

```bash
python3 src/log_analyzer.py data/sample_system.log --keyword network --keyword failed --output-dir output/network
```

Expected console summary:

```text
Read: data/sample_system.log
Total lines: 44
Parsed lines: 40
Skipped blank lines: 2
Skipped malformed lines: 2
Matched lines: 9
  ERROR: 5
  WARN: 4
Saved: output/network/filtered.log
Saved: output/network/summary.csv
Saved: output/network/analysis_report.md
```

On Windows, use `py -3` in place of `python3` if that is how Python is installed. The implementation uses `pathlib` for paths; the recorded verification was performed on Linux with Python 3.12.14.

## What it does

- Reads a UTF-8 file one physical line at a time.
- Extracts timestamp, host, service, PID, level, and message with a regular expression.
- Optionally selects one or more of `INFO`, `WARN`, and `ERROR`.
- Searches the **whole original log line** for each required literal keyword, ignoring case. Repeated keywords use **AND** semantics; their order does not matter.
- Counts matching lines by severity, service, and exact message text with dictionaries.
- Reports blank and unsupported lines separately.
- Writes a filtered log, a CSV summary, and a Markdown report.
- Reads an optional output-folder setting from an environment variable.
- Returns documented process exit codes for successful searches and errors.

Regex is used to parse the log structure. Keywords are literal text, not user-supplied regex. For example, `--keyword "["` searches for an actual opening bracket.

## Commands to try

All supported records, with no keyword restriction:

```bash
python3 src/log_analyzer.py data/sample_system.log
```

Only ERROR records; expected matches: **12**:

```bash
python3 src/log_analyzer.py data/sample_system.log --level ERROR --output-dir output/errors
```

WARN-level network failures; expected matches: **4**:

```bash
python3 src/log_analyzer.py data/sample_system.log --level WARN --keyword network --keyword failed --output-dir output/network-warn
```

Select either WARN or ERROR:

```bash
python3 src/log_analyzer.py data/sample_system.log --level WARN ERROR --output-dir output/warn-and-error
```

No matching records; expected matches: **0**, exit code: **0**:

```bash
python3 src/log_analyzer.py data/sample_system.log --keyword no-such-event --output-dir output/no-matches
```

Help:

```bash
python3 src/log_analyzer.py --help
```

## Outputs

| File | Contents |
| --- | --- |
| `filtered.log` | Matching original lines, written with LF line endings, in input order |
| `summary.csv` | `dimension,value,count` rows for processing totals and matched levels, services, and messages |
| `analysis_report.md` | Search settings, processing totals, and tables of matched evidence |

`processing` rows in the CSV describe the full input. `level`, `service`, and `message` rows describe **only matched records**. Message grouping uses the exact message text, so messages with different embedded usernames or numbers remain separate.

Each run replaces these three output files in the chosen folder. An output that resolves or links to the source log is rejected. Generated working files under `output/` are ignored by Git; a reproducible example is included under [examples/network-failures/](examples/network-failures/).

## Environment variable exercise

On Ubuntu/Linux, set the default report folder for programs started from this terminal:

```bash
export LOG_LAB_OUTPUT=output/env-run
python3 src/log_analyzer.py data/sample_system.log --keyword network --keyword failed
unset LOG_LAB_OUTPUT
```

An explicit `--output-dir` takes precedence. Otherwise the tool uses `LOG_LAB_OUTPUT`, or `output` when the variable is absent or empty.

## Exit codes and standard streams

| Exit code | Meaning |
| --- | --- |
| `0` | Search and report creation succeeded, including an empty input or zero matches |
| `1` | Input/output, UTF-8 decoding, or source-overwrite protection error |
| `2` | Invalid command-line usage, such as a missing file argument, invalid level, or blank keyword |

Run information goes to STDOUT. Usage and operational error messages go to STDERR. An ERROR-level log entry is data: it does not itself make the analyzer exit with a failure code.

## Verification

```bash
python3 -m unittest discover -s tests -v
```

The initial implementation passed **22 checks** on Python 3.12.14. They use hand-specified sample counts and real subprocess invocations to check filtering, reports, no-match behavior, invalid arguments, missing input, UTF-8 errors, environment settings, and input preservation. See [docs/validation.md](docs/validation.md).

## Learn the implementation

| File or folder | Purpose |
| --- | --- |
| `src/log_analyzer.py` | Main runnable implementation |
| `data/sample_system.log` | 40 valid records, 2 blank lines, and 2 intentionally malformed lines |
| `data/expected_results.json` | Hand-specified acceptance counts |
| `learning/` | Four short stages: reading, filtering, counting, and running a child process |
| `docs/learning_guide_ko.md` | Korean explanation and small extension exercises |
| `docs/support_ticket_example.md` | Fictional ticket showing how the outputs support triage |
| `docs/learning_journal.md` | Template for recording your own changes and explanations |
| `docs/github_upload_ko.md` | Korean instructions for creating and uploading a GitHub repository |

## Scope

The parser supports this teaching format:

```text
MONTH DAY HH:MM:SS HOST SERVICE[PID]: LEVEL MESSAGE
```

It supports the three documented levels and one record per line. It is not a universal parser for JSON logs, journald, multiline tracebacks, or every syslog variant. Timestamps are extracted as text; calendar validation and time-window analysis are outside this version.

The input is read incrementally, but matching records and count dictionaries are retained in memory for reporting. This is a small-file learning tool, not a constant-memory or real-time monitoring service. Counts are log-line counts, not confirmed incident counts.

## Learning origin

The project is inspired by the file-processing, regular-expression, dictionary, and process-management concepts in Google's **Using Python to Interact with the Operating System** course. The initial implementation and documentation were prepared with ChatGPT assistance. The sample data was created for this lab; it is not a copy of a course log file. Record your own changes in the learning journal as you work through the project.

References are listed in [docs/references.md](docs/references.md). MIT license; see [LICENSE](LICENSE).
