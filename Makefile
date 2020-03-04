setup:
	@poetry install

run:
	@poetry run remotecv

unit:
	@poetry run pytest -n `nproc` --cov=remotecv tests/

flake:
	@poetry run flake8 --config flake8

pylint:
	@poetry run pylint remotecv tests

ci-test:
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; else $(MAKE) unit; fi
