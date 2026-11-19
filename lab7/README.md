# Lab 7 - Fuzzing for Input Validation Bugs

Student: Atharva D Kulkarni | PES2UG24CS093

The handout calls the files `processor.py` and `test_processor.py`. This assigned
repository uses `thermostat_control.py` and `test_thermostat_control.py` instead.

## Deliverables

- `PES2UG24CS093_Lab7_Report.pdf`: report with seven real terminal screenshots.
- `thermostat_control.py`: fixed application.
- `test_thermostat_control.py`: completed Hypothesis and regression tests.
- `evidence/`: original application, identical tests, full execution logs and screenshots.

## Run on Windows PowerShell

From the repository root:

```powershell
cd lab7
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe thermostat_control.py
.\.venv\Scripts\python.exe -m pytest test_thermostat_control.py -q
```

Directly using the virtual environment's Python avoids activation-policy issues.
On Linux/macOS, use `python3`, then `.venv/bin/python` instead.

Valid demo inputs, in order: `21.5C`, `20.5,21,22.5`, `07:05`.
Invalid demo inputs, in order: an empty line, `1,,3`, `24:00`.

## Validation contract

All functions return `None` for invalid input. The CLI displays an error and
continues to the next function. Valid data must produce a meaningful result;
returning `None` for everything would fail the tests.

| Function | Accepted input | Result |
| --- | --- | --- |
| `parse_setpoint` | Finite number followed by C/F, case insensitive; surrounding whitespace allowed | Celsius rounded to 1 decimal |
| `average_temperature` | Nonempty CSV of finite numbers; whitespace around values allowed | Arithmetic mean |
| `schedule_slot` | Strict HH:MM, hour 00-23, minute 00-59; surrounding whitespace allowed | `night MM` before 06:00, otherwise `day MM` |

Signed numbers, decimal fractions and scientific notation are supported.
NaN, infinity, unknown units, empty CSV fields and wrong Python types are rejected.
No physical temperature limits were specified, so finite temperatures are accepted.
Minutes are consistently zero padded (e.g. `day 05`).

## Test results

The exact same 57 collected tests ran against both versions:

| Version | Passed | Failed | Exit code |
| --- | ---: | ---: | ---: |
| Original | 13 | 44 | 1 |
| Fixed | 57 | 0 | 0 |

Six property tests each use a budget of 300 generated examples, with deterministic
generation for repeatability. The remaining 51 collected cases are regressions and
boundary checks. The number of collected tests is different from the number of
generated examples. A finite strategy can exhaust before reaching its budget.

The no-crash tests do not catch and ignore exceptions. They check return types,
finite numeric results and output shape. Generated valid-data tests verify
conversion, means and the day/night boundary against independent expectations.

Environment: Python 3.12.14, pytest 9.2.0, Hypothesis 6.170.15. Execution logs were
captured with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` to exclude unrelated host plugins;
this is not required in a clean virtual environment. Screenshots show terminal
views of actual saved run output. CLI input was supplied automatically, and the
input sequence is recorded at the top of each application log.

## Reproduce original failures

Use the same Python executable where dependencies were installed. From `lab7`:

```powershell
Push-Location evidence\original
..\..\.venv\Scripts\python.exe thermostat_control.py
..\..\.venv\Scripts\python.exe -m pytest test_thermostat_control.py -q --tb=short
Pop-Location
```

The original application and original-version tests are intentionally failing.
`pytest.ini` excludes the archived `evidence` directory from recursive collection.
The explicit commands above run the intended suite for each version.

## Main fixes and viva notes

- Fuzzing generates unexpected inputs; Hypothesis shrinks failures to small examples.
- Empty strings and `None` exposed unsafe slicing, conversion and `.split()` calls.
- Explicit type, format, range and finite-number checks prevent these failures.
- `21K` was silently accepted as Celsius; units are now checked.
- `24:00` and `23:60` were accepted; time bounds are now checked.
- Daytime minutes previously lost leading zeros; both slots now use two digits.
- Large finite readings could overflow an intermediate sum; `statistics.mean`
  avoids this. Fahrenheit conversion divides before multiplying for the same reason.
- Passing this suite demonstrates the tested properties, not absence of every bug.
