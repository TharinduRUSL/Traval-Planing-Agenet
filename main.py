"""Member A: start with python main.py or streamlit run main.py."""
import subprocess
import sys
from pathlib import Path
from streamlit.runtime.scriptrunner import get_script_run_ctx


def main():
    if get_script_run_ctx(suppress_warning=True) is not None:
        from frontend.app import app
        app()
        return 0
    root = Path(__file__).resolve().parent
    print("Starting TravelStudio. Follow the local URL printed below.", flush=True)
    command = [sys.executable, "-m", "streamlit", "run", str(root / "main.py"),
               "--server.address=localhost", "--server.port=8501", *sys.argv[1:]]
    process = subprocess.Popen(command, cwd=root)
    try:
        return process.wait()
    except KeyboardInterrupt:
        # Ctrl+C is a normal shutdown, not an application error.
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        print("\nTravelStudio stopped.")
        return 0


if __name__ == "__main__":
    code = main()
    if code:
        raise SystemExit(code)
