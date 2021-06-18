import json
import os
import re
from datetime import date
from glob import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template("index.html")

template_data = {
    "date_generated": date.today()
}
for json_file in glob('data/*.json'):
    name = re.sub(r'^\d+_(.+).json$', r'\1', os.path.basename(json_file))
    with open(json_file, "r") as file:
        template_data[name] = json.load(file)

# with open("data/1_feed_info.json", "r") as file:
#     feed_info = json.load(file)

output_html = template.render(template_data)

if not os.path.exists("build"):
    os.mkdir("build")
with open("build/index.html", "w") as file:
    file.write(output_html)
