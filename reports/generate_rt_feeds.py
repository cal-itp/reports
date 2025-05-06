"""
Adapted from from https://github.com/cal-itp/data-analyses/blob/8100fcd21a64fa6437ddb36701d77470b7592362/bus_service_increase/deploy_portfolio_yaml.py#L107-L129
"""
import argparse
import json
from datetime import datetime
from functools import cache

import requests
from calitp_data_analysis.sql import query_sql  # type: ignore
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
    # date format - 2025-4-01
    rt_feeds = (
        tbls.mart_gtfs_quality.idx_monthly_reports_site()  # This function returns a siuba lzytbl
        >> filter(_.publish_date == date_start)
        >> filter(_.has_rt == True)  # noqa: E712
        >> select(_.organization_itp_id, _.has_rt)
        >> collect()
    )
    return rt_feeds.values.tolist()


@cache
def _get_organization_name_to_itp_id():
    df = query_sql(
        """
  SELECT
  idx.`organization_itp_id` as itp_id,
    REPLACE(LOWER(idx.`organization_name`), ' ', '-') AS organization_name,
  FROM `mart_gtfs_quality.idx_monthly_reports_site` AS idx
  where publish_date in (select idx.`publish_date` FROM `mart_gtfs_quality.idx_monthly_reports_site` AS idx order by publish_date DESC limit 1)
  """,
        as_df=True,
    )
    return dict(zip(df["organization_name"], df["itp_id"]))


# Scrape the actual speedmap site to get the urls
def get_speedmap_urls():
    org_to_itp_id_dict = _get_organization_name_to_itp_id()
    response = requests.get("https://analysis.calitp.org/rt/README.html")
    html = response.content
    results = {}
    for line in html.decode("utf-8").split("\n"):
        if "reference internal' href='/district" not in line:
            # print(f"WARNING: skipping line because it doesn't contain the expected text: {line}")
            continue
        href = line.split("href='")[-1].split("'")[0]
        if "organization_name_" not in href:
            # print(f"WARNING: skipping url because organization_name not in href: {href}")
            continue
        try:
            # Extract organization_name from the href
            organization_name = href.split("organization_name_")[-1].split("__")[0]
            if not organization_name.isalnum() and "-" not in organization_name:
                print(
                    f"WARNING: skipping url because organization_name is not valid: {organization_name}"
                )
                continue
            if organization_name in org_to_itp_id_dict:
                results[
                    int(org_to_itp_id_dict[organization_name])
                ] = f"https://rt--cal-itp-data-analyses.netlify.app{href}"
            else:
                print(
                    f"WARNING: skipping url because itp_id not in org_dict: {organization_name}, {href}"
                )
        except IndexError:
            print(f"ERROR: Failed to parse organization_name from href: {href}")
            continue
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
