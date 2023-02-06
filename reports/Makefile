FILES= outputs/$(YEAR)/$(MONTH)/*/1_file_info.json

.SECONDARY:

all: $(FILES)

clean:
	rm -rf outputs/*

sync:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data-test/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data/report_gtfs_schedule/

generate_parameters:
	python generate_index_report.py
	python generate_rt_feeds.py

outputs/index_report.json: generate_parameters

outputs/%/1_file_info.json:
	python generate_reports_data.py -v --f $(dir $@)1_file_info.json
