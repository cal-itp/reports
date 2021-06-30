import json
import os
import re
import shutil

from datetime import date
from glob import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape()
)

################################################################################
# site config data

global_data = {
    "SITE_DOMAIN": "https://reports.calitp.org",
    "SITE_PATH": "",
    # "SITE_DOMAIN": "http://localhost:8000",
    # "SITE_PATH": "",
    "PATH_GTFS_SCHEDULE": "gtfs_schedule"
}


################################################################################
# render index

index_template = env.get_template('index.html.jinja')

index_data = {}
with open('data/index_report.json') as file:
    index_data['reports'] = json.load(file)

index_html = index_template.render({**global_data, **index_data})

if not os.path.exists('build'):
    os.mkdir('build')
with open('build/index.html', 'w') as file:
    file.write(index_html)

################################################################################
# render monthly report index pages
month_template = env.get_template('month.html.jinja')
month_html = month_template.render({**global_data, **index_data})

p_month = Path(f'build/{global_data["PATH_GTFS_SCHEDULE"]}/2021/05')
p_month.mkdir(parents=True, exist_ok=True)
(p_month / 'index.html').write_text(month_html)


################################################################################
# render individual report for 2021/07
# TODO make this process dynamic; remove hardcoded dates

report_template = env.get_template('report.html.jinja')

report_data = {
    'date_generated': date.today()
}
for json_file in glob('data/example_data_itp_98/*.json'):
    name = re.sub(r'^\d+_(.+).json$', r'\1', os.path.basename(json_file))
    with open(json_file, 'r') as file:
        report_data[name] = json.load(file)

report_html = report_template.render({**global_data, **report_data})

build_dir = Path('build/2021/07')
build_dir.mkdir(parents=True, exist_ok=True)

for p_image in Path("data/example_data_itp_98").glob("*.png"):
    shutil.copy(str(p_image), build_dir / p_image.name)


with open('build/2021/07/index.html', 'w') as file:
    file.write(report_html)
