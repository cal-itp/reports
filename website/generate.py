import argparse
import calendar
import json
import os
import re
from datetime import datetime
from pathlib import Path

import jinja_markdown  # noqa: F401
import tomli
from jinja2 import Environment, FileSystemLoader, pass_eval_context, select_autoescape
from markupsafe import Markup
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument(
    "-v", help="Use verbose output.", type=bool, nargs="?", const=True, default=False
)
args = parser.parse_args()

env = Environment(
    loader=FileSystemLoader("../templates"),
    autoescape=select_autoescape(),
    extensions=[
        "jinja_markdown.MarkdownExtension",
    ],
)

# Copied from https://jinja.palletsprojects.com/en/3.0.x/api/
# used as filter to convert newlines into <br>


@pass_eval_context
def nl2br(eval_ctx, value):
    br = "<br>\n"

    # if eval_ctx.autoescape:
    #    value = escape(value)
    #    br = Markup(br)

    result = "\n\n".join(
        f"<p>{br.join(p.splitlines())}</p>"
        for p in re.split(r"(?:\r\n|\r(?!\n)|\n){2,}", value)
    )
    return Markup(result)


def month_name(month_number):
    return calendar.month_name[month_number]


def datetime_format(value, format="%H:%M %d-%m-%y"):
    if isinstance(value, int):
        return datetime.utcfromtimestamp(value / 1e3).strftime(format)
    return value.strftime(format)


def string_to_html_id(s):
    # does not guarantee uniqueness
    return re.sub("[^(a-z)(A-Z)(0-9)._-]", "", s.lower().replace(" ", "-"))


env.filters = {
    **env.filters,
    "nl2br": nl2br,
    "month_name": month_name,
    "datetime_format": datetime_format,
    "html_id": string_to_html_id,
}


def friendly_month(x):
    return datetime.strptime(x, "%Y-%m-%d").strftime("%B")


def friendly_month_from_int(x):
    return datetime.utcfromtimestamp(x / 1e3).strftime("%B")


def friendly_month_day(x):
    return datetime.strptime(x, "%Y-%m-%d").strftime("%B %d")


def friendly_month_day_from_int(x):
    return datetime.utcfromtimestamp(x / 1e3).strftime("%B %d")


def friendly_month_year(x):
    return datetime.strptime(x, "%Y-%m-%d").strftime("%B %Y")


def friendly_month_year_from_int(x):
    return datetime.utcfromtimestamp(x / 1e3).strftime("%B %Y")


def friendly_month_day_year_from_int(x):
    return datetime.fromtimestamp(x / 1e3).strftime("%m-%d-%Y")


def friendly_month_day_year_from_string(x):
    return datetime.strptime(x, "%Y%m%d").strftime("%m-%d-%Y")


################################################################################
# site config data


global_data = {
    # "SITE_DOMAIN": "https://reports.calitp.org",
    "SITE_PATH": "",
    "SITE_DOMAIN": "",
    # "SITE_PATH": "",
    "PATH_GTFS_SCHEDULE": "gtfs_schedule",
}

print()

################################################################################
# render index

if args.v:
    print("generating homepage")

index_template = env.get_template("index.html.jinja")

index_data = {}
with open("../reports/outputs/index_report.json") as file:
    index_data["reports"] = json.load(file)

index_html = index_template.render({**global_data, **index_data})

if not os.path.exists("build"):
    os.mkdir("build")
with open("build/index.html", "w") as file:
    file.write(index_html)

################################################################################
# render other pages

# FAQs
if args.v:
    print("generating FAQs")
faqs_template = env.get_template("faqs.html.jinja")
with open("data/faqs.toml", "rb") as file:
    faqs_content = tomli.load(file)
faqs_html = faqs_template.render({**global_data, **faqs_content})

if not os.path.exists("build/faqs"):
    os.makedirs("build/faqs")
with open("build/faqs/index.html", "w") as file:
    file.write(faqs_html)


################################################################################
# render individual reports


def iter_report_entries(index):
    for year in index:
        for month in year["months"]:
            month_path = month["reports"][0]["report_path"][0:7].replace("/", "-")
            for entry in tqdm(
                month["reports"],
                leave=False,
                desc=f"        ↳ reports for {month_path}",
                unit=" pages",
                colour="cyan",
            ):
                if args.v:
                    print(f"Creating report for {entry['report_path']}")
                yield year, month, entry


