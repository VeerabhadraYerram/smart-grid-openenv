"""
Baseline LLM Agent Inference (Phase 2)
========================================
A simple baseline that uses an LLM to control the grid.
Uses the 'situation_report' from observations for zero-shot reasoning.

Phase 2 update:
- Fixed: step() now returns Observation directly (not a StepResult)
- Added: battery_action prompting and response parsing
- Added: all 5 tasks to the evaluation loop
"""

import os
import json
from openai import OpenAI
from server.grid_env import SmartGridEnv
from models import Action


# Configure the client (pointing to HF Spaces or a local API if needed)
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("HF_TOKEN", "dummy_key")
)
MODEL = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")


def run_episode(task_name: str) -> float:
    """Run one full episode with the LLM agent and return the final grade."""
    env = SmartGridEnv()
    obs = env.reset(task_name=task_name)   # obs is an Observation directly
    total_reward = 0.0
    step_count = 0

    print(f"\n--- Starting Episode: {task_name} ---")

    while True:
        # 1. Build prompt from the situation_report
        loads_summary = json.dumps(
            [
                {
                    "id": l["id"],
                    "name": l["name"],
                    "current_mw": l["current_mw"],
                    "max_reducible_mw": l["reducible_mw"],
                    "priority": l["priority"],
                    "tripped": l.get("tripped", False),
                }
                for l in obs.loads
            ],
            indent=2,
        )

        prompt = f"""You are an AI Smart Grid Dispatcher for an Indian city power grid.
Your goal: maintain grid frequency at 50Hz, protect critical infrastructure (hospital, metro),
and minimize customer discomfort and curtailment cost.

=== SITUATION REPORT ===
{obs.situation_report}

=== CONTROLLABLE LOADS ===
{loads_summary}

=== BATTERY ===
State of Charge: {obs.battery_soc_pct:.1f}% ({obs.battery_hours_remaining:.1f}h at max rate)
Max rate: 25MW. Use 'charge' to store surplus energy, 'discharge' to release stored energy.

=== CASCADING RISK ===
Tripped loads (offline): {obs.tripped_loads}
Consecutive low-freq steps (cascade at 2): {obs.low_freq_consecutive_steps}

INSTRUCTIONS:
- Analyze the supply-demand balance and frequency.
- Curtail LOW and MEDIUM priority loads first. NEVER curtail 'critical' loads.
- Use the battery strategically: discharge if there's a deficit, charge if there's surplus.
- If frequency < 49.2Hz for 2 consecutive steps, loads will auto-disconnect!

Respond ONLY with valid JSON:
{{"curtailments": {{"load_id": mw_to_reduce}}, "battery_action": "idle", "battery_mw": 0.0}}

battery_action must be one of: "charge", "discharge", "idle"
battery_mw must be between 0 and 25.
"""

        # 2. Get LLM response
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            action_dict = json.loads(content)

            # Normalize response structure
            if "curtailments" not in action_dict:
                action_dict = {"curtailments": action_dict}
            # Ensure battery fields exist
            action_dict.setdefault("battery_action", "idle")
            action_dict.setdefault("battery_mw", 0.0)

            action = Action(**action_dict)
        except Exception as e:
            print(f"  ⚠️  Parse error: {e}. Using no-op action.")
            action = Action(curtailments={}, battery_action="idle", battery_mw=0.0)

        # 3. Step the environment — returns Observation directly
        obs = env.step(action)
        total_reward += obs.reward
        step_count += 1

        print(
            f"  Step {step_count:3d} | Freq: {obs.grid_frequency_hz:.2f}Hz | "
            f"Alert: {obs.alert_level:8s} | SOC: {obs.battery_soc_pct:.0f}% | "
            f"Reward: {obs.reward:.3f} | Tripped: {obs.tripped_loads}"
        )

        if obs.done:
            break

    # 4. Final grade
    final_score = env.grade()
    print(f"  Grade: {final_score:.4f} | Total Reward: {total_reward:.3f}")
    return final_score


if __name__ == "__main__":
    tasks = [
        "peak_survival",
        "daily_balance",
        "extreme_event",
        "monsoon_crisis",
        "renewable_transition",
    ]
    scores = {}
    for task in tasks:
        try:
            scores[task] = run_episode(task)
        except Exception as e:
            print(f"Error running task {task}: {e}")
            scores[task] = 0.0

    print("\n--- SUMMARY OF BASELINE SCORES ---")
    for task, score in scores.items():
        print(f"{task.upper():<25} | Score: {score:.4f}")
