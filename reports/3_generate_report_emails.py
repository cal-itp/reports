from calitp.tables import tbl
from siuba import *
import sys
from postmarker.core import PostmarkClient
import os
import pandas as pd
import configparser

# read config from ini
config = configparser.ConfigParser()
config.read("config.ini")
print({section: dict(config[section]) for section in config.sections()})

# +
SERVER_TOKEN=os.environ["POSTMARK_SERVER_TOKEN"]

if len(sys.argv) < 2:
    raise Exception (
        "2 arguments required: report publish date YYYY-MM-DD and Month"
    )
else:
    REPORT_PUBLISH_DATE = sys.argv[1:]

#REPORT_PUBLISH_DATE = "2021-07-01"
#REPORT_PUBLISH_MONTH = "October"
REPORT_PUBLISH_DATE = str(sys.argv[1])
REPORT_PUBLISH_MONTH = str(sys.argv[2])
print("Report Publish Date is:",REPORT_PUBLISH_DATE)
print("Report Publish Month is:",REPORT_PUBLISH_MONTH)
split_date = REPORT_PUBLISH_DATE.split("-")    
PUBLISH_DATE_YEAR = split_date[0]
PUBLISH_DATE_MONTH= split_date[1]

REPORT_LINK_BASE = f'https://reports.calitp.org/gtfs_schedule/{PUBLISH_DATE_YEAR}/{PUBLISH_DATE_MONTH}'
DEV_LINK_BASE = f'https://development-build--cal-itp-reports.netlify.app/gtfs_schedule/{PUBLISH_DATE_YEAR}/{PUBLISH_DATE_MONTH}'    


# +
df_crm_emails = pd.read_csv(
    "https://docs.google.com/spreadsheets"
    "/d/1AHFa5SKcEn7im374mPwULFCj7VlFchQr/export?gid=289636985&format=csv",
    skiprows=1,
)

df_crm_emails.columns = df_crm_emails.columns.str.lower()

# +
tbl.gtfs_schedule.feed_info() >> count(missing_email = _.feed_contact_email.isna())

tbl_report_emails = (
    tbl.views.reports_gtfs_schedule_index()
    >> left_join(
        _,
        tbl.gtfs_schedule.feed_info()
        >> select(_.startswith("calitp"), _.feed_contact_email),
        ["calitp_itp_id", "calitp_url_number"]
    )
    # NOTE: reports currently only use url number = 0, so we remove any others --
    >> filter(_.publish_date == REPORT_PUBLISH_DATE,  _.calitp_url_number == 0)
    >> select(_.startswith("calitp"), _.agency_name, _.use_for_report, _.feed_contact_email)
)

report_emails = tbl_report_emails >> collect()
# -

report_crm_emails = (
    report_emails
    >> full_join(
        _,
        df_crm_emails
        >> filter(_.itp_id.notna())
        >> mutate(itp_id=_.itp_id.astype(int)),
        {"calitp_itp_id": "itp_id"},
    )
)

report_crm_emails_inner = (
    report_crm_emails
    >> filter(_.calitp_itp_id.notna(), _.itp_id.notna())
    >> select(-_.itp_id)
    >> mutate(calitp_itp_id=_.calitp_itp_id.astype(int))
)


final_all_emails = (
    report_crm_emails_inner
    >> transmute(_.calitp_itp_id, _.calitp_url_number, email = _["main email"], origin = "CRM")
    >> filter(_.email.notna())
    >> mutate(
        calitp_itp_id = _.calitp_itp_id.astype(int),
        calitp_url_number = _.calitp_url_number.astype(int),
        report_url = REPORT_LINK_BASE + "/" + _.calitp_itp_id.astype(str) + "/",
        dev_url = DEV_LINK_BASE + "/" + _.calitp_itp_id.astype(str) + "/",
    )
)


# +
### send emails using postmarks API

# +
def _html_body(col):
    ##return a single formatted html for a single row of the table
    return f"""<html>
            <body>Hello!<br> Greetings from the Cal-ITP team.<br> As part of our work with the GTFS feeds for agencies across the state, we prepare a monthly report with some basic statistics and validation results for your agencies' feed.<br>
            You can view your report for {REPORT_PUBLISH_MONTH} at {col.report_url}. We are actively looking for opportunities to help transit agencies address issues with their GTFS feeds. If you would like to meet with our team to learn more about how we can help, or have any questions, please email our team at hello@calitp.org. <br>
            <br>Thanks,<br>
            The Cal-ITP Team<br>
            https://reports.calitp.org/
            </body>
        </html>"""

HTML_MESSAGE = final_all_emails.apply(_html_body, axis =1)
EMAIL = final_all_emails.email
email_list = list(zip(EMAIL,HTML_MESSAGE))
#email_dict = dict(zip(final_all_emails.email,HTML_MESSAGE))


# +
postmark = PostmarkClient(server_token=SERVER_TOKEN)

for EMAIL, HTML_MESSAGE in email_list:
    email = postmark.emails.Email(
        From='general+cal-itp@jarv.us',
        To=EMAIL,
        Subject='GTFS Quality Reports from Cal-ITP',
        HtmlBody=HTML_MESSAGE,
        )
    email.send()
  
    
    




    




# +
##final_all_emails.to_csv(f"report_emails_{REPORT_PUBLISH_DATE}.csv")

# +
# import requests

# for link in final_all_emails.dev_url.tolist():
#     r = requests.get(link)
#     r.raise_for_status()
