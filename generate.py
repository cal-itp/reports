import json
import os
import re
from datetime import date
from glob import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape()
)

################################################################################
# site config data

global_data = {
    "SITE_PATH": "reports"
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
# render individual report for 2021/07
# TODO make this process dynamic; remove hardcoded dates

report_template = env.get_template('report.html.jinja')

report_data = {
    'date_generated': date.today()
}
for json_file in glob('data/2021/07/*.json'):
    name = re.sub(r'^\d+_(.+).json$', r'\1', os.path.basename(json_file))
    with open(json_file, 'r') as file:
        report_data[name] = json.load(file)

report_html = report_template.render({**global_data, **report_data})

if not os.path.exists('build/2021/07'):
    os.makedirs('build/2021/07')
with open('build/2021/07/index.html', 'w') as file:
    file.write(report_html)
