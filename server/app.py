import sys
import os
from typing import Union

# 1. PATH INJECTION: Force the project root into sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Ensure the root directory is at the front of the path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. CORE OPENENV IMPORT
try:
    from openenv.core.env_server.http_server import create_app
except ImportError:
    raise ImportError("openenv library not found in container.")

# 3. ABSOLUTE IMPORTS
import models

# Targeted import for inference.py from the root
try:
    from inference import ApiWorkflowEnvironment
except ImportError:
    import importlib.util
    # Constructing absolute path to inference.py at repo root
    file_path = os.path.join(project_root, "inference.py")
    spec = importlib.util.spec_from_file_location("inference", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not find inference.py at {file_path}")
    env_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(env_module)
    ApiWorkflowEnvironment = env_module.ApiWorkflowEnvironment

# 4. CREATE APP
app = create_app(
    ApiWorkflowEnvironment,
    Union[models.AddCalendarEvent, models.ScheduleMeeting, models.SearchContact],
    Union[models.CalendarObservation, models.ContactObservation],
    env_name="api_workflow_env",
    max_concurrent_envs=1,
)

# 5. RUN SERVER (Port 7860 is mandatory for Hugging Face)
def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    # Defaulting to 7860 for Hugging Face compatibility
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    main(port=args.port)


