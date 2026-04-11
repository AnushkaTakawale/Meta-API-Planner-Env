import sys
import os
from typing import Union

# 1. PATH INJECTION
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. CORE OPENENV IMPORT
try:
    from openenv.core.env_server.http_server import create_app
    _has_openenv = True
except ImportError:
    _has_openenv = False

# 3. IMPORTS
try:
    import models
    from api_workflow_env_environment import ApiWorkflowEnvironment
    _has_env = True
except ImportError:
    try:
        import importlib.util
        file_path = os.path.join(current_dir, "api_workflow_env_environment.py")
        spec = importlib.util.spec_from_file_location("api_workflow_env_environment", file_path)
        env_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(env_module)
        ApiWorkflowEnvironment = env_module.ApiWorkflowEnvironment
        models_path = os.path.join(project_root, "models.py")
        mspec = importlib.util.spec_from_file_location("models", models_path)
        models = importlib.util.module_from_spec(mspec)
        mspec.loader.exec_module(models)
        _has_env = True
    except Exception:
        _has_env = False

# 4. CREATE APP (only if all deps available)
if _has_openenv and _has_env:
    app = create_app(
        ApiWorkflowEnvironment,
        Union[models.AddCalendarEvent, models.ScheduleMeeting, models.SearchContact],
        Union[models.CalendarObservation, models.ContactObservation],
        env_name="api_workflow_env",
        max_concurrent_envs=4,
    )
else:
    # Fallback: bare FastAPI app so the module is always importable
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

# 5. MAIN ENTRY POINT - must always be present and callable
def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run("app:app", host=host, port=port)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
   
   
