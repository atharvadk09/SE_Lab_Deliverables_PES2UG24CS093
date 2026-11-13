import pytest
from thermostat_control import target_temperature, hvac_action, energy_alert

#Example test cases:
def test_away_mode():
    assert target_temperature("away", True, 12) == 16

def test_no_readings():
    assert energy_alert([], 10) == "ok"

#Write the rest of the test cases so that the code is 90- 100% covered.

# Test cases for target_temperature()

def test_sleep_night():
    assert target_temperature("sleep", True, 23) == 18

def test_sleep_day():
    assert target_temperature("sleep", True, 12) == 20

def test_unoccupied():
    assert target_temperature("home", False, 12) == 18

def test_morning_temperature():
    assert target_temperature("home", True, 7) == 22

def test_evening_temperature():
    assert target_temperature("home", True, 18) == 21

def test_normal_temperature():
    assert target_temperature("home", True, 12) == 20


# Test cases for hvac_action()

def test_hvac_idle():
    assert hvac_action(20, 20, 15) == "idle"

def test_hvac_heat_boost():
    assert hvac_action(15, 20, 2) == "heat_boost"

def test_hvac_heat():
    assert hvac_action(15, 20, 15) == "heat"

def test_hvac_cool_boost():
    assert hvac_action(25, 20, 35) == "cool_boost"

def test_hvac_cool():
    assert hvac_action(25, 20, 20) == "cool"


# Test cases for energy_alert()

def test_energy_warning():
    assert energy_alert([12, 5, 6], 10) == "warning"

def test_energy_critical():
    assert energy_alert([12, 15, 5], 10) == "critical"
