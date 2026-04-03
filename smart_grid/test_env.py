"""
Quick smoke test for the Smart Grid environment.

Run:  python -m smart_grid.test_env
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smart_grid.models import SmartGridAction, SmartGridObservation
from smart_grid.server.smart_grid_environment import SmartGridEnvironment


def main():
    env = SmartGridEnvironment()

    # Reset
    obs = env.reset(seed=42)
    assert isinstance(obs, SmartGridObservation)
    assert obs.done is False
    assert obs.step_number == 0
    print(f"[RESET] hour={obs.hour_of_day}, day={obs.day_of_year}, "
          f"solar={obs.solar_available:.2f} MW, wind={obs.wind_available:.2f} MW, "
          f"demand={obs.demand:.2f} MW, SOC={obs.battery_soc:.2f}")

    # Run a few steps
    total_reward = 0.0
    for i in range(24):  # simulate 1 day
        action = SmartGridAction(
            solar_dispatch=1.0,
            wind_dispatch=1.0,
            battery_action=0.1 if obs.battery_soc < 0.8 else -0.3,
            grid_exchange=0.2 if obs.demand > obs.solar_available + obs.wind_available else -0.1,
        )
        obs = env.step(action)
        total_reward += obs.reward
        if i % 6 == 0:
            print(
                f"  [step {obs.step_number:3d}] h={obs.hour_of_day:2d} "
                f"sol={obs.solar_dispatched:5.2f} wind={obs.wind_dispatched:5.2f} "
                f"batt={obs.battery_power:+5.2f} grid={obs.grid_power:+5.2f} "
                f"demand={obs.demand:5.2f} unmet={obs.unmet_demand:5.2f} "
                f"cost=${obs.energy_cost:+.3f} SOC={obs.battery_soc:.2f} "
                f"R={obs.reward:+.3f}"
            )

    print(f"\n  24-step totals: cost=${obs.total_cost:.2f}, "
          f"carbon={obs.total_carbon:.4f} kg, "
          f"unmet={obs.total_unmet:.4f} MWh, "
          f"reward={total_reward:.2f}")
    print(f"  Episode done? {obs.done}")
    print("\n[OK] All checks passed!")


if __name__ == "__main__":
    main()
