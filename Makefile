COVERAGE = $(or $(shell which coverage), $(shell which python-coverage), coverage)

setup:
	@pip install -Ue.\[tests\]

test:
	@$(COVERAGE) run --branch -m nose -v --with-yanc -s tests/

coverage:
	@$(COVERAGE) report -m --fail-under=30

focus:
	@$(COVERAGE) run --branch -m nose -vv --with-yanc --logging-level=WARNING --with-focus -i -s tests/
