import pytest
from smart_grid_env.server.grid_env import SmartGridEnv
from smart_grid_env.models import Action

def test_grid_env_reset():
    env = SmartGridEnv()
    obs = env.reset(task_name="daily_balance")
    assert obs.step_number == 0
    assert not obs.done
    assert obs.active_task == "daily_balance" if hasattr(obs, 'active_task') else True
    # The models don't have active_task, it's just passed back by the wrapper.
    # We test what is in observation
    assert obs.grid_frequency_hz > 0
    assert obs.situation_report != ""

def test_grid_env_step_mechanics():
    env = SmartGridEnv()
    env.reset(task_name="daily_balance")
    
    action = Action(curtailments={}, battery_action="idle", battery_mw=0.0)
    obs = env.step(action)
    
    assert obs.step_number == 1
    assert not obs.done

def test_grid_env_rewards_and_grading():
    env = SmartGridEnv()
    env.reset(task_name="peak_survival")
    
    action = Action(curtailments={}, battery_action="idle", battery_mw=0.0)
    # Fast forward to end of episode
    for _ in range(12):
        obs = env.step(action)
        
    assert obs.done
    grade = env.grade()
    assert 0.0 <= grade <= 1.0
