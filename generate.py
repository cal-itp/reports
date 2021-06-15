import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template("index.html")
output_html = template.render(foo="bar", baz="qux")

if not os.path.exists("build"):
    os.mkdir("build")
with open("build/index.html", "w") as file:
    file.write(output_html)
