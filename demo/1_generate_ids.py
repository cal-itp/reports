# +
from utils import tbl
from siuba import *
import papermill as pm
from pathlib import Path

DATE_TODAY="2021-05-27"
# -

feeds = (
    tbl.gtfs_schedule_type2_feed_info()
    >> filter(
        _.calitp_extracted_at <= DATE_TODAY,
        _.calitp_deleted_at.fillna("2099-01-01") > DATE_TODAY,
    )
    >> distinct(_.calitp_itp_id, _.calitp_url_number)
    >> collect()
)

tbl_status = tbl.views_gtfs_status_latest()

ids_with_feeds = (
    tbl_status
    >> distinct(calitp_itp_id=_.itp_id, calitp_url_number=_.url_number)
    >> collect()
    >> inner_join(_, feeds, ["calitp_itp_id", "calitp_url_number"])
    >> arrange(_.calitp_itp_id, _.calitp_url_number)
)

ids_with_feeds >> count()

# +
from papermill.exceptions import PapermillExecutionError

for k, (itp_id, url_num) in list(ids_with_feeds.iterrows()):
    p_dir = Path(f"output/{itp_id}_{url_num}")
    p_dir.mkdir(parents=True, exist_ok=True)
    
    fname = str(p_dir / "report.ipynb")
    
    print(f"Knitting to: {fname}")

    pm.execute_notebook("report.ipynb", fname, parameters={"CALITP_ITP_ID": itp_id, "CALITP_URL_NUMBER": url_num})

