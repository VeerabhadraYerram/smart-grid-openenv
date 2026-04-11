from server.grid_env import SmartGridEnv
import test_variance
env = SmartGridEnv()
test_variance.run_policy("peak_survival", "super_smart_heuristic")
