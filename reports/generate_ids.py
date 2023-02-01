from calitp.tables import tbl
import pandas as pd
from siuba import *
import papermill as pm
from pathlib import Path


ids_with_feeds = (
    tbl.mart_gtfs_quality.idx_monthly_reports_site()
    >> collect()
)

# generate an index for the homepage
df_report_index = (
    ids_with_feeds
    >> mutate(
        date_start=_.publish_date.astype("datetime64[ns]"),
        year=_.publish_date.dt.year,
        month=_.publish_date.dt.month,
        dir_path=_.apply(
            lambda d: f"{d.year}/{d.month:02d}/{d.organization_itp_id}", axis=1
        ),
        report_path=_.apply(
            lambda d: f"{d.dir_path}", axis=1
        ),
    )
)

cols_to_keep = ["agency_name", "itp_id", "report_path"]

index_report = (
    df_report_index
    >> rename(itp_id = _.organization_itp_id)
    >> rename(agency_name = _.organization_name)
    >> arrange(_.year, _.month, _.agency_name)
    >> group_by(_.year, _.month)
    >> summarize(reports=lambda _: [_[cols_to_keep].to_dict(orient="records")])
    >> group_by(_.year)
    >> summarize(
        first_month=_.month.min(),
        last_month=_.month.max(),
        months=lambda _: [_[["month", "reports"]].to_dict(orient="records")],
    )
)

index_report.to_json("outputs/index_report.json", orient="records")

all_ids = list(ids_with_feeds.organization_itp_id)
" ".join(map(str,all_ids))

# ## Save each report's parameters

from pathlib import Path
root_dir = Path("outputs")

date_cols = ["publish_date", "date_start", "date_end"]

fixed_dates = (
    df_report_index
    >> mutate(**{name: _[name].astype(str) for name in date_cols})
)

for ii, row in fixed_dates.iterrows():
    p_params = root_dir / row["dir_path"] / "report.json"
    p_params.parent.mkdir(parents=True, exist_ok=True)
    row.to_json(p_params)
