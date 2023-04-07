clean:
	rm -rf outputs/*

sync:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data-test/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data/report_gtfs_schedule/

generate_parameters:
	python generate_index_report.py
	python generate_rt_feeds.py
