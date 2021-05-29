NOTEBOOKS=$(patsubst %.ipynb,%.html,$(wildcard output/*/report.ipynb))

all: $(NOTEBOOKS)

output/%/report.html: output/%/report.ipynb
	jupyter nbconvert \
		--to html \
		--TagRemovePreprocessor.remove_input_tags="{'hide', 'injected-parameters'}" \
		--TagRemovePreprocessor.remove_single_output_tags="{'hide', 'injected-parameters'}" \
		--no-input \
		--no-prompt \
		$<
