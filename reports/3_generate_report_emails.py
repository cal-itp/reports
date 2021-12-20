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
# read config from ini
parser = configparser.ConfigParser()
parser.read("config.ini")

# TODO: how do people want to choose the config? Michael recommends using sys.argv
#       so you could do e.g. python 3_generate_report_emails.py development
config = parser["development"]

# +
## Generate the report and dev link base to create report url 

# +
# TODO: note this server token from environment. Michael recommends not putting it in the config,
#       so we are not mixing sensitive info with configuration. Could also put it in a .env file that
#       is .gitignored
SERVER_TOKEN=os.environ["POSTMARK_SERVER_TOKEN"]
PUBLISH_DATE_YEAR = config['year']
PUBLISH_DATE_MONTH = config['month']

REPORT_LINK_BASE = f'https://reports.calitp.org/gtfs_schedule/{PUBLISH_DATE_YEAR}/{PUBLISH_DATE_MONTH}'  
# -
# TODO: need to ensure that the test_emails.csv and production email sheet use the
#       same column names
tbl_report_emails = pd.read_csv(config["email_csv_path"], skiprows=1)
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


{**config}


# +
#for each row in report_emails, populate template
def _generate_template(report_url):
    stream = os.popen('npx mjml ../templates/email/report.mjml -s')
    template = stream.read()
    
    # render variables in template which use e.g. {{ month_name }} by passing in config
    completed = jinja_env.from_string(template).render(**config, url=report_url)
    return completed
    
html_messages = report_emails.report_url.apply(_generate_template)
all_emails = report_emails.main_email
all_emails_list = list(zip(all_emails,html_messages))


# +
postmark = PostmarkClient(server_token=SERVER_TOKEN)

# Double check if we're on development that it is going to the sandbox ----
if config["is_development"]:
    server = postmark.server.get()
    assert server.DeliveryType == "Sandbox"

# Prompt user on whether to continue (if show_prompt specified) ----
if config["show_prompt"]:
    result = input(f"""
You are about to email the following addresses: {", ".join(all_emails)}
To continue, type yes.""")
    
    if result != "yes":
        raise Exception("Need yes to continue")
    

for emails, html_messages in all_emails_list:
    email = postmark.emails.Email(
        From=config['email_from'],
        To=emails,
        Subject=config['email_subject'],
        HtmlBody=html_messages,
        )
    email.send()
