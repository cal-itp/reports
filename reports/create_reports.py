"""Use papermill to generate GTFS Schedule reports from notebooks

Note that ProcessPoolExecutor cannot run in an interactive session, so this
script is called independently. We could normally use ThreadPoolProcessor, but
papermill is not thread safe.
"""

import sys

from pathlib import Path
import papermill as pm
from papermill.exceptions import PapermillExecutionError

from concurrent.futures import ProcessPoolExecutor

MAX_WORKERS = 8

def build_report(itp_id):
    p_dir = Path(f"output/{itp_id}")
    p_dir.mkdir(parents=True, exist_ok=True)

    fname = str(p_dir / "report.ipynb")

    print(f"Knitting to: {fname}")

    return pm.execute_notebook(
        "report.ipynb",
        fname,
        parameters={
            "CALITP_ITP_ID": int(itp_id),
            "CALITP_URL_NUMBER": 0,
            "DEBUG": False,
            "START_DATE": "2021-05-01",
            "END_DATE": "2021-06-01"
        },
    )



if __name__ == "__main__":
    all_ids = sys.argv[1:]
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(build_report, all_ids)
