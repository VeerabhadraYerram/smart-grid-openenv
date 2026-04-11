import pytest
from pydantic import ValidationError
from smart_grid_env.models import Action, Observation

def test_action_validation():
    # Valid action
    action = Action(curtailments={}, battery_action="idle", battery_mw=0.0)
    assert action.battery_action == "idle"

    # Action with battery constraint error (battery_mw bounds inside pydantic)
    with pytest.raises(ValidationError):
        Action(curtailments={}, battery_action="charge", battery_mw=30.0) # > 25.0

    with pytest.raises(ValidationError):
        Action(curtailments={}, battery_action="charge", battery_mw=-5.0) # < 0.0

def test_observation_defaults():
    obs = Observation(
        step_number=5,
        hour=12,
        day=1,
        situation_report="Grid is ok",
        grid_frequency_hz=50.0,
        temperature_c=35.0,
        weather="clear",
        loads=[],
        battery_soc_pct=50.0,
        battery_capacity_mwh=50.0,
        total_supply_mw=1.0,
        solar_output_mw=10.0,
        total_demand_mw=15.0,
        supply_deficit_mw=0.0,
        done=False
    )
    assert obs.step_number == 5
    assert not obs.done
