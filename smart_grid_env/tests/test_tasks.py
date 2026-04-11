import pytest
from smart_grid_env.server.tasks import get_task, PeakSurvivalTask, DailyBalanceTask

def test_task_initialization():
    task = get_task("peak_survival")
    assert isinstance(task, PeakSurvivalTask)
    
    task = get_task("daily_balance")
    assert isinstance(task, DailyBalanceTask)
    
    with pytest.raises(ValueError):
        get_task("invalid_task")

def test_task_episode_duration():
    task = get_task("peak_survival")
    assert task.episode_steps == 12
    
def test_graders_bounds():
    task = get_task("peak_survival")
    # Grade with raw baseline stats
    grade = task.grade([
        {
            "grid_frequency_hz": 50.0,
            "avg_discomfort": 0.0,
            "curtailment_cost_inr": 0.0
        } for _ in range(12)
    ])
    assert 0.0 <= grade <= 1.0
    
    # Grade terrible performance
    grade_fail = task.grade([
        {
            "grid_frequency_hz": 48.0,
            "avg_discomfort": 1.0,
            "curtailment_cost_inr": 100000.0
        } for _ in range(12)
    ])
    assert 0.0 <= grade_fail <= 1.0
