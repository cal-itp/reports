clean:
	rm -rf outputs/*

sync:
	gsutil -m rsync -r -d outputs/ gs://test-calitp-reports-data/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://calitp-reports-data/report_gtfs_schedule/

parameters:
	poetry run python generate_index_report.py
	poetry run python generate_rt_feeds.py

data:
	poetry run python generate_reports_data.py
