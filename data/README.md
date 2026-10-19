# Fictional sample data

`sample_system.log` was written for this lab. Names, services, timestamps, and messages are training examples, not evidence from a real server or employer.

| Property | Expected value |
| --- | ---: |
| Physical lines | 44 |
| Parsed records | 40 |
| Blank lines | 2 |
| Intentionally malformed nonblank lines | 2 |
| INFO records | 14 |
| WARN records | 14 |
| ERROR records | 12 |

Required format:

```text
MONTH DAY HH:MM:SS HOST SERVICE[PID]: LEVEL MESSAGE
```

`network` AND `failed`, ignoring case and with no level restriction, matches 9 records: 5 ERROR and 4 WARN. Their services are NetworkManager (6), CRON (1), updater (1), and kernel (1).

`expected_results.json` is a hand-specified acceptance reference. Tests compare the analyzer with these counts. Keep the baseline data unchanged while doing exercises: copy it into `output/practice.log` for your own additions.

Only matched records are included in the level/service/message summary dimensions. Blank and malformed line counts describe the complete input file.
