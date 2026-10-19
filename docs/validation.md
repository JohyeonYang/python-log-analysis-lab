# Verification record

Initial verification date: **2026-10-19**.  
Runtime used: **Python 3.12.14 on Linux**.  
Result: **22 checks passed** with Python's standard-library `unittest`.

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The expected dataset counts were specified independently in `data/expected_results.json`. They are not calculated by the analyzer to produce its own expected answer.

## Coverage

| Area | Checked behavior |
| --- | --- |
| Baseline | 44 physical lines, 40 records, 2 blanks, 2 malformed lines; expected severity and service counts |
| Network failure search | 9 records, including 4 WARN and 5 ERROR; expected services and messages |
| Level filtering | WARN network failures: 4; ERROR-only records: 12 |
| Search meaning | All keywords required; keyword order independent; case-insensitive matching |
| Literal keywords | A dot is not a regex wildcard; a bracket does not raise a regex error |
| Parsing | Unsupported lines skipped; fields extracted; severity normalized; UTF-8 message preserved |
| Output integration | Real CLI produces filtered log, CSV, and Markdown with expected content |
| Empty results | Zero matches and an empty input are successful searches |
| Input errors | Missing file and invalid UTF-8 return 1 and an error on STDERR |
| Usage errors | Unsupported severity and blank keyword return 2 |
| Output errors | Output path that is a file returns 1; input/output aliasing is rejected without changing the source |
| Configuration | Environment default honored; explicit output folder overrides it |

## Acceptance commands

| Search | Expected matches | Expected levels |
| --- | ---: | --- |
| No filters | 40 | INFO 14, WARN 14, ERROR 12 |
| `--keyword network --keyword failed` | 9 | WARN 4, ERROR 5 |
| `--level WARN --keyword network --keyword failed` | 4 | WARN 4 |
| `--level ERROR` | 12 | ERROR 12 |
| `--keyword no-such-event` | 0 | none |

The example outputs under `examples/network-failures/` are generated from the supplied sample with the documented network-failure command. CSV dimensions describe matching log lines. These checks do not establish universal syslog support, production readiness, a root cause, or a benchmark for very large files.

Use the learning journal to record checks you perform after making your own changes.
