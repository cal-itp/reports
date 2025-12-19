clean:
	rm -rf outputs/*

sync-test:
	gsutil -m rsync -r -d outputs/ gs://calitp-reports-data-staging/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://calitp-reports-data/report_gtfs_schedule/

fetch-prod-data:
	gcloud storage cp gs://calitp-reports-data/report_gtfs_schedule/ outputs/ --recursive --content-encoding=utf-8

parameters:
	poetry run python generate_index_report.py
	poetry run python generate_rt_feeds.py

data:
	poetry run python generate_reports_data.py
