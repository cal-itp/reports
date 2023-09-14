"""
Adapted from from https://github.com/cal-itp/data-analyses/blob/8100fcd21a64fa6437ddb36701d77470b7592362/bus_service_increase/deploy_portfolio_yaml.py#L107-L129
"""
import argparse
import json
from datetime import datetime

import requests
from calitp_data_analysis.tables import tbls
from siuba import _, collect, filter, select

monthArg = datetime.now().strftime("%m")
yearArg = datetime.now().strftime("%Y")
parser = argparse.ArgumentParser()
parser.add_argument(
    "--month",
    help="The month of the year in M notation. Defaults to current month.",
    type=int,
    default=monthArg,
)
parser.add_argument(
    "--year",
    help="The year in YYYY notation. Defaults to current year.",
    type=int,
    default=yearArg,
)
parser.add_argument("-v", help="Use verbose output.", type=bool, nargs="?", const=True)
args = parser.parse_args()
month = args.month
year = args.year
date_start = f"{year}-{month}-01"


# Get feeds with rt for selected month
def check_if_rt_data_available(date_start):
    rt_feeds = (
        tbls.mart_gtfs_quality.idx_monthly_reports_site()
        >> filter(_.publish_date == date_start)
        >> filter(_.has_rt == True)  # noqa: E712
        >> select(_.organization_itp_id, _.has_rt)
        >> collect()
    )
    return rt_feeds.values.tolist()


# Scrape the actual speedmap site to get the urls
def get_speedmap_urls():
    response = requests.get("https://analysis.calitp.org/rt/README.html")
    html = response.content
    results = {}
    for line in html.decode("utf-8").split("\n"):
        if "reference internal' href='/district" not in line:
            continue
        href = line.split("href='")[-1].split("'")[0]
        if "itp_id_" not in href or "__speedmaps__district_" not in line:
            continue
        itp_id = href.split("itp_id_")[-1].split(".")[0].split("'")[0]
        if not itp_id.isdigit():
            print(f"WARNING: skipping url because itp_id is not a number: {itp_id}")
            continue
        results[int(itp_id)] = f"https://rt--cal-itp-data-analyses.netlify.app{href}"
    return results


if __name__ == "__main__":
    feed = check_if_rt_data_available(date_start)
    with open("./outputs/rt_feed_ids.json", "w") as f:
        f.write(json.dumps(feed))
        if args.v:
            print("rt_feed_ids.json written")

    speedmap_urls = get_speedmap_urls()
    with open("./outputs/speedmap_urls.json", "w") as f:
        f.write(json.dumps(list(speedmap_urls.items())))
        if args.v:
            print("speedmap_urls.json written")
