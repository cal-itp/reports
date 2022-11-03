import json
import os
import re
import shutil
import calendar

from datetime import date, datetime
from glob import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape, pass_eval_context
from markupsafe import Markup, escape
from pathlib import Path

env = Environment(
    loader=FileSystemLoader('../templates'),
    autoescape=select_autoescape()
)

# env.add_extension('jinja2.ext.debug')

# Copied from https://jinja.palletsprojects.com/en/3.0.x/api/
# used as filter to convert newlines into <br>
@pass_eval_context
def nl2br(eval_ctx, value):
    br = "<br>\n"

    #if eval_ctx.autoescape:
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
        return datetime.fromtimestamp(value / 1e3).strftime(format)
    return value.strftime(format)

env.filters = {
    **env.filters,
    "nl2br": nl2br,
    "month_name": month_name,
    "datetime_format": datetime_format,
}

def friendly_month(x):
    return datetime.strptime(x, "%Y-%m-%d").strftime("%B")

def friendly_month_day(x):
    return datetime.strptime(x, "%Y-%m-%d").strftime("%B %d")

def friendly_month_year(x):
    return datetime.strptime(x, "%Y-%m-%d").strftime("%B %Y")

def friendly_month_day_year_from_string(x):
    return datetime.strptime(x,'%Y%m%d').strftime('%m-%d-%Y')

################################################################################
# site config data

global_data = {
    # "SITE_DOMAIN": "https://reports.calitp.org",
    "SITE_PATH": "",
    "SITE_DOMAIN": "",
    # "SITE_PATH": "",
    "PATH_GTFS_SCHEDULE": "gtfs_schedule"
}


################################################################################
# render index

index_template = env.get_template('index.html.jinja')

index_data = {}
with open('../reports/outputs/index_report.json') as file:
    index_data['reports'] = json.load(file)

index_html = index_template.render({**global_data, **index_data})

if not os.path.exists('build'):
    os.mkdir('build')
with open('build/index.html', 'w') as file:
    file.write(index_html)

################################################################################
# render monthly report index pages

month_template = env.get_template('month.html.jinja')

p_basedir = Path(f"build/{global_data['PATH_GTFS_SCHEDULE']}")
for year in index_data["reports"]:
    for month in year["months"]:
        p_month = (
                p_basedir / f"{year['year']}/{month['month']:02d}"
        )

        DATE_MONTH_YEAR = friendly_month_year(f"{year['year']}-{month['month']:02d}-01")

        month_html = month_template.render(**global_data, year=year, month=month, DATE_MONTH_YEAR=DATE_MONTH_YEAR)

        p_month.mkdir(parents=True, exist_ok=True)
        (p_month / 'index.html').write_text(month_html)


################################################################################
# render individual reports

def iter_report_entries(index):
    for year in index:
        for month in year["months"]:
            for entry in month["reports"]:
                yield year, month, entry

def fetch_report_data(report_dir):
    report_data = {}

    # report data lives in {year}/{month}/{itp_id}/data
    json_files = Path(report_dir).glob("*.json")
    for json_file in json_files:
        name = re.sub(r'^\d+_(.+).json$', r'\1', json_file.name)
        with open(json_file, 'r') as file:
            report_data[name] = json.load(file)
            if name == 'feed_info' and report_data[name]['feed_end_date'] is not None:
                report_data[name]['feed_end_date'] = friendly_month_day_year_from_string(report_data[name]['feed_end_date'])

    # parameters file lives in {year}/{month}/{itp_id}
    parameters = json.load(open(Path(report_dir).parent / "parameters.json"))
    parameters["DATE_MONTH_YEAR"] = friendly_month_year(parameters["DATE_START"])
    parameters["DATE_MONTH"] = friendly_month(parameters["DATE_START"])
    parameters["START_MONTH_DAY"] = friendly_month_day(parameters["DATE_START"])
    parameters["END_MONTH_DAY"] = friendly_month_day(parameters["DATE_END"])
    report_data["parameters"] = parameters


    return report_data

REPORT_OUTPUTS_DIR = Path("../reports/outputs")
REPORT_BUILD_DIR = Path('build/gtfs_schedule')

report_template = env.get_template('report.html.jinja')

for year, month, entry in iter_report_entries(index_data["reports"]):
    p_report_path = Path(entry["report_path"])
    p_report_inputs = REPORT_OUTPUTS_DIR / p_report_path.parent / "data"

    report_data = fetch_report_data(p_report_inputs)
    report_html = report_template.render({**global_data, **report_data})


    p_final = REPORT_BUILD_DIR / p_report_path
    p_final.parent.mkdir(parents=True, exist_ok=True)
    p_final.write_text(report_html)


    for image in p_report_inputs.glob("*.png"):
        shutil.copy(str(image), p_final.parent / image.name)

################################################################################
# render all reports

