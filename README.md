# reports

GTFS data quality reports for California transit providers

## Repository structure

This repository is set up in two pieces:

- `reports/` subfolder - generates underlying GTFS data for each report.
- `website/` subfolder - uses `generate.py` and `../templates/` to create the static reports website.

## Generating the reports

See [this screencast](https://www.loom.com/share/b45317053ff54b9fbb46b8159947c379) for a full walkthrough of building the reports.

### How it works

- Python script `generate.py` loads JSON from the reports/outputs/YYYY/MM/ITPID/`data` directory and applies it to `index.html` template
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

Note that the folder also contains a `docker-compose.yml`, so you could run
the build inside docker by running these commands first.

```shell
docker-compose run --rm --service-ports calitp_reports /bin/bash
```

If google credentials are already configured on the host, the local credentials should already be mounted in the container, but it may only be necessary to run `gcloud auth application-default login`. 

When debugging, a jupyter notebook server within the container can be started via:

```shell
jupyter notebook --ip 0.0.0.0 --port 8891
```

and connect to it by copying/pasting the connection information in the terminal.
Here, port 8891 is used to avoid the default 8888 port for any prior jupyter servers.

### Executing Report Generation

From within the reports subfolder, i.e. (`cd reports`)

When looking for a clean start (i.e. start from scratch) run:

```shell
make clean
```

#### Fetching report data
Make the 'outputs' folder within the reports folder, and run the gsutil rsync to update all the locally stored reports:

```shell
mkdir outputs
gsutil -m rsync -r gs://gtfs-data-test/report_gtfs_schedule outputs
```

 (Replace `gtfs-data-test` with `gtfs-data` for testing on production data)

#### Generating reports
Next, update the `Makefile` with the desired month. For example, for March 2022, change the line:

```shell
NOTEBOOKS=$(subst parameters.json,index.html,$(wildcard outputs/2021/09/*/parameters.json))
```

to:

```shell
NOTEBOOKS=$(subst parameters.json,index.html,$(wildcard outputs/2022/03/*/parameters.json))
```

Then, start the report generation:

```shell
make generate_parameters
make all -j 15
```
Where the number after `-j` is the number of parallel threads (`15` in this case). 

This will create data for one month within the reports/outputs folder.

Note that running too many threads (i.e. parallel queries, such as `30` or more) may not complete successfully if many other BigQuery queries are happening simultaneously: [BigQuery has a limit of 100 concurrent queries](https://cloud.google.com/bigquery/quotas). If this is the case, try rerunning with fewer threads (i.e. `make all -j 8`).

If this still isn't successful, check each folder to see if both an index.html and 'data' folder exist. This can be done via:
```shell
find ./outputs/2022/04 -mindepth 1 -maxdepth 1 -type d '!' -exec test -e "{}/data" ';' -print

>./outputs/2022/04/274
```
Where '2022/04' is the current month. This should provide a list of folders that didn't complete reports generation. For each folder, simply rereun the papermill generation for that particular ITPID:
```shell
papermill -f outputs/2022/04/274/parameters.json report.ipynb outputs/2022/04/274/index.ipynb
```

### Build website

Once every single report is generated, navigate to the website subfolder (i.e. `cd ../website`), install the npm dependencies, and build the website.

```shell
npm install 
npm run build
```

This will run the script in generate.py that will render the index.html, monthly report index pages, and the individual reports. It will also apply the various jinja templates to the reports, JS frameworks, and CSS styles. It is worth mentioning that `npm run build` will currently only execute if you have data from previous months.

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

```shell
gsutil -m rsync -r -d outputs/ gs://gtfs-data-test/report_gtfs_schedule/
```

however if you are concerned with deleting information in the bucket run the following command.

```shell
gsutil -m rsync -r outputs/ gs://gtfs-data-test/report_gtfs_schedule/
```

Once you can verify that the gtfs-data-test bucket has updated. You will need to merge any code changes into the `development` branch in github. The github action might have to be re-run if the code was pushed to development before syncing to google cloud.  The build html is pushed automatically as `development-build`.
This site can be viewed at `https://development-build--cal-itp-reports.netlify.app/`.

### Pushing to google cloud - Production

Assuming that all the data is correct in development. The next step is to sync the development bucket with the production bucket.

```shell
gsutil -m rsync -r gs://gtfs-data-test/report_gtfs_schedule/ gs://gtfs-data/report_gtfs_schedule/
```

In order to deploy the site, ensure the data was pushed to the production bucket,
and merge any changes into the main branch.

If there are no changes between development and production rerun the last github action workflow run on main.
The production website should update shortly with the most recent month.

### A note about Netlify

Currently the reports site is deployed via netlify continuous deployments. If the website is not currently reflecting the most recent month even if the data is within the google cloud bucket, there is a chance that the deploy failed within the netlify dashboard. If so: please contact a system admin who will log into the dashboard and rerun the netlify deployment.
