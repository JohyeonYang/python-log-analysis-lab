# 여기서 시작하세요 — python-log-analysis-lab

이 프로젝트는 **가상의 서버 로그에서 필요한 줄을 찾고, 등장 횟수를 집계하고, 결과를 파일로 정리하는 도구**입니다. IT Support·운영·자동화 업무의 작은 연습입니다.

처음에는 이 안내와 `learning/`의 짧은 파일부터 보세요. 완성된 도구는 바로 실행할 수 있습니다.

## 1. 준비하기

1. ZIP을 다운로드하고 압축을 풉니다.
2. 풀린 `python-log-analysis-lab` 폴더 안에서 터미널을 엽니다.
3. 아래 명령으로 Python을 확인합니다.

```bash
python3 --version
```

Python 3.10 이상을 사용합니다. 별도로 `pip install`할 패키지는 없습니다. 아래 명령은 Ubuntu/Linux 터미널 기준입니다.

## 2. 먼저 완성된 프로그램 실행하기

아래는 **한 줄짜리 명령**입니다.

```bash
python3 src/log_analyzer.py data/sample_system.log --keyword network --keyword failed --output-dir output/network
```

| 명령의 부분 | 의미 |
| --- | --- |
| `python3` | Python 3로 실행 |
| `src/log_analyzer.py` | 실행할 스크립트 |
| `data/sample_system.log` | 분석할 파일 경로 |
| `--keyword network` | `network`가 들어 있어야 함 |
| `--keyword failed` | `failed`도 들어 있어야 함 |
| `--output-dir output/network` | 결과를 저장할 폴더 |

대소문자는 구분하지 않습니다. 두 단어의 순서도 상관없습니다. 두 단어가 **모두** 있는 줄을 찾습니다.

`Matched lines: 9`가 나오면 예상과 같습니다. 그중 `ERROR`는 **5개**, `WARN`은 **4개**입니다.

이 프로젝트의 핵심 사례입니다. 실패했다고 해서 모든 줄이 ERROR인 것은 아닙니다. 실습 코드처럼 `error`를 필수 검색어로 넣으면 WARN으로 기록된 네트워크 실패 4줄을 놓칩니다.

`python3`를 명시하므로 실행 권한을 따로 설정하지 않아도 됩니다. 프로그램 첫 줄에도 올바른 shebang을 넣어 두었습니다.

## 3. 결과 확인하기

```bash
cat output/network/filtered.log
```

찾아낸 로그 9줄을 봅니다.

```bash
cat output/network/summary.csv
```

집계표를 봅니다. CSV 파일은 Excel 등의 프로그램에서도 열 수 있습니다.

```bash
cat output/network/analysis_report.md
```

검색 조건, 처리한 줄 수, 프로그램별 횟수 등을 정리한 보고서를 봅니다. Markdown을 지원하는 편집기나 GitHub에서는 표로 볼 수 있습니다.

## 4. 다른 조건으로 실행하기

전체 로그: 정상 형식 40줄, 빈 줄 2줄, 형식이 맞지 않는 줄 2줄입니다.

```bash
python3 src/log_analyzer.py data/sample_system.log
```

ERROR만 찾기: 12줄입니다.

```bash
python3 src/log_analyzer.py data/sample_system.log --level ERROR --output-dir output/errors
```

WARN이면서 `network`와 `failed`가 있는 줄: 4줄입니다.

```bash
python3 src/log_analyzer.py data/sample_system.log --level WARN --keyword network --keyword failed --output-dir output/network-warn
```

각 명령 뒤에 다음을 입력하면 직전 명령의 종료 코드를 확인합니다.

```bash
echo $?
```

정상적으로 검색과 저장이 끝났다면 0입니다. 로그에서 ERROR를 찾았다는 사실은 프로그램 실행 실패를 뜻하지 않습니다. 검색 결과가 0개여도 검색 자체가 끝났다면 0입니다.

결과 파일 세 개는 같은 출력 폴더로 다시 실행하면 새 결과로 바뀝니다.

## 5. 짧은 코드부터 공부하기

프로젝트 루트에서 순서대로 실행합니다.

```bash
python3 learning/01_read_log.py data/sample_system.log
```

파일 경로를 `sys.argv[1]`로 받아 한 줄씩 출력합니다.

```bash
python3 learning/02_filter_warn.py data/sample_system.log
```

`if`와 `continue`로 WARN이 없는 줄을 건너뜁니다. 제공 데이터에서는 14줄입니다.

```bash
python3 learning/03_count_levels.py data/sample_system.log
```

정규식 캡처 그룹으로 로그 수준을 꺼내 딕셔너리로 횟수를 셉니다. 예상값은 INFO 14, WARN 14, ERROR 12입니다.

```bash
python3 learning/04_run_as_subprocess.py
```

부모 Python 프로그램이 완성 도구를 하위 프로세스로 실행합니다. `capture_output=True`, `text=True`, `result.returncode`, `result.stdout`, `result.stderr`를 확인할 수 있습니다.

각 파일의 설명과 직접 바꿔 볼 과제는 [한국어 학습 안내](docs/learning_guide_ko.md)에 있습니다.

## 6. 검증 실행하기

```bash
python3 -m unittest discover -s tests -v
```

초기 버전에는 22개 검증이 있습니다. 모두 통과하면 마지막에 `OK`가 나옵니다. 검증 내용은 [검증 기록](docs/validation.md)에 정리했습니다.

## 7. GitHub에 올리기

[GitHub 업로드 안내](docs/github_upload_ko.md)를 따르세요. ZIP 파일 하나를 그대로 저장소에 올리는 대신 **압축을 푼 프로젝트 안의 파일들**을 업로드합니다.

채용 담당자가 볼 `README.md`는 영어로 작성했습니다. 학습 출처와 초기 구현의 AI 도움을 명시했습니다. 직접 바꿔 본 기능과 확인한 결과는 [학습 기록](docs/learning_journal.md)에 적어 두면 본인이 한 작업을 설명하기 좋습니다.
