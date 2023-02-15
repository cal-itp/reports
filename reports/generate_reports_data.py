import argparse
import json
import os
import warnings
from datetime import datetime, timedelta
from pathlib import Path

from calitp.tables import tbls
from siuba import _, arrange, collect
from siuba import filter as filtr
from siuba import if_else, mutate, pipe, rename, select, spread

os.environ["CALITP_BQ_MAX_BYTES"] = str(800_000_000_000)

month_arg = datetime.now().strftime("%m")
year_arg = datetime.now().strftime("%Y")
parser = argparse.ArgumentParser()
parser.add_argument(
    "--month",
    help="The month of the year in M notation. Defaults to current month.",
    type=str,
    default=month_arg,
)
parser.add_argument(
    "--year",
    help="The year in YYYY notation. Defaults to current year.",
    type=int,
    default=year_arg,
)
parser.add_argument(
    "--file",
    help="A string path to a 1_feed_info.json file, ie outputs/YYYY/MM/DD/1_feed_info.json",
    type=str,
    default=False,
)
parser.add_argument(
    "-v", help="Use verbose output.", type=bool, nargs="?", const=True, default=False
)

args = parser.parse_args()
month = args.month
year = args.year
file = args.file

# Cached array of all report paths.
index_report_file_path = "outputs/index_report.json"

if not args.v:
    warnings.filterwarnings("ignore")


# Functions
def to_rowspan_table(df, span_col):
    d = df.to_dict(orient="split")
    row_span = df.groupby(span_col)[span_col].transform("count")
    not_first = df[span_col].duplicated()

    row_span[not_first] = 0

    d["rowspan"] = row_span.tolist()
    return d


def get_dates_year_month(year: int, month: int) -> list:
    start_dt = datetime(year, month, 1)
    date_end = (
        (start_dt + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    ).strftime("%Y-%m-%d")
    # Publish date is first day of the next month.
    publish_date = (
        (start_dt.replace(day=1) + timedelta(days=32))
        .replace(day=1)
        .strftime("%Y-%m-%d")
    )
    date_start = start_dt.strftime("%Y-%m-%d")
    return [date_start, date_end, publish_date]


def generate_feed_info(itp_id: int, publish_date):
    feed_info = (
        tbls.mart_gtfs_quality.idx_monthly_reports_site()
        >> filtr(_.publish_date == publish_date)
        >> filtr(_.organization_itp_id == itp_id)
        >> select(
            _.organization_itp_id,
            _.organization_name,
            _.organization_website,
            _.publish_date,
            _.date_start,
            _.date_end,
            _.route_ct,
            _.stop_ct,
            _.no_service_days_ct,
            _.earliest_feed_end_date,
        )
        >> mutate(has_feed_info=True)
        >> rename(feed_publisher_name=_.organization_name)
        >> rename(feed_publisher_url=_.organization_website)
        >> rename(report_start_date=_.date_start)
        >> rename(report_end_date=_.date_end)
        >> rename(has_feed_info=_.true)
        >> rename(n_routes=_.route_ct)
        >> rename(n_stops=_.stop_ct)
        >> collect()
    )
    return feed_info


def generate_daily_service_hours(itp_id: int, date_start, date_end):
    service_hours = (
        tbls.mart_gtfs_quality.fct_daily_reports_site_organization_scheduled_service_summary()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.service_date >= date_start)
        >> filtr(_.service_date <= date_end)
        >> select(
            _.service_date,
            _.n_routes,
            _.organization_itp_id,
            _.n_trips,
            _.ttl_service_hours,
            _.first_departure_sec,
            _.last_arrival_sec,
            _.n_stop_times,
            _.service_day_type,
        )
        >> rename(last_arrival_ts=_.last_arrival_sec)
        >> rename(calitp_itp_id=_.organization_itp_id)
        >> rename(first_departure_ts=_.first_departure_sec)
        >> rename(weekday=_.service_day_type)
        >> collect()
    )
    return service_hours


def generate_file_check(itp_id: int, publish_date):
    importance = ["Visual display", "Navigation", "Fares", "Technical contacts"]

    file_check = (
        tbls.mart_gtfs_quality.fct_monthly_reports_site_organization_file_checks()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> select(_.date_checked, _.reason, _.filename, _.file_present)
        >> collect()
        >> rename(success=_.file_present)
        >> rename(name=_.filename)
        >> rename(category=_.reason)
        >> mutate(
            success=if_else(_.success == True, "✅", ""),  # noqa: E712
            date_checked=_.date_checked.astype(str),
        )
        >> spread(_.date_checked, _.success)
        >> arrange(_.category.apply(importance.index))
        >> pipe(_.fillna(""))
    )
    return file_check


