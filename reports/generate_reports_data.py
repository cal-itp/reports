import json
import os
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Optional

import numpy as np
import typer
from calitp_data_analysis.sql import get_engine  # type: ignore
from siuba import _, arrange, collect  # type: ignore
from siuba import filter as filtr  # type: ignore
from siuba import left_join, mutate, pipe, rename, select, spread  # type: ignore
from siuba.sql import LazyTbl  # type: ignore
from tqdm import tqdm

os.environ["CALITP_BQ_MAX_BYTES"] = str(800_000_000_000)

engine = get_engine()

# Cached array of all report paths.
index_report_file_path = "outputs/index_report.json"


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


@cache
def _feed_info():
    return (
        LazyTbl(
            engine,
            "mart_gtfs_quality.idx_monthly_reports_site",
        )
        >> left_join(
            _,
            LazyTbl(
                engine,
                "mart_gtfs_quality.fct_monthly_reports_site_organization_gtfs_vendors",
            ),
            ["organization_itp_id", "date_start", "organization_name"],
        )
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
            _.schedule_vendors,
            _.rt_vendors,
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


def generate_feed_info(itp_id: int, publish_date):
    return (
        _feed_info()
        >> filtr(_.publish_date == publish_date)
        >> filtr(_.organization_itp_id == itp_id)
    )


@cache
def _daily_service_hours():
    return (
        LazyTbl(
            engine,
            "mart_gtfs_quality.fct_daily_reports_site_organization_scheduled_service_summary",
        )
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


def generate_daily_service_hours(itp_id: int, date_start, date_end):
    return (
        _daily_service_hours()
        >> filtr(_.calitp_itp_id == itp_id)
        >> filtr(_.service_date >= date_start)
        >> filtr(_.service_date <= date_end)
    )


@cache
def _guideline_check():
    return (
        LazyTbl(
            engine,
            "mart_gtfs_quality.fct_monthly_reports_site_organization_guideline_checks",
        )
        >> select(
            _.organization_itp_id,
            _.publish_date,
            _.date_checked,
            _.feature,
            _.check,
            _.reports_status,
            _.is_manual,
            _.reports_order,
        )
        >> collect()
    )


def generate_guideline_check(itp_id: int, publish_date, feature):
    guideline_check = (
        _guideline_check()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> filtr(_.feature == feature)
        >> select(
            _.date_checked, _.check, _.reports_status, _.is_manual, _.reports_order
        )
        >> mutate(
            date_checked=_.date_checked.astype(str),
            check=np.where(_.is_manual, _.check + "*", _.check),
        )
        >> spread(_.date_checked, _.reports_status)
        >> arrange(_.reports_order)
        >> pipe(_.fillna(""))
    )

    return guideline_check


@cache
def _validation_codes():
    return (
        LazyTbl(
            engine,
            "mart_gtfs_quality.fct_monthly_reports_site_organization_validation_codes",
        )
        >> select(
            _.organization_itp_id,
            _.publish_date,
            _.code,
            _.human_readable_description,
            _.severity,
        )
        >> collect()
    )


def generate_validation_codes(itp_id, publish_date):
    return (
        _validation_codes()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> select(_.code, _.human_readable_description, _.severity)
    ).to_dict(orient="split")


change_query = select(
    _.organization_itp_id, _.publish_date, _.change_status, _.n
) >> rename(status="change_status")


@cache
def _routes_changed():
    return (
        LazyTbl(engine, "mart_gtfs_quality.fct_monthly_route_id_changes")
        >> change_query
        >> collect()
    )


def generate_routes_changed(itp_id: int, publish_date):
    routes_changed = (
        _routes_changed()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> mutate(percent=_.n / _.n.sum())
    )
    return routes_changed


@cache
def _stops_changed():
    return (
        LazyTbl(engine, "mart_gtfs_quality.fct_monthly_stop_id_changes")
        >> change_query
        >> collect()
    )


def generate_stops_changed(itp_id: int, publish_date):
    routes_changed = (
        _stops_changed()
        >> filtr(_.organization_itp_id == itp_id)
        >> filtr(_.publish_date == publish_date)
        >> mutate(percent=_.n / _.n.sum())
    )
    return routes_changed


def get_month_index(file_path, year, month):
    index = {}
    with open(file_path) as file:
        index = json.load(file)

    year_index = list(filter(lambda x: (x["year"] == year), index))[0]
    month_index = list(filter(lambda x: (x["month"] == month), year_index["months"]))[0]
    year_index = list(filter(lambda x: (x["year"] == year), index))[0]
    month_index = list(filter(lambda x: (x["month"] == month), year_index["months"]))[0]
    return month_index


def dump_report_data(
    itp_id: int,
    month: str,
    year: int,
    publish_date,
    date_start,
    date_end,
    verbose=False,
):
    out_dir = Path(f"outputs/{year}/{month}/{itp_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1_feed_info.json
    if verbose:
        print(f"Generating feed info for {itp_id}")
    feed_info = generate_feed_info(itp_id, publish_date)
    if feed_info.empty:
        if verbose:
            print(f"ERROR: Could not find feed info for {itp_id}")
        with open(out_dir / "1_feed_info.json", "w") as f:
            json.dump({"feed_info": False}, f)
    else:
        feed_info.to_json(out_dir / "1_feed_info.json", orient="records")

    # 2_daily_service_hours.json
    if verbose:
        print(f"Generating service hours for {itp_id}")
    service_hours = generate_daily_service_hours(itp_id, date_start, date_end)
    service_hours.to_json(out_dir / "2_daily_service_hours.json", orient="records")

    # 3_stops_changed.json
    if verbose:
        print(f"Generating stops changed for {itp_id}")
    stops_changed = generate_stops_changed(itp_id, publish_date)
    stops_changed.to_json(out_dir / "3_stops_changed.json", orient="records")

    # 3_routes_changed.json
    if verbose:
        print(f"Generating routes changed for {itp_id}")
    routes_changed = generate_routes_changed(itp_id, publish_date)
    routes_changed.to_json(out_dir / "3_routes_changed.json", orient="records")

    # 4_guideline_checks_schedule.json
    if verbose:
        print(f"Generating schedule guideline checks for {itp_id}")
    guideline_checks_schedule = generate_guideline_check(
        itp_id, publish_date, feature="Compliance (Schedule)"
    )
    # for debugging:
    # print(guideline_check.to_string(index=False))

    with open(out_dir / "4_guideline_checks_schedule.json", "w") as f:
        json.dump(to_rowspan_table(guideline_checks_schedule, "check"), f)

    # 5_validation_notices.json
    if verbose:
        print(f"Generating validation codes for {itp_id}")
    validation_codes = generate_validation_codes(itp_id, publish_date)
    with open(out_dir / "5_validation_codes.json", "w") as f:
        json.dump(validation_codes, f)


# Generates all data by month
# def generate_report_data_by_year_month(
#     year,
#     month,
#     publish_date,
#     date_start,
#     end_date,
#     index_report_file_path,
#     verbose=False,
# ):
#     month_index = get_month_index(index_report_file_path)
#     for report in month_index["reports"]:
#         dump_report_data(
#             int(month_index["itp_id"]),
#             month,
#             year,
#             publish_date,
#             date_start,
#             end_date,
#             verbose=verbose,
#         )


# Generate data by "outputs/YYYY/MM/ITP_ID/1_feed_info.json"
def generate_data_by_file_path(feed_dir, pbar=None, verbose=False):
    if verbose:
        print_func = pbar.write if pbar else print
        print_func(f"Generating data for file: {feed_dir}")
    items = feed_dir.split("/")
    year, month, itp_id = int(items[1]), items[2], items[3]
    dates = get_dates_year_month(year, int(month))
    date_start, date_end, publish_date = dates[0], dates[1], dates[2]
    dump_report_data(
        int(itp_id), month, year, publish_date, date_start, date_end, verbose=verbose
    )


# @app.command()
# def generate_data_by_year_month(year, month, verbose=False):
#     print(f"Generating data for month: {month}")
#     dates = get_dates_year_month(year, month)
#     date_start, date_end, publish_date = dates[0], dates[1], dates[2]
#     generate_report_data_by_year_month(
#         year, month, publish_date, date_start, date_end, verbose=verbose
#     )


def generate_data(
    directory: Path = typer.Option(
        default="outputs",
        exists=True,
        file_okay=False,
    ),
    year: Optional[str] = None,
    month: Optional[str] = None,
    itp_id: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
):
    if month and not year:
        raise ValueError("if providing a month, must also provide a year")

    if itp_id and not (month and year):
        raise ValueError("if providing an itp_id, must also provide a month and year")

    years = (
        [directory / Path(year)]
        if year
        else [p for p in directory.iterdir() if p.is_dir()]
    )

    for year_dir in tqdm(years):
        month_dirs = (
            [year_dir / Path(month)]
            if month
            else [p for p in year_dir.iterdir() if p.is_dir()]
        )

        for month_dir in tqdm(month_dirs, desc=year_dir.stem, leave=False):
            itp_id_dirs = (
                [month_dir / Path(itp_id)]
                if itp_id
                else [p for p in month_dir.iterdir() if p.is_dir()]
            )

            pbar = tqdm(itp_id_dirs, desc=month_dir.stem, leave=False)
            for itp_id_dir in pbar:
                if dry_run:
                    print(f"Would be populating {itp_id_dir}")
                else:
                    generate_data_by_file_path(
                        feed_dir=str(itp_id_dir),
                        pbar=pbar,
                        verbose=verbose,
                    )


if __name__ == "__main__":
    typer.run(generate_data)
