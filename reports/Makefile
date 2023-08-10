clean:
	rm -rf outputs/*

sync:
	gsutil -m rsync -r -d outputs/ gs://test-calitp-reports-data/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://calitp-reports-data/report_gtfs_schedule/

parameters:
	python generate_index_report.py
	python generate_rt_feeds.py

data:
	python generate_reports_data.py
