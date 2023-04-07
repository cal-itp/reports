# reports

GTFS data quality reports for California transit providers

#### Repository structure

This repository is set up in two pieces:

- `reports/` subfolder - generates underlying GTFS data for each report.
- `website/` subfolder - uses `generate.py` and `../templates/` to create the static reports website.

## To Get Started

### Set up Google Cloud credentials

Set up [google cloud authentication credentials](https://cloud.google.com/docs/authentication/getting-started).

Specifically, download the SDK/CLI at the above link, install it, create a new terminal/source a .zshrc and be sure to run both

1. `gcloud init`
2. `gcloud auth application-default login`

Note that with a user account authentication, the environment variable `CALITP_SERVICE_KEY_PATH` should be unset.

### To Run Locally

#### with a Virtual Environment

1. `source .venv/bin/activate` to activate Python virtual environment
2. `pip install -r requirements.txt` to download Python dependencies
3. `npm install` to download npm dependencies

#### with Docker-compose

Note that the folder also contains a `docker-compose.yml`, so it is possible to run the build inside docker by running these commands first.
In this case, docker first needs to be [installed locally](https://docs.docker.com/get-docker/), setting resources as desired (i.e. enable 6 cores if you have an 8 core machine, etc).
Open a terminal and navigate to the root folder of a locally cloned repo and enter:

```shell
docker-compose run --rm --service-ports calitp_reports /bin/bash
```

If google credentials are already configured on the host, the local credential files should already be mounted in the container, but it may only be necessary to run `gcloud auth application-default login` from within the container.

## Executing Report Generation

See [this screencast](https://www.loom.com/share/b45317053ff54b9fbb46b8159947c379) for a full walkthrough of building the reports.

### Generating the Reports Data

The following takes place within the reports subfolder, i.e. (`cd reports`).

When looking for a clean start (i.e. start from scratch) run:

```shell
make clean
```

#### Fetch existing report data
Run the gsutil rsync to update all the locally stored reports.
Note that `gtfs-data-test` can be replaced with `gtfs-data` for testing on production data:

```shell
gsutil -m rsync -r gs://gtfs-data-test/report_gtfs_schedule outputs
```

#### Generate the index file and create the outputs folder structure
Execute `make generate_parameters` to generate the following artifacts.
* `outputs/index_report.json` - a file that lists every agency name and `outputs/YYYY/MM` folder
* `outputs/rt_feed_ids.json` - labels agencies by whether they have an RT feed
* `outputs/speedmap_urls.json` - labels agencies with their RT speedmap URL, if one exists
* Empty `outputs/YYYY/MM/AGENCY_ITP_ID/` folder for each agency

#### Run the data
Execute `poetry run python generate_reports_data.py generate-data --year=2023 --month=02` to populate those output folders for a given month with the following files (per folder).
* 1_feed_info.json
* 2_daily_service_hours.json
* 3_routes_changed.json
* 3_stops_changed.json
* 4_file_check.json
* 5_validation_codes.json

These files are used to generate the static HTML (see below).

All report data for every month can be generated by running: `poetry run python generate_reports_data.py generate-data` without any options. This may be necessary when data or webpage changes necessitates re-generating prior months (for example, adding a new field).

**NOTE** that the `--month` refers to the month of the folders that will be generated, NOT the month in which the reports are published (typically on the first day of the month). For example, `poetry run python generate_reports_data.py generate-data --year=2023 --month=02` will populate `outputs/2023/02/*` folders, whereas the `publish_date` for the data in those folders is `2023-03-01`.

#### Validating the report creation

After generation, the reports can be validated by running `python validate_reports.py`. This examines all of the output folders and ensures that the generated files are present and that they follow the same schema.

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

### Building the website

Once the report data has been generated navigate to the website subfolder (i.e. `cd ../website`), install the npm dependencies if you haven't done so already, and build the website.

```shell
npm install
npm run build
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

#### Viewing the website

To check that everything is rendered appropriately, go into the website/build (i.e. `cd build`) directory:

 ```shell
python -m http.server
```
and open up a web browser, and navigate to:
[localhost:8000](localhost:8000)


### Pushing Data to Google Cloud

#### Pushing to Development

The next step is to update the development bucket in google cloud with the new data.
In the case where data must be overwritten (please use caution!) a `-d` flag can be added to the command
to "mirror" the buckets, i.e. delete destination data that isn't being copied
from the source.
```shell
gsutil -m rsync -r [-d] outputs/ gs://gtfs-data-test/report_gtfs_schedule/
```

Once you can verify that the gtfs-data-test bucket has updated, you can merge your
PR to main. This site can be viewed at `https://development-build--cal-itp-reports.netlify.app/`.

>❗️In the event there are no code changes necessary for a monthly deploy,
> you can produce empty commits with `git commit --allow-empty` and merge those
> into the main branch.

#### Pushing to Production

Assuming that all the data is correct in development, you can sync the test data to production.

```shell
gsutil -m rsync -r gs://gtfs-data-test/report_gtfs_schedule/ gs://gtfs-data/report_gtfs_schedule/
```

### Deploying the site to Netlify
Once you've synced data to either development or production, you may deploy the
appropriate environment to Netlify.
* For development, pushing a commit (or merging a PR) to the `main` branch
* For production, pushing a tag

You may want to monitor GitHub Actions to ensure your deploy succeeded.
