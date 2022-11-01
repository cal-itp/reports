# +
import sys
import os
import pandas as pd
from calitp.tables import tbl
from siuba import *
from postmarker.core import PostmarkClient
import configparser

# This script generates a email body using mjml. The result itself has templated variables
# of form {{SOME_VARIABLE_NAME}}, so we will use jinja to complete these email bodies
from jinja2 import Environment, StrictUndefined
jinja_env = Environment(undefined=StrictUndefined)

# +
if len(sys.argv) > 1:
    config_section_name = sys.argv[1]
    print(f"Using config section: {config_section_name}")
else:
    raise ValueError("This script requires 1 argument, the section of config to use.")
    

# read config from ini
parser = configparser.ConfigParser()
parser.read("config.ini")

# select specific section to config
config = parser[config_section_name]

# +
## Generate the report and dev link base to create report url 

# +
SERVER_TOKEN = config['postmark_server_token']
postmark = PostmarkClient(server_token=SERVER_TOKEN)
PUBLISH_DATE_YEAR = config['year']
PUBLISH_DATE_MONTH = config['month']

REPORT_LINK_BASE = f'https://reports.calitp.org/gtfs_schedule/{PUBLISH_DATE_YEAR}/{PUBLISH_DATE_MONTH}'  
# -
# TODO: need to ensure that the test_emails.csv and production email sheet use the
#       same column names
tbl_report_emails = pd.read_csv(config["email_csv_path"])
tbl_report_emails.columns = tbl_report_emails.columns.str.lower()
tbl_report_emails.columns = tbl_report_emails.columns.str.replace(' ','_')
report_emails = (
    tbl_report_emails
    >> collect()
    >> mutate (
         calitp_itp_id = _.itp_id.astype(int),
         report_url = REPORT_LINK_BASE + "/" + _.itp_id.astype(str) + "/",
       )
     )
report_emails


# +
# generate mjml template
stream = os.popen('npx mjml ../templates/email/report.mjml -s')
mjml_template = stream.read()


#for each row in report_emails, populate template
def _generate_template(report_url):
    # render variables in template which use e.g. {{ month_name }} by passing in config
    completed = jinja_env.from_string(mjml_template).render(**config, url=report_url)
    return completed
    
html_messages = report_emails.report_url.apply(_generate_template)
all_emails = report_emails.main_email
all_emails_list = list(zip(all_emails,html_messages))

print("Using server token (Sandbox is f38...): " + config["postmark_server_token"])
# +
# Double check if we're on development that it is going to the sandbox ----
if config.getboolean("is_development"):
    server = postmark.server.get()
    assert server.DeliveryType == "Sandbox"
    print("In sandbox environment")
else:
    print("In production environment")

# Prompt user on whether to continue (if show_prompt specified) ----
if config.getboolean("show_prompt"):
    result = input(f"""
You are about to email the following {all_emails.count()} addresses: {", ".join(all_emails)}
To continue, type yes.""") 
    if result != "yes":
        raise Exception("Need yes to continue")
    

for emails, html_messages in all_emails_list:
    email = postmark.emails.Email(
        From=config['email_from'],
        To=emails,
        Cc=config['cc_email'],
        Subject=config['email_subject'],
        HtmlBody=html_messages,
        TrackOpens=config['track_opens'],
        TrackLinks=config['track_links']
        )
    print(f"sending to emails: {emails}")
    try:
        email.send()
    except BaseException as err:
        print(f"failure to print to {emails}: {err}")
