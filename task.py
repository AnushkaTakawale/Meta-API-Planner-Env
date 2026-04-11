# task.py
from inference import ApiWorkflowEnvironment

TASK_DESCRIPTION = "Schedule a meeting with Rahul for tomorrow at 10 AM. You must find his email first."

def get_agent():
    return ApiWorkflowEnvironment()
