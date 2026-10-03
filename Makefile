PYTHON ?= python

.PHONY: all check visuals paper package browser
all: check visuals paper package
check:
	$(PYTHON) -m pytest study analysis -q --junitxml=results/tests.xml
	$(PYTHON) -m study.verify_results
visuals:
	$(PYTHON) -m study.analyze
	$(PYTHON) -m analysis.make_all
paper:
	$(PYTHON) -m analysis.report_numbers
	$(PYTHON) -m study.build_paper
package:
	$(PYTHON) -m study.package
browser:
	node analysis/check_dashboard.mjs