rt_feed_path = "../reports/outputs/rt_feed_ids.json"
if os.path.isfile(rt_feed_path):
    with open(rt_feed_path, "r") as f:
        rt_feeds = dict(json.loads(f.read()))
else:
    rt_feeds = dict()

speedmap_urls_path = "../reports/outputs/speedmap_urls.json"
if os.path.isfile(speedmap_urls_path):
    with open(speedmap_urls_path, "r") as f:
        speedmap_urls = dict(json.loads(f.read()))
else:
    speedmap_urls = dict()


def fetch_report_data(report_dir):
    report_data = {}
    # report data lives in ../reports/outputs/{year}/{month}/{itp_id}
    itp_id = int(str(report_dir).split("/")[5])
    report_data["has_rt_feed"] = itp_id in rt_feeds
    report_data["speedmap_url"] = speedmap_urls.get(itp_id)
    json_files = Path(report_dir).glob("*.json")
    for json_file in json_files:
        name = re.sub(r"^\d+_(.+).json$", r"\1", json_file.name)
        with open(json_file, "r") as file:
            report_data[name] = json.load(file)
            if name == "feed_info":
                report_data[name] = dict(report_data[name][0])
                report_data[name]["date_month_year"] = friendly_month_year_from_int(
                    report_data[name]["report_start_date"]
                )
                report_data[name]["date_month"] = friendly_month_from_int(
                    report_data[name]["report_start_date"]
                )
                report_data[name]["start_month_day"] = friendly_month_day_from_int(
                    report_data[name]["report_start_date"]
                )
                report_data[name]["end_month_day"] = friendly_month_day_from_int(
                    report_data[name]["report_end_date"]
                )
                # Feed end date is not always provided
                if report_data[name]["earliest_feed_end_date"]:
                    report_data[name][
                        "feed_end_date_m_d_y"
                    ] = friendly_month_day_year_from_int(
                        report_data[name]["earliest_feed_end_date"]
                    )
                else:
                    report_data[name]["feed_end_date_m_d_y"] = "None"

    return report_data


REPORT_OUTPUTS_DIR = Path("../reports/outputs")
REPORT_BUILD_DIR = Path("build/gtfs_schedule")

report_template = env.get_template("report.html.jinja")

all_rt_vendors = set()
all_schedule_vendors = set()

################################################################################
# render all reports

with tqdm(
    total=len(list(iter_report_entries(index_data["reports"]))),
    desc="generating individual reports",
    unit=" pages",
    colour="blue",
) as pbar:
    for year, month, entry in iter_report_entries(index_data["reports"]):
        p_report_path = Path(entry["report_path"])
        p_report_inputs = REPORT_OUTPUTS_DIR / p_report_path.parent
        report_data = fetch_report_data(p_report_inputs)
        report_data["feeds"] = entry["feeds"]

        # track vendors
        rt_vendors = report_data["feed_info"]["rt_vendors"]
        schedule_vendors = report_data["feed_info"]["schedule_vendors"]
        # add info to individual entry
        entry["rt_vendors"] = rt_vendors
        entry["schedule_vendors"] = schedule_vendors
        # add to list of all
        all_rt_vendors.update(rt_vendors)
        all_schedule_vendors.update(schedule_vendors)

        report_html = report_template.render({**global_data, **report_data})
        pbar.update(1)

        p_final = REPORT_BUILD_DIR / p_report_path
        p_final.parent.mkdir(parents=True, exist_ok=True)
        p_final.write_text(report_html)

################################################################################
# render monthly report index pages

if args.v:
    print("generating monthly indexes")

month_template = env.get_template("month.html.jinja")

p_basedir = Path(f"build/{global_data['PATH_GTFS_SCHEDULE']}")
for year in index_data["reports"]:
    for month in year["months"]:
        p_month = p_basedir / f"{year['year']}/{month['month']:02d}"

        date_month_year = friendly_month_year(f"{year['year']}-{month['month']:02d}-01")

        month_html = month_template.render(
            **global_data,
            year=year,
            month=month,
            date_month_year=date_month_year,
            rt_vendors=all_rt_vendors,
            schedule_vendors=all_schedule_vendors,
        )

        p_month.mkdir(parents=True, exist_ok=True)
        (p_month / "index.html").write_text(month_html)
