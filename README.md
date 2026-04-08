# ⚡️ Smart Grid Demand Response (OpenEnv)

[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-blue)](https://huggingface.co/spaces/Maybe-Heisenberg-07/smart-grid-demand-response)
[![OpenEnv Compliance](https://img.shields.io/badge/OpenEnv-Compliant-brightgreen)](https://github.com/huggingface/openenv)

> **"It's 6:00 PM on a 42°C day in Delhi. 20 million ACs just switched on. Solar power is dropping fast. You have 15 minutes to save the grid from a total blackout. What do you do?"**

## 📋 The Mission
This is the first demand response reinforcement learning environment natively designed for **LLM Agents**. 

Instead of feeding the AI simple numeric vectors (which fail to capture the human cost of power outages), this environment provides a **Natural Language Situation Report**. It demands that the AI agent reason like a grid operator from **Adani Power** or **Tata Power**, balancing the physics of grid frequency against the ethical priority of critical infrastructure.

---

## 💎 Our Novel Approach: Agentic Situational Awareness

Most RL environments for energy (like CityLearn or Grid2Op) are designed for traditional models that see the world as `[50.2, 0.8, 120]`. 

**This environment breaks that mold.** By grounding the simulation in the **OpenEnv** framework, we leverage:

1.  **Situation Reports, Not Vectors:** Each observation contains a strategic briefing. The agent doesn't just see "Load 5", it sees "Residential Neighborhood - High Priority".
2.  **Cascading Failure Physics:** If the agent fails to act, frequency drops trigger a chain reaction. This rewards agents that can *forecast* the "Blackout Clock".
3.  **Ethical Grid Dispatch:** The grading logic penalizes curtailing a Hospital higher than a Factory, forcing the LLM to use its internal world model of society to make better grid decisions.

---

## 🛠️ Environment Architecture

### 5 Evaluation Tasks
| Task | Difficulty | Focus |
| :--- | :--- | :--- |
| **Peak Survival** | Easy | Survive a 3-hour evening spike. |
| **Daily Balance** | Medium | 24h stability & cost optimization. |
| **Extreme Event** | Hard | 48h Heatwave scenario (Delhi style). |
| **Monsoon Crisis** | Hard | Zero solar, high wind turbulence. |
| **Grid Transition** | Expert | Retire coal; rely 100% on green + battery. |

### Physics Engine
We built a custom simulator in `simulator.py` that models:
*   **Grid Frequency (Hz):** Real-time balancing of supply vs demand.
*   **Battery Storage (BESS):** 50MWh utility-scale storage.
*   **Dynamic Demand:** 10+ load categories with India-specific consumption curves.

---

## 🧪 Proof of Solvability (Score Variance)

We validated the environment using 4 different control levels to ensure the grader correctly rewards intelligence:

| Scenario | Do Nothing | Random | Basic AI | Smart Oracle |
| :--- | :---: | :---: | :---: | :---: |
| **Peak Survival** | 0.050 | 0.189 | 0.209 | 0.204 |
| **Extreme Event** | 0.001 | 0.001 | 0.156 | **0.180** |
| **Monsoon Crisis** | 0.146 | 0.078 | 0.421 | **0.647** |

The results show a massive skill ceiling—naive agents cause blackouts immediately (0.001), while smart agents that manage the battery and load effectively thrive.

---

## 🚀 Getting Started

1.  **Clone & Install:**
    ```bash
    git clone https://github.com/Schrodingerscat07/smart-grid-openenv.git
    cd smart_grid_env
    pip install openenv-core[core]
    pip install -e .
    ```
2.  **Launch the Control Room:**
    ```bash
    openenv serve . --port 7860
    ```

**Built for the OpenEnv Hackathon.** ⚡