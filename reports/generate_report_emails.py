import configparser
import sys

import hubspot
import pandas as pd
from hubspot.marketing.transactional import ApiException, PublicSingleSendRequestEgg

# (TODO: update this section to remove outdated info) This script generates a email body using mjml. The result itself has templated variables
# of form {{SOME_VARIABLE_NAME}}, so we will use jinja to complete these email bodies
from jinja2 import Environment, StrictUndefined
from siuba import _, collect, mutate

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
# Generate the report and dev link base to create report url

# +
SERVER_TOKEN = config["hubspot_server_token"]
hubspot_client = hubspot.Client.create(access_token=SERVER_TOKEN)
PUBLISH_DATE_YEAR = config["year"]
PUBLISH_DATE_MONTH_NAME = config["month_name"]
PUBLISH_DATE_MONTH_INT = config["month"]

REPORT_LINK_BASE = f"https://reports.calitp.org/gtfs_schedule/{PUBLISH_DATE_YEAR}/{PUBLISH_DATE_MONTH_INT}"
# -
# TODO: need to ensure that the test_emails.csv and production email sheet use the
#       same column names
tbl_report_emails = pd.read_csv(config["email_csv_path"])
tbl_report_emails.columns = tbl_report_emails.columns.str.lower()
tbl_report_emails.columns = tbl_report_emails.columns.str.replace(" ", "_")
report_emails = (
    tbl_report_emails
    >> collect()
    >> mutate(
        calitp_itp_id=_.itp_id.astype(int),
        report_url=REPORT_LINK_BASE + "/" + _.itp_id.astype(str) + "/",
    )
)
report_emails

# +
# Double check if we're on development that it is going to the sandbox ----
if config.getboolean("is_development"):
    print("Using development values from config.ini")
else:
    print("Using production values from config.ini")

# Prompt user on whether to continue (if show_prompt specified) ----
if config.getboolean("show_prompt"):
    result = input(
        f"""
You are about to email the following {report_emails["main_email"].count()} addresses: {", ".join(report_emails.main_email)}
To continue, type yes."""
    )
    if result != "yes":
        raise Exception("Need yes to continue")

for index, email in report_emails.iterrows():
    message = {
        "from": config["email_from"],
        "to": email["main_email"],
        "replyTo": [config["email_from"]],
    }
    custom_properties = {
        "month_name": PUBLISH_DATE_MONTH_NAME,
        "url": email["report_url"],
    }
    public_single_send_request_egg = PublicSingleSendRequestEgg(
        email_id=config["email_id"],
        message=message,
        custom_properties=custom_properties,
    )
    try:
        api_response = (
            hubspot_client.marketing.transactional.single_send_api.send_email(
                public_single_send_request_egg=public_single_send_request_egg
            )
        )
        print(api_response)
    except ApiException as e:
        print("Exception when calling single_send_api->send_email: %s\n" % e)
