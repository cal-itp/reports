from calitp.tables import tbl
import pandas as pd
from siuba import *
import papermill as pm
from pathlib import Path

legacy_ids_with_feeds = (
    tbl.views.reports_gtfs_schedule_index()
    >> filter(_.has_feed_info, _.use_for_report)
    >> filter(_.publish_date < '2022-06-01')
    >> collect()
)
# run reports for feeds even without feed info, but only for May '22 onwards
expanded_ids_with_feeds = (
    tbl.views.reports_gtfs_schedule_index()
    >> filter(_.use_for_report)
    >> filter(_.publish_date >= '2022-06-01')
    >> collect()
)

ids_with_feeds = pd.concat([legacy_ids_with_feeds, expanded_ids_with_feeds])

# +
# generate an index for the homepage
from collections import defaultdict

df_report_index = (
    ids_with_feeds
    >> select(
        -_.status, -_.calitp_extracted_at, -_.gtfs_schedule_url
    )
    >> mutate(
        date_start=_.date_start.astype("datetime64[ns]"),
        year=_.date_start.dt.year,
        month=_.date_start.dt.month,
        dir_path=_.apply(
            lambda d: f"{d.year}/{d.month:02d}/{d.calitp_itp_id}", axis=1
        ),
        report_path=_.apply(
            lambda d: f"{d.dir_path}/index.html", axis=1
        ),
    )
    # >> pipe(_.to_json("index_report.json", orient="records"))
)

cols_to_keep = ["agency_name", "itp_id", "report_path"]

index_report = (
    df_report_index
    >> rename(itp_id = _.calitp_itp_id)
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
# report_index = defaultdict(lambda: defaultdict(lambda: {}))
# for (year, month), g in df_report_index.groupby(["year", "month"]):
#     # note that year and month are originally numpy.int64...
#     report_index[int(year)][f"{month:02d}"] = g[cols_to_keep].to_dict(orient="records")
# -

all_ids = list(ids_with_feeds.calitp_itp_id)
" ".join(map(str,all_ids))

# +
# (
#     ids_with_feeds
#     >> mutate(
#         path=_.calitp_itp_id.transform(
#             lambda s: "https://deploy-preview-5--cal-itp-reports.netlify.app/demo/output/%s/report.html"
#             % s
#         )
#     )
# ).to_clipboard()
# -

# ## Save each report's parameters

# +
from pathlib import Path
root_dir = Path("outputs")

date_cols = ["publish_date", "date_start", "date_end"]

fixed_dates = (
    df_report_index
    >> mutate(**{name: _[name].astype(str) for name in date_cols})
)

for ii, row in fixed_dates.iterrows():
    p_params = root_dir / row["dir_path"] / "parameters.json"
    p_params.parent.mkdir(parents=True, exist_ok=True)
    row.index = row.index.str.upper()
    row.to_json(p_params)

    
