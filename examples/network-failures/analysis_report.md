# Log analysis report

Source: data/sample_system.log

Levels: ALL (INFO, WARN, ERROR)

Required keywords (literal AND search, case-insensitive): network, failed

## Processing

| Metric | Count |
| --- | ---: |
| total_lines | 44 |
| parsed_lines | 40 |
| blank_lines | 2 |
| malformed_lines | 2 |
| matched_lines | 9 |

## Matched levels

| Value | Count |
| --- | ---: |
| ERROR | 5 |
| WARN | 4 |

## Matched services

| Value | Count |
| --- | ---: |
| NetworkManager | 6 |
| CRON | 1 |
| kernel | 1 |
| updater | 1 |

## Exact matched messages

| Value | Count |
| --- | ---: |
| Failed to start network connection | 6 |
| Failed to start network check job USER (ops_user) | 1 |
| Network driver failed to initialize | 1 |
| Network package update failed | 1 |

Counts describe matching log lines, not confirmed incidents or root causes.
The bundled sample is fictional. Review the source lines before drawing operational conclusions.
