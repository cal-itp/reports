# Generating reports

```
docker-compose run reports /bin/bash

# inside container

. venv/bin/activate
cd app

# should produce notebooks, html and other assets in e.g. outputs/2021/05/10
# replace -j 8 with the number of notebooks to build in parallel
# the build process is not computationally intensive, but requires waiting on 
# http requests to google bigquery
make generate_parameters
make all -j 8
```

Finally, to push report data to the production bucket, run the following.

```
# NOTE: currently need to replace gtfs-data-test with gtfs-data in Makefile
# to push to production
make sync
```

## Using Postmark to send emails (SAFELY)
We are currently using the postmark API to send the reports via email to their respective clients
1. Access to Postmark (contact for access to Bitwarden)
    There is a Cal-ITP developer shared" collection in Bitwarden that contains keys for the reports sandbox server. An indivudal will not be given access to prod unless it is absolutely necessary. 
2. Access the Postmark Server token- within the Postmark site, navigate to the existing servers 'gtfs reports.calip' is the transactional server used for sending out the emails and 'gtfs reports test' is the testing sandbox server used to test emails before sending to clients. Each server has its own respective Token within the API Token tab. Once you have the server API Token, set the variable in terminal using `export POSTMARK_SANDBOX_SERVER_TOKEN=<"your token here">` if you are one of the chosed few to be given production access use `POSTMARK_PRODUCTION_SERVER_TOKEN=<"your token here">` It is very important to label the tokens seperately if you have access to both (trust me). 
3. Put in the code safeguards:
If you are using the sandbox:
It is a sandbox server meaning that it sends emails to a "blackhole" rather than actual clients. It is worth mentioning that while they are not actually delivered they are still processed by postmark and count towards the monthly sending volume
Double check you are using the sandbox server token, then you can execute the code as expected. 
4. Navigate to the reports subfolder, the script requires 2 arguments to generate the report link base, Report Publish Date (YYYY-MM-DD format) and Report Publish Month (October capitalized string format). The Report publish date is used to generate the url and the report publish month is used to populate the html message to the client.
5. Navigate to the reports subfolder, script requires 2 arguments Report Publish Date (YYYY-MM-DD) and Report Publish Month (Capitalized String)
6. Run script- `python 3_generate_report_emails.py 2021-10-01 October`
7. Verify email successfully sent in postmark account, within the tracking tab.

if you are using production:
For some features of postmark, you will not be able to visualize the email bodies within the sandbox, URL Hypolinks for example. Then it is necessary to VERY CAREFULLY use the production api key:
On line 117, comment out the for loop code and put in a simplified method.
    ' postmark.emails.send(
        From='general-email@jarv.us',
        To='test-personal-email@test.com',
        Subject='test-email',
        HtmlBody='test-body'
    )' 
Once you have triple checked you are only using a single personal email, send an email to yourself. Once you have verified code works in VS Code, carefully add back in the POSTMARK_PRODUCTION_SERVER_TOKEN and thecommented out for-loop
