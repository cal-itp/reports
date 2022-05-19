# $(wildcard outputs/2021/05/*/parameters.json)
NOTEBOOKS=$(subst parameters.json,index.html,$(wildcard outputs/2021/09/*/parameters.json))


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
	papermill -f $(dir $@)parameters.json $< $@


outputs/%/index.html: outputs/%/index.ipynb
	jupyter nbconvert \
		--to html \
		--TagRemovePreprocessor.remove_input_tags="{'hide', 'injected-parameters'}" \
		--TagRemovePreprocessor.remove_single_output_tags="{'hide', 'injected-parameters'}" \
		--no-input \
		--no-prompt \
		$<
