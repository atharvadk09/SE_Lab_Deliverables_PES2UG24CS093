"""The same tests are run against the original and fixed applications."""

import math
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st
from thermostat_control import parse_setpoint, average_temperature, schedule_slot


settings.register_profile("lab7", max_examples=300, deadline=None, derandomize=True)
settings.load_profile("lab7")

INPUTS = st.one_of(
    st.text(), st.none(), st.integers(), st.floats(), st.booleans(),
    st.binary(), st.lists(st.integers(), max_size=5),
    st.dictionaries(st.text(max_size=5), st.integers(), max_size=3),
)


@given(INPUTS)
def test_parse_setpoint_no_crash(s):
    result = parse_setpoint(s)
    assert result is None or (isinstance(result, float) and math.isfinite(result))


@given(INPUTS)
def test_average_temperature_no_crash(s):
    result = average_temperature(s)
    assert result is None or (isinstance(result, float) and math.isfinite(result))


@given(INPUTS)
def test_schedule_slot_no_crash(s):
    result = schedule_slot(s)
    if result is not None:
        slot, minute = result.split()
        assert slot in ("day", "night")
        assert len(minute) == 2 and 0 <= int(minute) <= 59


@given(st.integers(-10000, 10000), st.sampled_from(["C", "c", "F", "f"]))
def test_setpoint_conversion(value, unit):
    expected = float(value) if unit.upper() == "C" else (value - 32) * 5 / 9
    assert parse_setpoint(f" {value}{unit} ") == pytest.approx(round(expected, 1))


@given(st.lists(st.integers(-1000000, 1000000), min_size=1, max_size=50))
def test_csv_mean(values):
    csv = ",".join(f" {value} " for value in values)
    result = average_temperature(csv)
    expected = float(sum(Decimal(v) for v in values) / Decimal(len(values)))
    assert result == pytest.approx(expected)
    assert min(values) <= result <= max(values)


@given(st.integers(0, 23), st.integers(0, 59))
def test_valid_time(hour, minute):
    expected = f"{'night' if hour < 6 else 'day'} {minute:02d}"
    assert schedule_slot(f"{hour:02d}:{minute:02d}") == expected


@pytest.mark.parametrize("text", ["", " ", "21", "21K", "C", "nanC", "infF",
                                       "1e999C", "21CC", "1_0C", "20C\nextra"])
def test_invalid_setpoint(text):
    assert parse_setpoint(text) is None


@pytest.mark.parametrize("text", ["", " ", ",", "1,,3", "1,", ",1", "one,two",
                                       "nan", "1,inf", "1e999", "1_0,20"])
def test_invalid_csv(text):
    assert average_temperature(text) is None


@pytest.mark.parametrize("text", ["", " ", "6:05", "06:5", "24:00", "23:60",
                                       "-1:00", "00:-1", "06:00:00", "aa:bb"])
def test_invalid_time(text):
    assert schedule_slot(text) is None


@pytest.mark.parametrize("text, expected", [("21.5C", 21.5), ("70F", 21.1),
    ("32F", 0.0), ("-40F", -40.0), (" 21.5 c ", 21.5), ("1e2C", 100.0)])
def test_known_setpoints(text, expected):
    assert parse_setpoint(text) == expected


@pytest.mark.parametrize("text, expected", [("00:00", "night 00"),
    ("05:59", "night 59"), ("06:00", "day 00"), ("07:05", "day 05"),
    ("23:59", "day 59"), (" 06:05 ", "day 05")])
def test_schedule_boundaries(text, expected):
    assert schedule_slot(text) == expected


@pytest.mark.parametrize("text, expected", [("20.5,21,22.5", 64 / 3),
    ("5", 5.0), ("-10,10", 0.0), ("1e308,1e308", 1e308),
    ("1e308,1e308,-1e308,-1e308", 0.0)])
def test_mean_regressions(text, expected):
    assert average_temperature(text) == pytest.approx(expected)


@pytest.mark.parametrize("unit", ["C", "F"])
def test_large_finite_setpoint(unit):
    result = parse_setpoint("1.7976931348623157e308" + unit)
    assert isinstance(result, float) and math.isfinite(result)
