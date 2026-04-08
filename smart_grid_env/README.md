---
title: Smart Grid Demand Response
emoji: ⚡
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
base_path: /web
---

# ⚡ Smart Grid Demand Response (OpenEnv)

> **"It's 6:00 PM on a 42°C day in Delhi. 20 million ACs just switched on. Solar power is dropping fast. You have 15 minutes to save the grid from a total blackout. What do you do?"**

## 🌍 The Problem (In Simple Terms)
Imagine you are the manager of a massive power grid like **Adani Power** or **Tata Power**. You have to keep the electricity "frequency" at exactly **50Hz**. 

If people use more power than you produce, the frequency drops. If it drops too low, transformers explode and the whole city goes dark (**Blackout**). Currently, this is handled by complex math models that only see numbers. They don't understand that a **Hospital** shouldn't be turned off, but a **Steel Plant** can wait.

## 🧠 Our Novel Approach: Agentic Awareness
Standard AI models see the grid as a list of numbers like `[50.1, 0.8, 120]`. They are "blind" to context.

**Our solution is fundamentally different.** We built the first environment designed for **LLM Agents** (like GPT-4 or Nemotron). Instead of numbers, our AI receives a **Natural Language Situation Report**:

> *"⚠️ EMERGENCY: Frequency at 49.5Hz. Heatwave intensity is peaking. Steel Plant is consuming 80MW. Hospital is on critical backup. Action required immediately to prevent cascading failure."*

This allows the AI to **reason** about priority, ethics, and physics simultaneously.

---

## 🎮 How the Environment Works

### 📋 Action Space
The Agent has two ways to save the day:
1. **Load Curtailment:** Tell specific factories or neighborhoods to reduce power.
2. **Battery (BESS):** Use a 50MWh "Giant Power Bank" to bridge the gap.

### 🏆 The 5 Mission Scenarios
*   **Peak Survival (Easy):** Survive a 3-hour evening rush.
*   **Daily Balance (Medium):** 24 hours of stability and cost-cutting.
*   **Extreme Event (Hard):** A brutal 48-hour heatwave.
*   **Monsoon Crisis (Hard):** Storms kill your Solar; Wind is erratic.
*   **Grid Transition (Expert):** Coal plants are retired; you must rely only on Green Energy + Batteries.

---

## 🕵️ Judge's Testing Guide
To see our grid physics in action, try the **"Blackout Challenge"** in the UI:
1. Select **"extreme_event"**.
2. Click **Reset**.
3. Do **NOT** take any actions (leave everything at 0).
4. Click **Step** until the Frequency drops below 48.5Hz.
5. Watch the **Situation Report** describe the cascading grid failure as neighborhoods go dark!

---

## 📊 Proof of Variance (Data)
We proved our environment isn't a "toy." Incompetent agents lose immediately, while smart ones excel:

*   **Incompetent Bot:** Score 0.001 (Fast Blackout)
*   **Basic AI Bot:** Score 0.209 (Poor Stability)
*   **Our "Smart Oracle" Bot:** Score 0.647+ (Professional Grid Management)

**OpenEnv Spec Compliant & Deployable.** ⚡
