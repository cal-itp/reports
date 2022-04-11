# reports

GTFS data quality reports for California transit providers

## Repository structure

This repository is set up in two pieces:

- `reports/` subfolder - generates underlying GTFS data for each report.
- root folder - uses `generate.py` and `templates/` to create the static reports website.

## Generating the reports

See [this screencast](https://www.loom.com/share/b45317053ff54b9fbb46b8159947c379) for a full walkthrough of building the reports.

#### Running Locally
Set up [google cloud authentication credentials](https://cloud.google.com/docs/authentication/getting-started).

From the `reports` subfolder..

```shell
pip install -r requirements
```
### Running via Docker-compose
Note that the folder also contains a `docker-compose.yml`, so you could run
the build inside docker by running these commands first.

Save Google Cloud authentication credentials in `$HOME/.config/gcloud/service-account-file.json`

```shell
docker-compose run --service-ports calitp_reports /bin/bash
```

When debugging, a jupyter notebook server within the container can be started via:
```
jupyter notebook --ip 0.0.0.0 --port 8891
```
and connect to it by copying/pasting the connection information in the terminal.
Here, port 8891 is used to avoid the default 8888 port for any prior jupyter servers.

### Executing Report Generation
When looking for a clean start (i.e. start from scratch) run:
```
make clean
```
Next, update the makefile with the desired month. For example, for March 2022, change the line:
```
NOTEBOOKS=$(subst parameters.json,index.html,$(wildcard outputs/2021/09/*/parameters.json))
```
to:
```
NOTEBOOKS=$(subst parameters.json,index.html,$(wildcard outputs/2022/03/*/parameters.json))
```
Then, start the report generation:
```
# should produce notebooks, html and other assets in e.g. outputs/2021/05/10
# replace -j 8 with the number of notebooks to build in parallel
# the build process is not computationally intensive, but requires waiting on 
# http requests to google bigquery
make generate_parameters
make all -j 8
```

### Pushing to google cloud

Finally, to push report data to the production bucket, run the following.

```shell
# for pushing to development
make sync

# for pushing to production
make sync-prod

# or to copy from dev to prod
gsutil -m rsync -r -d gs://gtfs-data-test/report_gtfs_schedule/ gs://gtfs-data/report_gtfs_schedule/
```

## Generating static site

### How it works

- Python script `generate.py` loads JSON from `data` directory and applies it to `index.html` template
- HTML templates written with [Jinja](https://jinja.palletsprojects.com/en/3.0.x/)
- CSS written with [SCSS](https://sass-lang.com/documentation/syntax#scss) and [Tailwind](https://tailwindcss.com/docs) via [PostCSS](https://postcss.org/)
- JS behavior added with [Alpine.js](https://alpinejs.dev)
  - Bundled with [Rollup](https://rollupjs.org/guide/en/)
- Build scripts via [NPM](https://www.npmjs.com/)

### How to use it

### Setup

1. (Recommended) `source .venv/bin/activate` to activate Python virtual environment
2. `pip install -r requirements.txt` to download Python dependencies
3. `npm install` to download npm dependencies

### Fetch report data

1. Run `gsutil -m rsync -r gs://gtfs-data-test/report_gtfs_schedule/ reports/outputs/`. (Replace `gtfs-data-test` with `gtfs-data` for testing on production data)

### Build report

1. `npm run build` to get a slim build or `npm run watch` to monitor the source files for changes and run dev builds automatically
2. Load `build/index.html` in a browser, preferably via an HTTP server. To do this, change to the `build` directory and run `python -m http.server`.

## Preview and Deploy

Github actions automatically build and deploy any changes to the `development` branch.
The built HTML is pushed automatically as `development-build`.
This site can be viewed at <https://development-build--cal-itp-reports.netlify.app/>.

In order to deploy the site, ensure the data was pushed to the production bucket,
and merge any changes into the main branch.
