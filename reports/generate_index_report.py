import argparse
import json
from pathlib import Path

from calitp_data_analysis.tables import tbls
from siuba import _, arrange, collect, group_by, mutate, rename, summarize

parser = argparse.ArgumentParser()
parser.add_argument(
    "--publish_date",
    help="Supply a specific publish date for the report in YYYY-MM-01 format to generate an index for a single month for testing purposes.",
    type=str,
    nargs="?",
    default=False,
)

args = parser.parse_args()
publish_date = args.publish_date

ids_with_feeds = tbls.mart_gtfs_quality.idx_monthly_reports_site() >> collect()
if publish_date:
    ids_with_feeds = ids_with_feeds >> filter(_.publish_date == publish_date)

# generate an index for the homepage
df_report_index = ids_with_feeds >> mutate(
    date_start=_.date_end.astype("datetime64[ns]"),
    year=_.date_start.dt.year,
    month=_.date_start.dt.month,
    dir_path=_.apply(
        lambda d: f"{d.year}/{d.month:02d}/{d.organization_itp_id}", axis=1
    ),
    report_path=_.apply(lambda d: f"{d.dir_path}/index.html", axis=1),
    feeds=_.feeds.apply(json.loads),
)

cols_to_keep = ["agency_name", "itp_id", "report_path", "feeds"]

index_report = (
    df_report_index
    >> rename(itp_id=_.organization_itp_id)
    >> rename(agency_name=_.organization_name)
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

root_dir = Path("outputs")

date_cols = ["publish_date", "date_start", "date_end"]

fixed_dates = df_report_index >> mutate(
    **{name: _[name].astype(str) for name in date_cols}
)

for ii, row in df_report_index.iterrows():
    p_params = root_dir / row["dir_path"]
    p_params.mkdir(parents=True, exist_ok=True)
