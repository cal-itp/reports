import os
os.environ["CALITP_BQ_MAX_BYTES"] = str(800_000_000_000)
import json
import warnings
from calitp.tables import tbl
from datetime import date, datetime, timedelta
import pandas as pd
from siuba import filter as filtr, _, collect, pipe, select, rename, mutate, right_join, spread, arrange, if_else
import argparse
from pathlib import Path
import calendar

# Default to previous month.
prev = date.today().replace(day=1) - timedelta(days=1)
monthArg = prev.month
yearArg = datetime.now().strftime('%Y')
parser = argparse.ArgumentParser()
parser.add_argument("--month", help="The month of the year in M notation. Defaults to current month.", type=int, default=monthArg)
parser.add_argument("--year", help="The year in YYYY notation. Defaults to current year.", type=int, default=yearArg)
parser.add_argument("-v", help="Use verbose output.", type=bool, nargs="?", const=True)

args = parser.parse_args()
month = args.month
year = args.year
last_day_month = calendar._monthlen(year, month)
date_start = f"{year}-{month}-01"
date_end = f"{year}-{month}-{last_day_month}"

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

def generate_service_days(service_days):
  n_days_no_service = {"n": service_days}
  return n_days_no_service

def generate_daily_service_hours(itp_id, date_start, date_end):
  service_hours = (
    tbl.mart_gtfs_quality.fct_daily_reports_site_organization_scheduled_service_summary()
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
    >> rename(last_arrival_ts = _.last_arrival_sec)
    >> rename(calitp_itp_id = _.organization_itp_id)
    >> rename(first_departure_ts = _.first_departure_sec)
    >> rename(weekday = _.service_day_type)
    >> collect()
  )
  return service_hours
  
def get_param_data(itp_id, month, year):
  param_data_path = f"../reports/outputs/{year}/{month}/{itp_id}/parameters.json"
  out_dir = Path(f"outputs/{year}/{month}/{itp_id}/data")
  out_dir.mkdir(parents=True, exist_ok=True)

  with open(param_data_path) as file:
    param_data = json.load(file)
  return param_data

def generate_file_check(itp_id, date_start):

  importance = ["Visual display", "Navigation", "Fares", "Technical contacts"]

  fc =(
    tbl.mart_gtfs_quality.fct_monthly_reports_site_organization_file_checks()
    >> filtr(_.organization_itp_id == itp_id)
    >> filtr(_.publish_date == date_start)
    >> select(_.date_checked, _.reason, _.filename, _.file_present)
    >> collect()
    >> rename(success = _.file_present)
    >> rename(name = _.filename)
    >> rename(category = _.reason)
    >> mutate(
      success = if_else(_.success == True, "✅", ""),
      date_checked = _.date_checked.astype(str),
    )
    >> spread(_.date_checked, _.success)
    >> arrange(_.category.apply(importance.index))
    >> pipe(_.fillna(""))
  )
  return fc

def generate_validation_severity(itp_id, date_start):
  validation_severity = (
    tbl.mart_gtfs_quality.fct_monthly_reports_site_organization_validation_codes()
    >> filtr(_.organization_itp_id == itp_id)
    >> filtr(_.publish_date == date_start)
    >> select(_.code, _.severity)
    >> collect()
  )
  return validation_severity.to_dict(orient="split")

def generate_report_data_by_month(month, year, date_start, end_date):
  index = {}
  with open('../reports/outputs/index_report.json') as file:
    index = json.load(file)
 
  year_index = list(filter(lambda x: (x['year'] == year), index))[0]
  month_index = list(filter(lambda x: (x['month'] == month), year_index['months']))[0]
  year_index = list(filter(lambda x: (x['year'] == year), index))[0]
  month_index = list(filter(lambda x: (x['month'] == month), year_index['months']))[0]
  
  for report in month_index['reports']:
    # Use cached data.
    param_data = get_param_data(report['itp_id'], month, year)
    out_dir = Path(f"outputs/{year}/{month}/{report['itp_id']}/data")

    # 1_feed_info.json

    # 2_n_days_no_service.json
    if args.v:
      print(f"Generating service days for {report['itp_id']}")
    service_days = int(param_data['no_service_days_ct']) if param_data['no_service_days_ct'] is not None else None
    n_days_no_service = generate_service_days(service_days)
    json.dump(n_days_no_service, open(out_dir / "2_n_days_no_service.json", "w"))  

    # 2_daily_service_hours.json
    if args.v:
      print(f"Generating service hours for {report['itp_id']}")
    service_hours = generate_daily_service_hours(report['itp_id'], date_start, date_end)
    service_hours.to_json(out_dir / "2_daily_service_hours.json", orient="records")

    # 3_stops_changed.json

    # 3_routes_changed.json

    # 4_file_check.json
    if args.v:
      print(f"Generating file check for {report['itp_id']}") 
    file_check = generate_file_check(report['itp_id'], date_start) 
    json.dump(to_rowspan_table(file_check, "category"), open(out_dir / "4_file_check.json", "w"))

    # 4_validation_severity.json
    validation_severity = generate_validation_severity(report['itp_id', date_start])
    json.dump(validation_severity, open(out_dir / "4_validation_severity.json", "w"))


    if args.v:
      print(f"Generating validation notices for {report['itp_id']}")  
