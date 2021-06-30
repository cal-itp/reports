from calitp.tables import tbl
from siuba import *
import papermill as pm
from pathlib import Path

ids_with_feeds = (
    tbl.views.reports_gtfs_schedule_index() >> filter(_.use_for_report) >> collect()
)

# +
# generate an index for the homepage
from collections import defaultdict

df_report_index = (
    ids_with_feeds
    >> select(
        -_.status, -_.calitp_extracted_at, -_.calitp_url_number, -_.gtfs_schedule_url
    )
    >> mutate(
        year=2021,
        month=5,
        path=_.apply(
            lambda d: f"{d.year}/{d.month:02d}/{d.calitp_itp_id}.html", axis=1
        ),
    )
    # >> pipe(_.to_json("index_report.json", orient="records"))
)

cols_to_keep = ["agency_name", "itp_id", "path"]

index_report = (
    df_report_index
    >> rename(itp_id = _.calitp_itp_id)
    >> arrange(_.year, _.month)
    >> group_by(_.year, _.month)
    >> summarize(reports=lambda _: [_[cols_to_keep].to_dict(orient="records")])
    >> group_by(_.year)
    >> summarize(
        first_month=_.month.min(),
        last_month=_.month.max(),
        months=lambda _: [_[["month", "reports"]].to_dict(orient="records")],
    )
)

index_report.to_json("index_report.json", orient="records")
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
