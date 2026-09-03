"""Quick refresh script for Project Volusia data (repo-root launcher).

Runs the unified pipeline (``Tools/volusia_data/refresh_v2.py``), which ingests
Census PEP, NOAA NCEI, BLS LAUS, BEA CAINC1, and BLS QCEW data into
``Tools/volusia_data/volusia.db``.

Usage (from the Project-Volusia directory):
    python run_refresh.py

Exit code 0 = all sources OK, 1 = one or more sources failed.
"""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent / "Tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from volusia_data.refresh_v2 import main  # noqa: E402

if __name__ == "__main__":
    results = main()
    failed = [name for name, ok in results.items() if not ok]
    for name, ok in results.items():
        print(f"  {'OK' if ok else 'FAIL'}: {name}")
    print(f"Refresh {'failed' if failed else 'completed successfully'}.")
    sys.exit(1 if failed else 0)
