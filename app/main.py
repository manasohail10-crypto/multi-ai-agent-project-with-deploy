import subprocess
import sys
import time

from app.common.logger import get_logger

logger = get_logger(__name__)


def run_backend() -> subprocess.Popen:
    logger.info("Starting backend on port 9999")
    return subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "app.backend.api:app",
            "--host", "127.0.0.1", "--port", "9999",
        ]
    )


def run_frontend() -> subprocess.Popen:
    logger.info("Starting frontend on port 8501")
    return subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app/frontend/ui.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ]
    )


if __name__ == "__main__":
    backend = run_backend()
    time.sleep(3)  # give the backend a moment to start
    frontend = run_frontend()
    try:
        frontend.wait()
    except KeyboardInterrupt:
        logger.info("Stopping the app")
    finally:
        frontend.terminate()
        backend.terminate()