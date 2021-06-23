# +
from calitp.tables import tbl
from siuba import *
import papermill as pm
from pathlib import Path

DATE_TODAY="2021-06-01"

# +
# workaround for external tables not showing up automatically
from calitp import get_engine
from siuba.sql import LazyTbl

tbl_gtfs_status = LazyTbl(get_engine(), "gtfs_schedule_history.calitp_status")
# -

tbl_gtfs_status

feeds = (
    tbl.gtfs_schedule_type2.feed_info()
    >> filter(
        _.calitp_extracted_at <= DATE_TODAY,
        _.calitp_deleted_at.fillna("2099-01-01") > DATE_TODAY,
    )
    >> distinct(_.calitp_itp_id, _.calitp_url_number)
    >> collect()
)

tbl_status = tbl_gtfs_status >> filter(_.calitp_extracted_at == DATE_TODAY)

tbl_status

ids_with_feeds = (
    tbl_status
    >> filter(_.url_number==0)
    >> rename(calitp_itp_id=_.itp_id, calitp_url_number=_.url_number)
    >> collect()
    >> inner_join(_, feeds, ["calitp_itp_id", "calitp_url_number"])
    >> arrange(_.calitp_itp_id, _.calitp_url_number)
)

# +
# generate an index for the homepage
from collections import defaultdict

df_report_index = (
    ids_with_feeds
    >> select(-_.status, -_.calitp_extracted_at, -_.calitp_url_number, -_.gtfs_schedule_url)
    >> mutate(year=2021, month=5, report_path=_.apply(lambda d: f"{d.year}/{d.month:02d}/{d.calitp_itp_id}.html", axis=1))
    #>> pipe(_.to_json("index_report.json", orient="records"))
)

cols_to_keep = ["agency_name", "calitp_itp_id", "report_path"]
report_index = defaultdict(lambda: defaultdict(lambda: {}))
for (year, month), g in df_report_index.groupby(["year", "month"]):
    # note that year and month are originally numpy.int64...
    report_index[int(year)][f"{month:02d}"] = g[cols_to_keep].to_dict(orient="records")
    
# -

import json
json.dump(report_index, open("report_index.json", "w"))

# +
from papermill.exceptions import PapermillExecutionError

from concurrent.futures import ThreadPoolExecutor


def build_report(itp_id):
    p_dir = Path(f"output/{itp_id}")
    p_dir.mkdir(parents=True, exist_ok=True)
    
    fname = str(p_dir / "report.ipynb")
    
    print(f"Knitting to: {fname}")

    pm.execute_notebook("report.ipynb", fname, parameters={"CALITP_ITP_ID": itp_id, "CALITP_URL_NUMBER": 0})

all_ids = list(ids_with_feeds.calitp_itp_id)

with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(build_report, all_ids)
