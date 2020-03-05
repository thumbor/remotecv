setup: update-setup
	@poetry install

update-setup:
	@if [ "$(command -v dephell)" != "" ]; then echo 'Error: dephell is not installed. Installing...' && python3 -m pip install "dephell[full]"; fi
	@dephell deps convert

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
