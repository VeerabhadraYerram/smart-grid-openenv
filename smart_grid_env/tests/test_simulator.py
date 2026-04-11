import pytest
from smart_grid_env.server.simulator import BatteryStorage, GridSimulator, get_tou_rate

def test_battery_storage():
    battery = BatteryStorage()
    assert battery.soc_pct == 50.0
    
    # Test charging
    actual_charge = battery.charge(10.0, dt_hours=1.0)
    assert actual_charge == 10.0
    assert battery.soc_pct > 50.0
    
    # Test bounds on charge
    battery.reset(0.95)
    actual_charge = battery.charge(25.0)
    assert actual_charge == 0.0 # already full
    
    # Test discharging efficiency
    battery.reset(0.50)
    actual_discharge = battery.discharge(10.0)
    assert actual_discharge == 10.0
    assert battery.soc_pct < 50.0

def test_grid_simulator_cascading_trips():
    sim = GridSimulator(seed=42)
    # Frequency drops below blackout threshold
    new_trips = sim.process_cascading_failures(48.0)
    assert len(new_trips) == len(sim.loads)
    assert len(sim.tripped_loads) == len(sim.loads)
    
def test_grid_simulator_grace_period():
    sim = GridSimulator(seed=42)
    new_trips = sim.process_cascading_failures(49.3) # Warning
    assert len(new_trips) == 0
    
    new_trips = sim.process_cascading_failures(49.1) # Critical
    assert len(new_trips) == 0 # Grace period (requires 2 steps)
    
    new_trips = sim.process_cascading_failures(49.1)
    assert len(new_trips) == 1 # Second step trips 1 load
    
def test_tou_rates():
    assert get_tou_rate(18) == 16.0 # Super peak
    assert get_tou_rate(12) == 8.0 # Normal
    
def test_sim_curtailment():
    sim = GridSimulator()
    res = sim.apply_curtailments({"steel_plant": 10.0}, hour=12)
    assert res["total_curtailed_mw"] == 10.0
    assert "steel_plant" in res["per_load"]
