import pytest
from smart_grid_env.server.weather import WeatherEngine, WEATHER_EFFECTS

def test_weather_engine_init():
    engine = WeatherEngine(seed=42)
    assert engine.current == "clear"

    engine.reset(initial="heatwave")
    assert engine.current == "heatwave"

def test_weather_effects():
    engine = WeatherEngine(seed=42)
    engine.reset(initial="storm")
    effects = engine.effects()
    
    assert effects["solar_mult"] == pytest.approx(0.1)
    assert effects["wind_mult"] == pytest.approx(0.3)
    
def test_weather_advancement():
    engine = WeatherEngine(seed=42)
    # Give it a known seed and advance
    engine.current = "monsoon"
    weather_seen = set()
    for _ in range(100):
        engine.advance()
        weather_seen.add(engine.current)
    
    # After 100 hours it should have transitioned at least once
    assert len(weather_seen) > 1
