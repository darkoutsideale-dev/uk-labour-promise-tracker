from pathlib import Path
import subprocess
import sys
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

COLLECT_SCRIPT = BASE_DIR / "scripts" / "collect_evidence.py"
STATUS_SCRIPT = BASE_DIR / "scripts" / "update_status.py"
TIMELINE_SCRIPT = BASE_DIR / "scripts" / "create_promise_timeline.py"

def run_script(script_path):
    print("=" * 70)
    print(f"Running: {script_path.name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        text=True
    )

    if result.returncode != 0:
        print(f"\nError: {script_path.name} failed.")
        sys.exit(result.returncode)

    print(f"\nFinished: {script_path.name}")


def main():
    print("\nStarting Promise Tracker update...")
    print(f"Update time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project folder: {BASE_DIR}\n")

    if not COLLECT_SCRIPT.exists():
        print(f"Missing file: {COLLECT_SCRIPT}")
        return

    if not STATUS_SCRIPT.exists():
        print(f"Missing file: {STATUS_SCRIPT}")
        return

run_script(COLLECT_SCRIPT)
run_script(STATUS_SCRIPT)

if TIMELINE_SCRIPT.exists():
    run_script(TIMELINE_SCRIPT)
else:
    print("Timeline script not found. Skipping timeline generation.")

    print("\nPromise Tracker update completed successfully!")
    print("\nTo open the dashboard, run:")
    print("python -m streamlit run website/app.py")


if __name__ == "__main__":
    main()