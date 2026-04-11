import json
import random
from typing import Dict, Any

from server.grid_env import SmartGridEnv
from models import Action

TASKS = ["peak_survival", "daily_balance", "extreme_event", "monsoon_crisis", "renewable_transition"]

def run_policy(task_name: str, policy_type: str) -> float:
    env = SmartGridEnv()
    obs = env.reset(task_name=task_name)
    step_count = 0
    
    while True:
        if policy_type == "do_nothing":
            action = Action(curtailments={}, battery_action="idle", battery_mw=0.0)
            
        elif policy_type == "random":
            curtailments = {}
            for l in obs.loads:
                if random.random() > 0.5:
                    curtailments[l["id"]] = random.uniform(0, l["reducible_mw"])
            batt_actions = ["idle", "charge", "discharge"]
            batt_choice = random.choice(batt_actions)
            action = Action(
                curtailments=curtailments,
                battery_action=batt_choice,
                battery_mw=random.uniform(0, 25.0) if batt_choice != "idle" else 0.0
            )
            
        elif policy_type == "smart_heuristic":
            # Hardcoded logic to act like a decent AI
            curtailments = {}
            freq = obs.grid_frequency_hz
            
            # If frequency is dipping, curtail low-priority loads heavily
            if freq < 49.8:
                for l in obs.loads:
                    if l["priority"] in ["low", "medium"]:
                        curtailments[l["id"]] = l["reducible_mw"]
                        
            # Battery logic
            if freq > 50.1 and obs.battery_soc_pct < 90:
                batt = "charge"
                mw = 20.0
            elif freq < 49.7 and obs.battery_soc_pct > 10:
                batt = "discharge"
                mw = 25.0
            else:
                batt = "idle"
                mw = 0.0
                
            action = Action(curtailments=curtailments, battery_action=batt, battery_mw=mw)

        elif policy_type == "super_smart_heuristic":
            demand = obs.total_demand_mw
            supply = obs.total_supply_mw
            
            mw_needed = demand - supply
            
            curtailments = {}
            batt = "idle"
            batt_mw = 0.0
            
            # Step 1: Battery logic
            if mw_needed > 20.0: # Only discharge if deficit > 20MW (freq will still be > 49.87Hz)
                batt = "discharge"
                batt_mw = min(50.0, mw_needed - 20.0)
                mw_needed -= batt_mw
            elif mw_needed < -20.0: # surplus
                batt = "charge"
                batt_mw = min(50.0, -mw_needed - 20.0)
                mw_needed += batt_mw
                
            # Smart lookahead force-charge for hard tasks
            if task_name in ["extreme_event", "renewable_transition", "monsoon_crisis"]:
                 if env.hour in [10, 11, 12, 13, 14, 15] and obs.battery_soc_pct < 90.0:
                     if batt == "discharge":
                         mw_needed += batt_mw
                         batt = "charge"
                         batt_mw = 50.0
                         mw_needed += 50.0
                     elif batt == "idle":
                         batt = "charge"
                         batt_mw = 50.0
                         mw_needed += 50.0
                     elif batt == "charge" and batt_mw < 50.0:
                         mw_needed += (50.0 - batt_mw)
                         batt_mw = 50.0
                     
            # Step 2: Smart curtailment alloc to respect 70% fairness rule
            if mw_needed > 20.01:
                valid_loads = [
                    l for l in obs.loads
                    if not l["tripped"] and l["reconnect_in"] == 0 and l["priority"] != "critical"
                ]
                
                limit = 0.70 * getattr(env.current_task, "episode_steps", 72)
                
                def load_score(l):
                    c_count = l["curtailed_this_episode"]
                    is_pen = c_count >= (limit - 1)
                    cost = l["discomfort_factor"] * {"low": 1, "medium": 2, "high": 5}.get(l["priority"], 1)
                    return (is_pen, cost)
                
                valid_loads.sort(key=load_score)
                
                for l in valid_loads:
                    c_count = l["curtailed_this_episode"]
                    is_penalized = c_count >= (limit - 1)
                    
                    # Acceptable deficit: 90MW (49.4Hz) if penalized to avoid cascade, else 20MW (49.87Hz)
                    acceptable_deficit = 90.0 if is_penalized else 20.0
                    
                    if mw_needed > acceptable_deficit + 0.1:
                        desired_reduction = mw_needed - acceptable_deficit
                        reduce_amount = min(l["reducible_mw"], desired_reduction)
                        if reduce_amount > 0:
                            curtailments[l["id"]] = reduce_amount
                            mw_needed -= reduce_amount

            action = Action(curtailments=curtailments, battery_action=batt, battery_mw=batt_mw)

        obs = env.step(action)
        step_count += 1
        
        if obs.done:
            break
            
    final_score = env.grade()
    return final_score

if __name__ == "__main__":
    POLICIES = ["do_nothing", "random", "smart_heuristic", "super_smart_heuristic"]
    
    print(f"{'Task':<22} | {'Do Nothing':<12} | {'Random':<12} | {'Smart':<12} | {'Super Smart Oracle'}")
    print("-" * 80)
    
    for task in TASKS:
        scores = {}
        for policy in POLICIES:
            try:
                score = run_policy(task, policy)
            except Exception as e:
                score = 0.0
            scores[policy] = score
            
        print(f"{task:<22} | {scores['do_nothing']:<12.3f} | {scores['random']:<12.3f} | {scores['smart_heuristic']:<12.3f} | {scores['super_smart_heuristic']:.3f}")
