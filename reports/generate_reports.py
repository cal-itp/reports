import os
os.environ["CALITP_BQ_MAX_BYTES"] = str(800_000_000_000)
import json
import warnings
from calitp.tables import tbl
from datetime import date, datetime, timedelta
from siuba import filter as filtr, _, collect, pipe, select, rename, mutate
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

index = {}
with open('../reports/outputs/index_report.json') as file:
    index = json.load(file)

year_index = list(filter(lambda x: (x['year'] == year), index))[0]
month_index = list(filter(lambda x: (x['month'] == month), year_index['months']))[0]

# Functions
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
    >> collect()
  )
  return service_hours
  

for report in month_index['reports']:
  # Use cached data.
  report_data_path = f"../reports/outputs/{report['report_path']}/report.json"
  out_dir = Path(f"outputs/{report['report_path']}/data")
  out_dir.mkdir(parents=True, exist_ok=True)

  with open(report_data_path) as file:
    report_data = json.load(file)

  # 1_feed_info.json

  # 2_n_days_no_service.json
  if args.v:
    print(f"Generating service days for {report['itp_id']}")
  service_days = int(report_data['no_service_days_ct']) if report_data['no_service_days_ct'] is not None else None
  n_days_no_service = generate_service_days(service_days)
  json.dump(n_days_no_service, open(out_dir / "2_n_days_no_service.json", "w"))  

  # 2_daily_service_hours.json
  # todo: missing "weekday", "calitp_url_number"
  if args.v:
    print(f"Generating service hours for {report['itp_id']}")
  service_hours = generate_daily_service_hours(report['itp_id'], date_start, date_end)
  service_hours.to_json(out_dir / "2_daily_service_hours.json", orient="records")

  # 3_stops_changed.json

  # 3_routes_changed.json

  # 4_file_check.json
  file_check =(
    tbl.mart_gtfs_quality.fct_monthly_reports_site_organization_file_checks()
    >> filtr(_.organization_itp_id == report['itp_id'])
    >> collect()
  )
  if args.v:
    print(f"Generating file check for {report['itp_id']}")  
  # 4_validation_severity.json

  # 5_validation_notices.json
  validation_notices = (
    tbl.fct_monthly_reports_site_organization_validation_codes()
    >> filtr(_.organization_itp_id == report['itp_id'])
    >> collect()
  )
  if args.v:
    print(f"Generating validation notices for {report['itp_id']}")  
