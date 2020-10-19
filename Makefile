SHELL := bash

.PHONY: venv run check clean reformat doit

all: doit

venv:
	scripts/create-venv.sh

doit:
	scripts/doit.sh

check:
	scripts/check-code.sh

reformat:
	scripts/format-code.sh

clean:
	rm -f '.doit.db*'
