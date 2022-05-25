# Generating reports

## Running from outside the container

```bash
docker-compose run --service-ports calitp_reports make generate_parameters
docker-compose run --service-ports calitp_reports make MONTH=02 all -j 8
```

Subsitute `MONTH` var for desired month.

## Manually inside the container

```
docker-compose run reports /bin/bash

# inside container

. venv/bin/activate
cd app

# Generate parameters.json files.
make generate_parameters

# should produce notebooks, html and other assets in e.g. outputs/2021/05/10
# replace -j 8 with the number of notebooks to build in parallel
# the build process is not computationally intensive, but requires waiting on 
# http requests to google bigquery
make generate_parameters
make MONTH=02 all -j 8
```

## Using Postmark to send emails (SAFELY)
We are currently using the postmark API to send the reports via email to their respective clients
1. Access to Postmark (contact for access to Bitwarden).
    - There is a Cal-ITP developer shared" collection in Bitwarden that contains keys for the reports sandbox server. An individual will not be given access to prod unless it is absolutely necessary. 
2. Update the config file.
    - All code variables are stored in a config file. config-example.ini is an example config file that shows what the script is expecting in terms of inputs. Create your own config.ini using the example config as a template and populate accordingly. Some commonly updated variables would be month_name or email_subject. If the environment is development, you will paste in your sandbox server token in the 'postmark_server_token' spot. Same goes for production. Quotations are not needed for strings. The two different environments use two different data inputs. `test_emails.csv` is a test csv that mimics the production data without any actual client emails. The email_csv_path in production will be the URL from the google doc that will contain client emails. 
3. Generate the template (if needed).
    - We are using the mjml markup language to generate the html body and styling of the template. Both the report email and its compiled output is stored in the /templates/email. If changes to the email contents are required, then the template should be updated. It is worth mentioning that mjml should use lowercase names to match the config file. 
4. Script execution
    - Within the reports subfolder run script with the config section name as an argument. It will be development or production depending on the need. For example:  `python generate_report_emails.py development`
5. Pass prompt checks.
    - Before sending out an email,  the `is_developement` config boolean will be checked to make sure it is going to the sandbox server. If you have the necessary permissions and have in production selected in the config file, a prompt will remind you that you are in production and it will print out your email recipients. Once all checks have been passed safely, the script will send out the emails.
6. Verify emails successfully sent. 
    - In postmark account, within the tracking tab it will display email status and other helpful information like if the email has been opened etc. 