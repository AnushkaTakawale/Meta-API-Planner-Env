import sys
import os
from typing import Union

# 1. PATH INJECTION: Force the project root into sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add both the root and the server folder to path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. CORE OPENENV IMPORT
try:
    from openenv.core.env_server.http_server import create_app
except ImportError:
    raise ImportError("openenv library not found in container.")

# 3. ABSOLUTE IMPORTS
import models

# Explicitly importing the inference file (renamed from api_workflow_env_environment)
try:
    from inference import ApiWorkflowEnvironment
except ImportError:
    # If the standard import fails, we use the manual path-based import
    import importlib.util
    file_path = os.path.join(project_root, "inference.py")
    spec = importlib.util.spec_from_file_location("inference", file_path)
    env_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(env_module)
    # This assumes your Class inside inference.py is named ApiWorkflowEnvironment
    ApiWorkflowEnvironment = env_module.ApiWorkflowEnvironment

# 4. CREATE APP
app = create_app(
    ApiWorkflowEnvironment,
    Union[models.AddCalendarEvent, models.ScheduleMeeting, models.SearchContact],
    Union[models.CalendarObservation, models.ContactObservation],
    env_name="api_workflow_env",
    max_concurrent_envs=1,
)

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)
