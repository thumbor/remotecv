REDIS_CONTAINER := redis-test redis-sentinel-test

setup:
	@poetry install

run:
	@poetry run remotecv

test: run-redis unit stop-redis

coverage:
	@poetry run coverage report -m --fail-under=52
	@poetry run coverage lcov

unit:
	@poetry run pytest --cov=remotecv --cov-report term-missing --asyncio-mode=strict -r tests/

flake:
	@poetry run flake8 --config .flake8

pylint:
	@poetry run pylint remotecv tests

ci-test:
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; else $(MAKE) unit; fi

run-redis:
	@docker-compose up -d $(REDIS_CONTAINER)

stop-redis:
	@docker-compose stop $(REDIS_CONTAINER)
