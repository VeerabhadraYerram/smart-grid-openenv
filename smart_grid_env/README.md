# Smart Grid Demand Response (OpenEnv)

> **First demand response reinforcement learning environment designed specifically for LLM agents.**

Instead of flat numerical arrays (e.g. `[50.2, 280.3, ...]`), this environment provides agents with **natural language situation reports** alongside deep grid mechanics: cascading failures, time-of-use pricing, Indian climatic conditions, and battery energy storage (BESS) management.

## 🚀 Quick Start

### Local Development
```bash
# Clone and install dependencies
pip install openenv-core[core]
pip install -e .

# Run the environment and interactive web UI
openenv serve . --port 7860
```
Open [http://localhost:7860](http://localhost:7860) to view the Smart Grid Control Room.

### Run tests
```bash
python test_env.py
```

### Docker
```bash
docker build -t smart-grid-openenv .
docker run -p 7860:7860 smart-grid-openenv
```

## 🧠 Core Mechanics

- **Observation**: Read a rich Markdown `situation_report` explaining grid frequency, cascading warnings, and weather effects.
- **Action**: Provide a JSON containing `{ "load_id": mb_to_curtail }` and battery management instructions.
- **Physics Engine**: Realistic frequency decay based on supply/demand imbalance. Dropping below 49.2Hz starts an automated cascade.
- **BESS**: A utility-scale 50MWh battery that the agent can charge during off-peak hours and discharge during emergencies.
- **Dynamic Demand**: Bottom-up load synthesis using industrial/residential profiles responsive to heatwaves/monsoons.

## 📊 Environment Tasks

| Task Name | Difficulty | Length | Focus |
|:---|:---:|:---:|:---|
| `peak_survival` | Easy | 12 steps | Survive a 3-hour evening peak (minimal battery needed). |
| `daily_balance` | Medium | 24 steps | 24h balance: maximize stability, minimize discomfort/cost. |
| `extreme_event` | Hard | 48 steps | 48h heatwave: fairness constraints + protect critical infrastructure. |
| `monsoon_crisis` | Med-Hard | 24 steps | Solar near zero, erratic wind. Aggressive battery management required. |
| `renewable_transition` | Expert | 72 steps | 3-day multi-cycle episode. Thermal supply reduced by 30%. |

## 📐 Hackathon Notes

- Runs fully compliant with OpenEnv APIs (`reset`, `step`, and `grade()`).
- Graders return varied strings between `0.0` (miserable failure) and `1.0` (perfect performance).
- Passes all strict `openenv validate` checks and deploys smoothly via Docker to Hugging Face spaces.
