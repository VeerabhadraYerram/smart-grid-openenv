import sys
import json
import inference

class MockMessage:
    def __init__(self):
        self.content = '{"curtailments": {"steel_plant": 5, "textile_mill": 2}, "battery_action": "idle", "battery_mw": 0}'

class MockChoice:
    def __init__(self):
        self.message = MockMessage()

class MockCompletions:
    def create(self, **kwargs):
        class MockResponse:
            choices = [MockChoice()]
        return MockResponse()

class MockChat:
    completions = MockCompletions()

class MockClient:
    chat = MockChat()

# Monkey-patch the OpenAI client inside inference.py
inference.client = MockClient()
inference.MODEL = "dummy-local-model"

if __name__ == "__main__":
    for task in [
        "peak_survival",
        "daily_balance",
        "extreme_event",
        "monsoon_crisis",
        "renewable_transition"
    ]:
        print(f"\n--- Running Task: {task} ---")
        try:
            inference.run_episode(task)
        except Exception as e:
            print(f"[END] success=false steps=0 score=0.001 rewards=0.00", flush=True)
