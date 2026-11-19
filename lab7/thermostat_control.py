"""Thermostat input helpers. Invalid input returns None instead of crashing."""

import math
import re
from statistics import mean


NUMBER = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
SETPOINT = re.compile(r"(" + NUMBER + r")\s*([cCfF])")
TIME = re.compile(r"([0-9]{2}):([0-9]{2})")


def _finite_number(text):
    if re.fullmatch(NUMBER, text) is None:
        return None
    value = float(text)
    return value if math.isfinite(value) else None


def parse_setpoint(text):
    """Convert a finite C/F setpoint to Celsius, rounded to one decimal."""
    if not isinstance(text, str):
        return None
    match = SETPOINT.fullmatch(text.strip())
    if match is None:
        return None
    value = _finite_number(match.group(1))
    if value is None:
        return None
    if match.group(2).upper() == "F":
        # Divide first so even very large finite readings do not overflow.
        value = (value / 9) * 5 - (32 / 9) * 5
    return round(value, 1)


def average_temperature(readings_csv):
    """Return the mean of nonempty finite CSV readings; reject malformed CSV."""
    if not isinstance(readings_csv, str) or not readings_csv.strip():
        return None
    values = []
    for token in readings_csv.split(","):
        value = _finite_number(token.strip())
        if value is None:
            return None
        values.append(value)
    # mean avoids overflow in the intermediate sum of large finite floats.
    return mean(values)


def schedule_slot(time_text):
    """Accept HH:MM in 24-hour time; 00:00-05:59 is the night slot."""
    if not isinstance(time_text, str):
        return None
    match = TIME.fullmatch(time_text.strip())
    if match is None:
        return None
    hour, minute = map(int, match.groups())
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    slot = "night" if hour < 6 else "day"
    return f"{slot} {minute:02d}"


def main():
    steps = [
        ("parse_setpoint", "Enter a setpoint (e.g. 21.5C or 70F): ",
         parse_setpoint, "Setpoint in Celsius:"),
        ("average_temperature", "Enter sensor readings as CSV (e.g. 20.5,21,22.5): ",
         average_temperature, "Average Temperature:"),
        ("schedule_slot", "Enter a time as HH:MM (e.g. 07:30): ",
         schedule_slot, "Schedule Slot:"),
    ]
    for name, prompt, function, label in steps:
        print(f"==== Running {name} ====")
        try:
            text = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return
        result = function(text)
        if result is None:
            print("Invalid input. Please check the format and range.")
        else:
            print(label, result)
        print()


if __name__ == "__main__":
    main()