def generate_validation_codes(itp_id, publish_date):
    validation_codes = (
        tbls.mart_gtfs_quality.fct_monthly_reports_site_organization_validation_codes()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> select(_.code, _.human_readable_description, _.severity)
        >> collect()
    )
    return validation_codes.to_dict(orient="split")


def change_id_query(itp_id: int, publish_date):
    change_query = (
        filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> select(_.organization_itp_id, _.change_status, _.n)
        >> rename(status="change_status")
        >> mutate(percent=_.n / _.n.sum())
        >> collect()
    )
    return change_query


def generate_routes_changed(change_query):
    routes_changed = (
        tbls.mart_gtfs_quality.fct_monthly_route_id_changes() >> change_query
    )
    return routes_changed


def generate_stops_changed(change_query):
    routes_changed = (
        tbls.mart_gtfs_quality.fct_monthly_stop_id_changes() >> change_query
    )
    return routes_changed


# Generate data by "outputs/YYYY/MM/ITP_ID/1_feed_info.json"
def generate_data_by_file_path(file_path):
    items = file_path.split("/")
    year, month, itp_id = int(items[1]), items[2], items[3]
    dates = get_dates_year_month(year, int(month))
    date_start, date_end, publish_date = dates[0], dates[1], dates[2]
    dump_report_data(int(itp_id), month, year, publish_date, date_start, date_end)


def get_month_index(file_path):
    index = {}
    with open(file_path) as file:
        index = json.load(file)

    year_index = list(filter(lambda x: (x["year"] == year), index))[0]
    month_index = list(filter(lambda x: (x["month"] == month), year_index["months"]))[0]
    year_index = list(filter(lambda x: (x["year"] == year), index))[0]
    month_index = list(filter(lambda x: (x["month"] == month), year_index["months"]))[0]
    return month_index


def dump_report_data(
    itp_id: int, month: str, year: int, publish_date, date_start, date_end
):
    out_dir = Path(f"outputs/{year}/{month}/{itp_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # The directory structure currently uses strings for months.
    month = int(month)

    # 1_feed_info.json
    if args.v:
        print(f"Generating feed info for {itp_id}")
    feed_info = generate_feed_info(itp_id, publish_date)
    if feed_info.empty:
        if args.v:
            print(f"ERROR: Could not find feed info for {itp_id}")
        json.dump({"feed_info": False}, open(out_dir / "1_feed_info.json", "w"))
    else:
        feed_info.to_json(out_dir / "1_feed_info.json", orient="records")

    # 2_daily_service_hours.json
    if args.v:
        print(f"Generating service hours for {itp_id}")
    service_hours = generate_daily_service_hours(itp_id, date_start, date_end)
    service_hours.to_json(out_dir / "2_daily_service_hours.json", orient="records")

    change_query = change_id_query(itp_id, publish_date)

    # 3_stops_changed.json
    if args.v:
        print(f"Generating stops changed for {itp_id}")
    stops_changed = generate_stops_changed(change_query)
    stops_changed.to_json(out_dir / "3_stops_changed.json", orient="records")

    # 3_routes_changed.json
    if args.v:
        print(f"Generating routes changed for {itp_id}")
    routes_changed = generate_routes_changed(change_query)
    routes_changed.to_json(out_dir / "3_routes_changed.json", orient="records")

    # 4_file_check.json
    if args.v:
        print(f"Generating file check for {itp_id}")
    file_check = generate_file_check(itp_id, publish_date)
    json.dump(
        to_rowspan_table(file_check, "category"),
        open(out_dir / "4_file_check.json", "w"),
    )

    # 5_validation_notices.json
    if args.v:
        print(f"Generating validation codes for {itp_id}")
    validation_codes = generate_validation_codes(itp_id, publish_date)
    json.dump(validation_codes, open(out_dir / "5_validation_codes.json", "w"))


# Generates all data by month
def generate_report_data_by_year_month(
    month, year, publish_date, date_start, end_date, index_report_file_path
):
    month_index = get_month_index(index_report_file_path)
    for report in month_index["reports"]:
        dump_report_data(
            int(month_index["itp_id"]), month, year, publish_date, date_start, end_date
        )


if __name__ == "__main__":
    if file:
        if args.v:
            print(f"Generating data for file: {file}")
        generate_data_by_file_path(file)
    else:
        if args.v:
            print(f"Generating data for month: {month}")
            dates = get_dates_year_month(year, month)
            date_start, date_end, publish_date = dates[0], dates[1], dates[2]
            generate_report_data_by_year_month(
                month, year, publish_date, date_start, date_end
            )
