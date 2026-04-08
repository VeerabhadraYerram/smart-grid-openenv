---
title: Smart Grid Demand Response
emoji: ⚡
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# ⚡ Smart Grid Demand Response (OpenEnv)

> **The first demand response reinforcement learning environment natively designed for LLM Agents.**

Instead of outputting simple 1D float arrays to the agent, this environment serves a **natural language situation report**, requiring advanced Agentic reasoning to manage cascading grid failures, time-of-use pricing, localized weather systems, and Battery Energy Storage (BESS).

---

## 🏆 Judge's Grading Guide
Welcome to the Smart Grid Control Room! If you are reviewing this space for Phase 3 (Human Review), here is the fastest way to test our core physics and ethical constraints:

*   **1. Trigger a Cascading Blackout (The Math works!)**
    Play the **`extreme_event`** task. Do absolutely nothing (leave curtailments blank) and click **Step**. Within 2 steps, the grid frequency will plummet below 49.0Hz, automatically triggering catastrophic cascading logic that permanently trips industrial loads to save the city. Unintelligent agents mathematically receive a `0.00` score here!
*   **2. Read the LLM-Native Situation Report**
    Play the **`monsoon_crisis`** task. Look at the `observation.situation_report`. Notice how the text dynamically reflects the chaotic weather and the severe drop in solar power. We built this environment specifically so LLMs could 'read' the grid.
*   **3. Violate the Ethical Constraints**
    Try explicitly typing `12` into the Hospital curtailment box. When the episode resolves, look at your grade. Our strict ethical grader heavily penalizes any agent that sacrifices critical infrastructure (Hospitals/Metro) over commercial targets, dramatically lowering the score.

---

## 🧠 Core Features

- **Cascading Failure Risk**: Frequency thresholds strictly enforce action. Drops below 49.2Hz trigger automated grid load-shedding cascades.
- **Battery Energy Storage**: A 50MWh BESS allowing LLM agents to plan ahead (charge during off-peak, discharge during peak).
- **Dynamic Demand Profiles**: 10 Unique commercial, industrial, and residential profiles scaling dynamically with underlying heatwave/climate variables.
- **Strict Compliance**: 100% compliant with OpenEnv automated tools. Phase 2 Inference script utilizes strict prompt separation to easily guide open-source LLMs to high baseline scores, proving solvability.

## 📊 Environment Tasks

| Task Name | Difficulty | Length | Focus |
|:---|:---:|:---:|:---|
| `peak_survival` | Easy | 12 steps | Survive a 3-hour evening peak (minimal battery needed). |
| `daily_balance` | Medium | 24 steps | 24h balance: maximize stability, minimize discomfort/cost. |
| `extreme_event` | Hard | 48 steps | 48h heatwave: fairness constraints + protect critical infrastructure. |
| `monsoon_crisis` | Med-Hard | 24 steps | Solar near zero, erratic wind. Aggressive battery management required. |
| `renewable_transition` | Expert | 72 steps | 3-day multi-cycle episode. Thermal supply reduced by 30%. |
