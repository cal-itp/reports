# Checklist for monthly report generation

## Process should begin on the first of the month and reports emailed out no later than 2 weeks after that

## Verify that development branch is synced with main

- [ ] Verify development is synced with main
- [ ] Switch to development branch

### Creating report data

``` python
pip install -r requirements
make generate_parameters
make all -j 30
```

- [ ] Verify that parameters are generated in subfolders
- [ ] Verify in outputs that reports were generated
- [ ] Verify that data subfolder is present

If needed update previous month's reports. Make sure that the hard-coded months are accurate.

``` python
python run_all_months.py
```

### Generate static site

From within the build subfolder

```python  
npm run build
python -m http.server
```

- [ ] Report month has been added to UI
- [ ] Find example of agency with no validation errors (avalon), with validation notices (santa clara), and with daily metric errors (sacrt)

### Publishing to development website

```python
make sync
```

Github actions automatically build and deploy any changes to the `development` branch. May need to re-run github actions. If on the main branch, need to sync development and main branch.

```python
gsutil -m rsync -r -d gs://gtfs-data-test/report_gtfs_schedule/ gs://gtfs-data/report_gtfs_schedule/
```

The built HTML is pushed automatically as `development-build`.
This site can be viewed at https://development-build--cal-itp-reports.netlify.app/.

### Review

- [ ] Request review of development site from Transit Data Quality Lead (@0-ram)
- [ ] Receive approval from Cal-ITP technical lead (@evansiroky) to deploy website to production

### Deploy Reports

to push report data to the production bucket

```python  
make sync-prod
```

or to copy from the dev to prod.

```python
gsutil -m rsync -r -d gs://gtfs-data-test/report_gtfs_schedule/ gs://gtfs-data/report_gtfs_schedule/
```

In order to deploy the site, ensure the data was pushed to the production bucket,
and merge any changes into the main branch.

If there are no changes between development and production rerun the last github action workflow run on main.

- [ ] Verify github action is using gtfs-data (production) rather than gtfs-data-test (development)
- [ ] Verify in the github action that it is copying production report data
- [ ] Verify that production site has been updated with most up to date month

### Email reports

#### Testing

Obtain test emails from Cal-ITP technical lead (@evansiroky). Verify with Transit Data Quality Lead (@o-ram) and Cal-ITP comms lead that email contents are correct. Update the config file.

- [ ] Verify with Transit Data Quality Lead (@o-ram) and Comms Lead that email content is correct
- [ ] Update config file to have current month
- [ ] Verify with Cal-ITP Technical Lead (@evansiroky) that test email list is correct
- [ ] Verify with Transit Data Quality Lead (@o-ram) that production email list is correct

##### Generate the template (if needed)

script execution in development

```python  
python 3_generate_report_emails.py development
```

- [ ] Send out emails to test email list using sandbox token.
- [ ] Send out emails to test email list production token
- [ ] Verify that the emails pass visual inspection

#### Production

Once emails have passed visual inspection, change config file for production

```python  
python 3_generate_report_emails.py production 
```

pass prompt that asks if production is correct and verify email recipients are production
send out emails

- [ ] Send out emails to production email list using production token.
- [ ] Check that all emails have been sent and none have been hard bounced. Send loop has concluded correctly.

If an email is no longer active, the send loop will continue and the email that produced the error will be printed in the console.

### Verify emails successfully sent

- [ ]  Verify in postmark that email tracking has been selected
- [ ]  Verify in postmark that emails have been sent in the production server correctly and have not bounced etc

#### Verify emails in GH Actions

- [ ] Verify in GH actions that all actions passed.