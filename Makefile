COVERAGE = $(or $(shell which coverage), $(shell which python-coverage), coverage)

setup:
	@pip install -Ue.\[tests\]

test:
	@$(COVERAGE) run --branch `which nosetests` -v --with-yanc -s tests/

coverage:
	@$(COVERAGE) report -m --fail-under=30

focus:
	@$(COVERAGE) run --branch `which nosetests` -vv --with-yanc --logging-level=WARNING --with-focus -i -s tests/
