# task.py
from inference import Agent

TASK_DESCRIPTION = "Schedule a meeting with Rahul for tomorrow at 10 AM. You must find his email first."

def get_agent():
    return Agent()

if __name__ == "__main__":
    print(f"Task: {TASK_DESCRIPTION}")
