# Fictional support ticket: repeated network-failure messages

**Ticket:** LAB-OPS-001  
**Environment:** supplied fictional training log  
**Status:** evidence collected; root cause not established

## Request

Review the sample for records containing both `network` and `failed`. Include warnings as well as errors so that the triage does not discard failed operations logged at WARN level.

## Reproduction

From the repository root:

```bash
python3 src/log_analyzer.py data/sample_system.log --keyword network --keyword failed --output-dir output/network
```

## Observed evidence

| Observation | Count |
| --- | ---: |
| Physical input lines | 44 |
| Parsed records | 40 |
| Blank lines | 2 |
| Unsupported nonblank lines | 2 |
| Matching records | 9 |
| Matching ERROR records | 5 |
| Matching WARN records | 4 |

Matching services: NetworkManager (6), CRON (1), updater (1), kernel (1).

The exact message `Failed to start network connection` appears 6 times in the matched records. Other matching lines concern a network check job, a package update, and a network driver.

## Interpretation

The sample shows that the same search topic spans more than one service and severity. Requiring ERROR would discard the 4 matching WARN records. The 9 records are not proof of 9 distinct network incidents; repeated messages may refer to a shared underlying event.

## Suggested next actions in a real support workflow

1. Review the original matching lines and their timestamps.
2. Compare network configuration, interface/driver state, and relevant recent changes.
3. Correlate related service messages before proposing a cause or a remediation.
4. Attach the filtered evidence and summary when escalating to the responsible team.

These are proposed investigation steps. No real server was investigated or changed in this lab.

## Attachments

- Reproducible example: [filtered.log](../examples/network-failures/filtered.log)
- [summary.csv](../examples/network-failures/summary.csv)
- [analysis_report.md](../examples/network-failures/analysis_report.md)
