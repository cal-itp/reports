clean:
	rm -rf outputs/*

sync:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data-test/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data/report_gtfs_schedule/

generate_parameters:
	poetry run python generate_index_report.py
	poetry run python generate_rt_feeds.py

generate_data:
	poetry run python generate_reports_data.py generate-data
