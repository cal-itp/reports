# reports

## Why reports?

[reports.calitp.org](https://reports.calitp.org/) exists to provide a snapshot of transit service information and transit data quality information for agencies across California. It also serves to connect agencies and other stakeholders with technical assistance from Cal-ITP and Caltrans.

## When and how to generate reports

We automatically update the reports site on a monthly cycle on the first of the month. This generates content for the previous month.

After the site is updated, we manually send emails using a list provided by the Cal-ITP Customer Success team.

### Generating reports via GitHub Actions

This is the easiest option to generate the reports site. Simply open the [Refresh Data](https://github.com/cal-itp/reports/actions/workflows/refresh-data.yml) Action, and use the "Run workflow" drop-down to generate the development or production Reports site.

### Sending reports emails

This step is not currently included in the GitHub Action. After obtaining an updated email list in the form of a csv file, it can be ran via JupyterHub or another platform.

Navigate to the subdirectory, i.e. (`cd reports`), and:

1. Access to Postmark (ask via Slack).
    - If necessary, ask for credentials in #product-reports-site, #services-team, etc
2. Update the config file and email list.
    - All code variables are stored in a config file. config-example.ini is an example config file that shows what the script is expecting in terms of inputs. Create your own config.ini using the example config as a template and populate accordingly, including development and production `postmark_server_token`.
    - Each month, update `year` (if needed), `month` and `month_name`.
    - `test_emails.csv` is a test csv that mimics the production data without any actual client emails.
    - Obtain an updated email list and place in the subdirectory (but do not commit to GitHub).
    - Start with `test_emails.csv` specified in _both_ development and production.
3. Generate the template (if needed).
    - We are using the mjml markup language to generate the html body and styling of the template. Both the report email and its compiled output is stored in the /templates/email. If changes to the email contents are required, then the template should be updated. It is worth mentioning that mjml should use lowercase names to match the config file.
    - _This step is currently somewhat difficult. If email content changes are necessary, use the existing template as a guide and be certain to do a test run before sending to all recipients._
4. Script execution
    - Within the reports subfolder run script with the config section name as an argument. It will be development or production depending on the need. For example:  `poetry run python generate_report_emails.py development` (you may need to run `poetry install` first).
    - If the script hangs, try installing mjml first by running `npx mjml`.
    - Note that the development option doesn't actually send any emails. We reccomend first running the _production_ option with the _test_ emails in order to confirm the actual email content before sending to the wider list.
    - After sending production emails to test recipients and confirming they look good, _now_ switch the config file production `email_csv_path` to your updated email list. Rerun the production script. It will prompt you to confirm the list of recipents. Once those emails are sent, the process is complete!
6. Verify emails successfully sent.
    - In Postmark account, within the tracking tab it will display email status and other helpful information like if the email has been opened etc.

### Generating reports on another platform

It is possible to generate the reports site outside the GitHub Action. Follow the instructions below, but note that it's not currently possible to generate the site locally on a Caltrans computer. It is possible to generate the reports and, importantly, send the reports emails on JupyterHub.

#### Set up Google Cloud credentials

If running on JupyterHub and you've completed the usual [analyst onboarding](https://docs.calitp.org/data-infra/analytics_onboarding/overview.html), no need to repeat this step. Otherwise:
Set up [google cloud authentication credentials](https://cloud.google.com/docs/authentication/getting-started).

Specifically, download the SDK/CLI at the above link, install it, create a new terminal/source a .zshrc and be sure to run both

1. `gcloud init`
2. `gcloud auth application-default login`

Note that with a user account authentication, the environment variable `CALITP_SERVICE_KEY_PATH` should be unset.

#### Pre-commit

This repository uses pre-commit hooks to format code, including [Black](https://black.readthedocs.io/en/stable/index.html). This ensures baseline consistency in code formatting.

> [!IMPORTANT]
> Before contributing to this project, please install pre-commit locally by running `pip install pre-commit` and `pre-commit install` in the root of the repo.

Once installed, pre-commit checks will run before you can make commits locally. If a pre-commit check fails, it will need to be addressed before you can make your commit. Many formatting issues are fixed automatically within the pre-commit actions, so check the changes made by pre-commit on failure -- they may have automatically addressed the issues that caused the failure, in which case you can simply re-add the files, re-attempt the commit, and the checks will then succeed.

Installing pre-commit locally saves time dealing with formatting issues on pull requests. There is a [GitHub Action](./.github/workflows/lint.yml)
that runs pre-commit on all files, not just changed ones, as part of our continuous integration.

#### Running with make and poetry

The Makefile located in the `reports/` subdirectory includes the necessary commands to generate the reports. [poetry](https://python-poetry.org/) handles the required Python dependencies and environment.

Navigate to the subdirectory, i.e. (`cd reports`), and run:

```shell
poetry install
poetry run make parameters
poetry run make data
```

If a clean start is necessary, first run:

```shell
poetry run make clean
```

### Building the website

Once the report data has been generated navigate to the website subfolder (i.e. `cd ../website`), install the npm dependencies if you haven't done so already, and build the website.

```shell
poetry run npm install
poetry run npm run build
```

These commands perform the following:

- Python script `website/generate.py` loads JSON from the `reports/outputs/YYYY/MM/ITPID/data` directory and applies it to template files in `/templates`
- HTML templates written with [Jinja](https://jinja.palletsprojects.com/en/3.0.x/)
- CSS written with [SCSS](https://sass-lang.com/documentation/syntax#scss) and [Tailwind](https://tailwindcss.com/docs) via [PostCSS](https://postcss.org/)
- JS behavior added with [Alpine.js](https://alpinejs.dev)
  - Bundled with [Rollup](https://rollupjs.org/guide/en/)
- Build scripts via [NPM](https://www.npmjs.com/)

It is worth mentioning that `npm run build` will currently only execute if you have data from previous months. Run ``npm run dev`` for verbose output and to see which month is failing, which can help with troubleshooting.

Note that the error:
```shell
jinja2.exceptions.UndefinedError: 'feed_info' is undefined
```
Is often due to a lack of generated reports. This can be remedied for prior months by rsyncing the reports from the upstream source (see [Fetching report data](#fetching-report-data)), and ensuring every single ITPID has a corresponding generated report for the current month (see [Generating reports](#generating-reports)).

#### Viewing the website (not possible via JupyterHub)

To check that everything is rendered appropriately, go into the website/build (i.e. `cd build`) directory:

 ```shell
python -m http.server
```
and open up a web browser, and navigate to:
[localhost:8000](localhost:8000)

Unfortunately it's not possible to do this if running on JupyterHub.

### Implementation details

#### Repository structure

This repository is set up in two pieces:

- `reports/` subfolder - generates underlying GTFS data for each report.
- `website/` subfolder - uses `generate.py` and `../templates/` to create the static reports website.

#### Local artifacts
Execute `make parameters` to generate the following artifacts.
* `outputs/index_report.json` - a file that lists every agency name and `outputs/YYYY/MM` folder
* `outputs/rt_feed_ids.json` - labels agencies by whether they have an RT feed
* `outputs/speedmap_urls.json` - labels agencies with their RT speedmap URL, if one exists
* Empty `outputs/YYYY/MM/AGENCY_ITP_ID/` folder for each agency

#### GitHub Action Triggers

* For production, pushing a commit (or merging a PR) to the `main` branch
* On the first of every month
* Alternatively, manually start the Refresh Data workflow

### Additional options

#### Fetch existing report data

This is rarely required since by default, the commands above will quickly generate reports data for all months. However, it remains possible to run gsutil rsync to update all the locally stored reports.

```shell
gsutil -m rsync -r gs://calitp-reports-data/report_gtfs_schedule outputs
```


#### Run reports data selectively

Also unnecesssary if using the defualt commands, it is possible to selectively run a single month's reports. Execute `poetry run python generate_reports_data.py --year=2023 --month=02` to populate those output folders for a given month with the following files (per folder).
* 1_feed_info.json
* 2_daily_service_hours.json
* 3_routes_changed.json
* 3_stops_changed.json
* 4_guideline_checks_schedule.json
* 5_validation_codes.json

These files are used to generate the static HTML (see below).

**NOTE** that the `--month` refers to the month of the folders that will be generated, NOT the month in which the reports are published (typically on the first day of the month). For example, `poetry run python generate_reports_data.py --year=2023 --month=02` will populate `outputs/2023/02/*` folders, whereas the `publish_date` for the data in those folders is `2023-03-01`.

#### Validating the report creation

After generation, the reports can be validated by running `poetry run python validate_reports.py`. This examines all of the output folders and ensures that the generated files are present and that they follow the same schema.

Additionally, you can see if there are any missing files by running:

```shell
find ./outputs/2023 -mindepth 3 -maxdepth 3 -type f '!' -exec test -e "1_feed_info.json" ';' -print
```

If there is a missing month, an individual month can be run with the following command:

```shell
python generate_reports_data.py -v --f outputs/YYYY/MM/AGENCY_NUM/1_file_info.json
```

#### Testing

Tests can be run locally from the ``tests`` directory by running ``python test_report_data.py``. These tests are run on commits through a github action.


#### Manually Pushing Data to Google Cloud

Since this is part of the development GitHub Action, it's not necessary to run manually. Info below for reference.

##### Pushing data to Production

```shell
gsutil -m rsync -r [-d] outputs/ gs://calitp-reports-data/report_gtfs_schedule/
```

##### Pushing the website to Production

```shell
cd iac
terraform plan
terraform apply
```

#### running with Docker-compose (deprecated)

Note that the folder also contains a `docker-compose.yml`, so it is possible to run the build inside docker by running these commands first.
In this case, docker first needs to be [installed locally](https://docs.docker.com/get-docker/), setting resources as desired (i.e. enable 6 cores if you have an 8 core machine, etc).
Open a terminal and navigate to the root folder of a locally cloned repo and enter:

```shell
docker-compose run --rm --service-ports calitp_reports /bin/bash
```

If google credentials are already configured on the host, the local credential files should already be mounted in the container, but it may only be necessary to run `gcloud auth application-default login` from within the container.
