# reports

GTFS data quality reports for California transit providers

## Repository structure

This repository is set up in two pieces:

- `reports/` subfolder - generates underlying GTFS data for each report.
- `website/` subfolder - uses `generate.py` and `../templates/` to create the static reports website.

## Generating the reports

See [this screencast](https://www.loom.com/share/b45317053ff54b9fbb46b8159947c379) for a full walkthrough of building the reports.

#### Generating Reports Data

The following steps are run within the `reports` folder.

- `make generate_parameters` runs the `generate_ids.py` file which generates:
  1. `outputs/index_report.json` - a file that lists every agency name and `outputs/YYYY/MM` folder
  2. `outputs/YYYY/MM` for every agency
- `make MONTH=02 all -j 15` runs the following commands:
  1. `papermill --log-level=ERROR -f outputs/YYYY/MM/AGENCY_NUM/parameters.json report.ipynb outputs/YYYY/MM/AGENCY_NUM/index.ipynb` - creates a copy of the `report.ipynb` file, runs queries in the `report.ipynb` file, and outputs `outputs/YYYY/MM/AGENCY_NUM/data` directories

The files in each `outputs/YYYY/MM/AGENCY_NUM/data` directory are used to generate the static HTML (see below).

#### Building the website

- Python script `website/generate.py` loads JSON from the `reports/outputs/YYYY/MM/ITPID/data` directory and applies it to template files in `/templates`
- HTML templates written with [Jinja](https://jinja.palletsprojects.com/en/3.0.x/)
- CSS written with [SCSS](https://sass-lang.com/documentation/syntax#scss) and [Tailwind](https://tailwindcss.com/docs) via [PostCSS](https://postcss.org/)
- JS behavior added with [Alpine.js](https://alpinejs.dev)
  - Bundled with [Rollup](https://rollupjs.org/guide/en/)
- Build scripts via [NPM](https://www.npmjs.com/)


### Set up google cloud credentials

Set up [google cloud authentication credentials](https://cloud.google.com/docs/authentication/getting-started).

Specifically, download the SDK/CLI at the above link, install it, create a new terminal/source a .zshrc and be sure to run both

1. `gcloud init`
2. `gcloud auth application-default login`

Note that with a user account authentication, the environment variable `CALITP_SERVICE_KEY_PATH` should be unset.

### Running Locally

#### Virtual environment

1. `source .venv/bin/activate` to activate Python virtual environment
2. `pip install -r requirements.txt` to download Python dependencies
3. `npm install` to download npm dependencies

### Running via Docker-compose

Note that the folder also contains a `docker-compose.yml`, so it is possible to run the build inside docker by running these commands first.
In this case, docker first needs to be [installed locally](https://docs.docker.com/get-docker/), setting resources as desired (i.e. enable 6 cores if you have an 8 core machine, etc).
Open a terminal and navigate to the root folder of a locally cloned repo and enter:

```shell
docker-compose run --rm --service-ports calitp_reports /bin/bash
```

If google credentials are already configured on the host, the local credential files should already be mounted in the container, but it may only be necessary to run `gcloud auth application-default login` from within the container.

When debugging, a jupyter lab server within the container can be started via:

```shell
jupyter lab --ip 0.0.0.0 --port 8891
```

and connect to it by copying/pasting the connection information generated from the jupyter lab server running in the container into a web browser URL.
Here, port 8891 is used to avoid the default 8888 port for any prior jupyter servers.

### Executing Report Generation

The following takes place within the reports subfolder, i.e. (`cd reports`).

When looking for a clean start (i.e. start from scratch) run:

```shell
make clean
```

#### Fetching report data
Run the gsutil rsync to update all the locally stored reports.
Note that `gtfs-data-test` can be replaced with `gtfs-data` for testing on production data:

```shell
gsutil -m rsync -r gs://gtfs-data-test/report_gtfs_schedule outputs
```

#### Generating reports
Next, start the report generation:

```shell
make generate_parameters
make MONTH=02 all -j 15
```
Where:
* the number after `MONTH=` is the desired numerical month (`02` in this case)
* the number after `-j` is the number of parallel threads (`15` in this case)

This will create data for one month within the reports/outputs folder.

Note that running too many threads (i.e. parallel queries, such as `30` or more) may not complete successfully if many other BigQuery queries are happening simultaneously: [BigQuery has a limit of 100 concurrent queries](https://cloud.google.com/bigquery/quotas).
If this is the case, try rerunning with fewer threads (i.e. `make all -j 8`).

If this still isn't successful, check each folder to see if both an index.html and 'data' folder exist.
This can be done via:
```shell
find ./outputs/2022/03 -mindepth 1 -maxdepth 1 -type d '!' -exec test -e "{}/data" ';' -print
```
Where `2022/03` is the current month. Folders without a `data` subfolder will return, for example:
```shell 
>./outputs/2022/03/274
```
 This should provide a list of ITPID folders that didn't complete reports generation for that month.
 For each folder, simply rereun the papermill generation for that particular ITPID:
```shell
papermill -f outputs/2022/03/274/parameters.json report.ipynb outputs/2022/03/274/index.ipynb
```

### Build website

Once every single report is generated, navigate to the website subfolder (i.e. `cd ../website`), install the npm dependencies, and build the website.

```shell
npm install 
npm run build
```

This will run the script in generate.py that will render the index.html, monthly report index pages, and the individual reports.
It will also apply the various jinja templates to the reports, JS frameworks, and CSS styles. It is worth mentioning that `npm run build` will currently only execute if you have data from previous months.

Note that the error:
```shell
jinja2.exceptions.UndefinedError: 'feed_info' is undefined
```
Is often due to a lack of generated reports. This can be remedied for prior months by rsyncing the reports from the upstream source (see [Fetching report data](#fetching-report-data)), and ensuring every single ITPID has a corresponding generated report for the current month (see [Generating reports](#generating-reports)).

To check that everything is rendered appropriately, go into the website/build (i.e. `cd build`) directory:

 ```shell
python -m http.server
```
and open up a web browser, and navigate to:
[localhost:8000](localhost:8000)

### Pushing to google cloud - Development

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

### Pushing to google cloud - Production

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
