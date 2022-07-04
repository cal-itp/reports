NOTEBOOKS=$(subst parameters.json,index.ipynb,$(wildcard outputs/2022/$(MONTH)/*/parameters.json))

.SECONDARY:

all: $(NOTEBOOKS)

clean:
	rm -rf outputs/*

sync:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data-test/report_gtfs_schedule/

sync-prod:
	gsutil -m rsync -r -d outputs/ gs://gtfs-data/report_gtfs_schedule/

generate_parameters:
	python generate_ids.py

outputs/%/parameters.json: generate_parameters

outputs/%/index.ipynb: report.ipynb outputs/%/parameters.json
	papermill --log-level=ERROR -f $(dir $@)parameters.json $< $@
