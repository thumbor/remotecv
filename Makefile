REDIS_CONTAINER := redis-test redis-sentinel-test

setup:
	@pip install -Ue .[dev]
	@echo  "\n\nYou are strongly recommended to run 'pre-commit install'\n"

run:
	@remotecv

test: run-redis unit stop-redis

unit:
	@pytest --cov=remotecv --cov-report term-missing --asyncio-mode=strict -s -r tests/

coverage:
	@coverage report -m --fail-under=52
	@coverage lcov

black:
	@black . --config pyproject.toml

flake:
	@flake8 --config .flake8

pylint:
	@pylint remotecv tests

lint: black flake pylint

ci-test:
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; else $(MAKE) unit; fi

run-redis:
	@docker-compose up -d $(REDIS_CONTAINER)

stop-redis:
	@docker-compose stop $(REDIS_CONTAINER)
