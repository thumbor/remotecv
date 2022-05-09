setup:
	@pip install -Ue .[dev]

run:
	@remotecv

unit:
	@pytest --cov=remotecv --cov-report term-missing --asyncio-mode=strict -r tests/

flake:
	@flake8 --config flake8

pylint:
	@pylint remotecv tests

ci-test:
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; else $(MAKE) unit; fi
