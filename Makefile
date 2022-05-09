REDIS_CONTAINER := redis-test redis-sentinel-test

setup:
	@pip install -Ue .[dev]

run:
	@remotecv

test: run-redis unit stop-redis

unit:
	@pytest --cov=remotecv --cov-report term-missing --asyncio-mode=strict -r tests/

flake:
	@flake8 --config flake8

pylint:
	@pylint remotecv tests

ci-test:
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; else $(MAKE) unit; fi

run-redis:
	@docker-compose up -d $(REDIS_CONTAINER)

stop-redis:
	@docker-compose stop $(REDIS_CONTAINER)
